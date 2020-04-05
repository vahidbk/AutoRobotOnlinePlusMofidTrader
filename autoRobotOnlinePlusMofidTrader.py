#python3 -c 'import datetime;import os;print(datetime.datetime.now());os.system("ping -c 10 google.com")'

import requests
import requests
from bs4 import BeautifulSoup
import requests.packages.urllib3
import jsons
import time

import atexit

import threading
import datetime
import time

from tinydb import TinyDB, Query
from tinydb import where

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import sys
import logging

logFile='/home/me/Desktop/Code/logger.log'
refreshUrl='https://onlineplus.mofidonline.com/Home/Default/page-1'
refreshMinutes=5

chromeWebDriverPath = '/usr/lib/chromium-browser/chromedriver'

baseFolder="/home/me/Desktop/Code/temp/"    
cookieFilename='MofidOnlineCookieFile'
cookieFile = baseFolder+cookieFilename+'.json'
chromeProfilePath=baseFolder+'ChromeProfile'
orderFile = baseFolder+'orderList.json'

showUI = True

class RealTimer:
    def setOffset(self, hourOffset, minuteOffset, secondOffset, microSecondOffset):
        self.hourOffset = hourOffset
        self.minuteOffset = minuteOffset
        self.secondOffset = secondOffset
        self.microSecondOffset = microSecondOffset

    sortedList=[]

    def start(self):
        def sortSortedListBySecondTarget(sortedList):
            return sorted(sortedList) 

        def RealTimeTimerTriggerWorker():
            for triggerData in self.sortedList:
                secondsTarget=triggerData[0]
                doOperation=triggerData[1]
                params=triggerData[2]
                comment=triggerData[3]
                while(True):
                    timeNow = datetime.datetime.now()
                    seconds=timeNow.second+60*(timeNow.minute+60*timeNow.hour)+(0.000001*timeNow.microsecond)
                    if (seconds>=secondsTarget):
                        break
                    if (secondsTarget-seconds>60):
                        time.sleep(1)
                #     processThread = threading.Thread(target=doOperation, args=[params])
                #     processThread.start()
                doOperation(params)

        self.sortedList = sortSortedListBySecondTarget(self.sortedList)
        threading.Thread(target=RealTimeTimerTriggerWorker).start()

    def add(self, doOperation, params, comment\
        , hourTarget, minuteTarget, secondTarget, microSecondTarget):
        hourTarget-=self.hourOffset
        minuteTarget-=self.minuteOffset
        secondTarget-=self.secondOffset
        microSecondTarget-=self.microSecondOffset

        secondsTarget=secondTarget+60*(minuteTarget+60*hourTarget)+microSecondTarget
        self.sortedList.append([secondsTarget, doOperation, params, comment])
        logger.info("triggerAt: "+str(secondsTarget) +" Or:"+ str(hourTarget)+":"+ str(minuteTarget)+":"+ str(secondTarget)+","+ str(microSecondTarget)+" Do:"+str(params))

def loadChromeAndWaitToLoad():
    def doOperationAt_Time(doOperation, params, comment\
        , hourTarget, minuteTarget, secondTarget, microSecondTarget\
        , hourOffset, minuteOffset, secondOffset, microSecondOffset):
        
        hourTarget-=hourOffset
        minuteTarget-=minuteOffset
        secondTarget-=secondOffset
        microSecondTarget-=microSecondOffset

        def RealTimeTimerTriggerWorker():
            timeNow = datetime.datetime.now()
            secondsTarget=secondTarget+60*(minuteTarget+60*hourTarget)+microSecondTarget
            while(True):
                timeNow = datetime.datetime.now()
                seconds=timeNow.second+60*(timeNow.minute+60*timeNow.hour)+(0.000001*timeNow.microsecond)
                if (seconds>=secondsTarget):
                    break
                time.sleep(1)
            timeNow = datetime.datetime.now()
            logger.info(timeNow)
            if (doOperation):
                if (params!=None):
                    doOperation(params)
                else:
                    doOperation() 
            
        SecondTimeTimerThread = threading.Thread(target=RealTimeTimerTriggerWorker)
        SecondTimeTimerThread.start()

    def checkIsLogin():
        #<a class="signout " href="/Account/Logout">
        inputStr="//a[@class='signout ' and @href='/Account/Logout']"
        signOutElems = driver.find_elements_by_xpath(inputStr) 
        if (signOutElems):
            return True
        return False
    
    def onClose():
        logger.info('Exit') 
        if (driver):
            driver.close()
        
    options = webdriver.ChromeOptions()
    if not (showUI):
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
    options.add_argument("--log-level=3");
    options.add_argument("user-data-dir="+chromeProfilePath) #Path to your chrome profile
    driver = webdriver.Chrome(executable_path=chromeWebDriverPath, options=options)
    atexit.register(onClose)
    driver.get(refreshUrl)
    while(True):
        if (checkIsLogin()):break
        time.sleep(1)
    
    def autoRefreshChrome():
        def saveCookie2File():
            cookies=driver.get_cookies()
            logger.info('cookies:'+str(cookies))
            try:
                db = TinyDB(cookieFile)
                db.purge_tables()
                db.insert_multiple(cookies)
                db.close()
            except Exception as err:
                logger.error(f'Error in save cookie File: {err}') 
        def refresh():
            driver.refresh()
            logger.info(str(datetime.datetime.now())+" Refreshed..")
            
        if not (checkIsLogin()):
            logger.error("Error in Login!!")
            return
        
        refresh()
        timeNow = datetime.datetime.now()
        seconds=timeNow.second+60*(timeNow.minute+60*timeNow.hour)+(0.000001*timeNow.microsecond)
        if (seconds>=60*(28+60*8) and seconds<=60*(32+60*8)):
            time.sleep(60*3+1)
        saveCookie2File()

        targetTime = datetime.datetime.now() + datetime.timedelta(minutes=refreshMinutes)
        doOperationAt_Time(autoRefreshChrome, None, "Chrome refresh Triggered", \
            targetTime.hour, targetTime.minute, targetTime.second, 0.0,\
                0,0,0,0)
    
    autoRefreshChrome()


def loadAllsendBuyRequest():
    def sendBuyRequestNow(orderData):
        def loadCookieFromFile(filename):
            db = TinyDB(filename)
            cookiesDB = db.all()
            cookies={}
            for cookieDB in cookiesDB:
                cookies[cookieDB["name"]]=cookieDB["value"]
            db.close()
            return cookies
        
        requests.packages.urllib3.disable_warnings()
        try:
            sendOrderurl="https://onlineplus.mofidonline.com/Customer/SendOrder"
            
            postData={\
                "IsSymbolCautionAgreement":"false"
                ,"CautionAgreementSelected":"false"
                ,"IsSymbolSepahAgreement":"false"
                ,"SepahAgreementSelected":"false"
                ,"orderCount":orderData["orderCount"]
                ,"orderPrice":orderData["orderPrice"]
                ,"FinancialProviderId":"1"
                ,"minimumQuantity":""
                ,"maxShow":"0"
                ,"orderId":"0"
                ,"isin":orderData["isin"]
                ,"orderSide":"65"
                ,"orderValidity":"74"
                ,"orderValiditydate":"null"
                ,"shortSellIsEnabled":"false"
                ,"shortSellIncentivePercent":"0"
            }
            
            headers = {\
                # ":method":"POST"\
                # ,":scheme":"https"\
                # ,":authority":"onlineplus.mofidonline.com"\
                # ,":path":"/Customer/SendOrder"\
                #,"content-length":"371"\
                "sec-fetch-dest":"empty"\
                ,"x-requested-with":"XMLHttpRequest"\
                ,'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'\
                ,"content-type":"application/json"\
                ,"accept":"*/*"\
                ,"origin":"https://onlineplus.mofidonline.com"\
                ,"sec-fetch-site":"same-origin"\
                ,"sec-fetch-mode":"cors"\
                ,"referer":"https://onlineplus.mofidonline.com/Home/Default/page-1"\
                ,"accept-encoding":"gzip, deflate, br"\
                ,"accept-language":"en-US,en;q=0.9"\
                
                #,"cookie":
                ## lastmessage-6=1
                ## lastmessage-2=1060528
                ## lastmessage-4=1
                ## "UserHasReadedHelp=true; 
                # _ga=GA1.2.816572881.1569671965;
                #  GuidedTourVersion=1; 
                # SiteVersion=3.7.4; 
                # _gid=GA1.2.252721106.1584126160; 
                ## _AuthCookie={\"t\":\"\",\"p\":1}; 
                # silverse=105h0lilzyxndpiigtkdvj3f; 
                # crisp-client%2Fsession%2Fe95056ad-2681-452d-976d-0c2a304165c9=session_bb27ba3c-c5ad-41aa-a983-e6b1cf022809; 
                ## ASP.NET_SessionId=ru0y0x5yfcht1gnotz1keng1;
                # .ASPXAUTH=A01484135FB8B5662BFD98E7E64EAAEEA18BF3BB08E9C43D7E1D9044A547705A483920EB562FA06DB6885AB016B6CC800492CDC1974BE30AE04BCEBE639F7D3061AE0842E5F1FC558D8B275918F085A210B21C4B1541BFA5997C60080F89107DA00A171B8BADBB29063BAE6A9326CAAFC98C4376375FF02987EEBCD653EA55C7; 
                # Token=4f6d168e-62df-46aa-991b-a84f912140e8"
            }
            localCookieFilename = baseFolder+cookieFilename+orderData["cookieFileIndex"]+'.json'
            cookies = loadCookieFromFile(localCookieFilename)
            def requestWorker():
                dateTimeRequest=datetime.datetime.now()
                response = requests.post(sendOrderurl\
                    , data=jsons.dumps(postData), headers=headers, cookies=cookies\
                    , verify = False, timeout=(10, 20))
                dateTimeResponse=datetime.datetime.now()
                logger.info("Calc\t"+orderData["cookieFileIndex"]+"\t"\
                    + str("%.6f" % (dateTimeRequest.second+dateTimeRequest.microsecond*0.000001))+"\t"\
                    + str("%.6f" % (dateTimeResponse.second+dateTimeResponse.microsecond*0.000001))+"\t"\
                    + str("%.6f" % ((dateTimeResponse-dateTimeRequest).microseconds*0.000001))+"\t"\
                    + str("%.6f" % (response.elapsed.total_seconds()))+"\t"
                    + str(jsons.loads(response.content)["MessageDesc"])+"\t"
                    + str(orderData["comment"]))
                    # +"\n"
                    # +"Request:"+str(dateTimeRequest)+"\n"\
                    # +"  Response:"+str(datetime.datetime.now())+"\n"\
                    # +"  orderData: " + str(orderData)+"\n"\
                    # +"  content: " + str(response.content)+"\n"\
                    # +"  total_seconds: " + str(response.elapsed.total_seconds())+"\n")
            threading.Thread(target=requestWorker).start()
                    
        except Exception as err:
            logger.error(f'Other error occurred: {err}') 
            ErrorJson=True
    realTimer = RealTimer()
    realTimer.setOffset(0,0,0,0)
    orderFileDB = TinyDB(orderFile)
    orderFileDatas = orderFileDB.all()

    for orderData in orderFileDatas:
        if (orderData["status"].strip().lower()=="done"):
            continue
        # orderCount=orderData["orderCount"]
        # orderPrice=orderData["orderPrice"]
        # isin=orderData["isin"]
        # isinName=orderData["isinName"]
        absoluteTime=orderData["absoluteTime"].split(":")
        hour=int(absoluteTime[0])
        minute=int(absoluteTime[1])
        second=int(absoluteTime[2])
        microSecond=int(absoluteTime[3])*0.000001
        realTimer.add(sendBuyRequestNow, orderData, orderData["comment"]\
            , hour, minute, second, microSecond)
        repeatTime=float(orderData["repeatTime"])
        repeatCount=int(orderData["repeatCount"])
        for counter in range(1,repeatCount):
            target=second+60*(minute+60*hour)+microSecond+(repeatTime*counter)
            microSecondTarget=target-int(target)
            target=int(target)
            secondTarget=target%60
            target=int(target/60)
            minuteTarget=target%60
            target=int(target/60)
            hourTarget=target
            if (target<24):
                customOrderData=orderData.copy()
                customOrderData["orderCount"]=str(int(customOrderData["orderCount"])+counter)
                realTimer.add(sendBuyRequestNow, customOrderData, orderData["comment"]+":"+str(counter)\
                    , hourTarget, minuteTarget, secondTarget, microSecondTarget)
                
    orderFileDB.close()
    realTimer.start()
   
def initLogger():
    logger = logging.getLogger(name+cookieFileIndex)
    fileHandler = logging.FileHandler(logFile)
    formatter = logging.Formatter("%(asctime)s [%(name)-11.11s] [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler) 
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)       
    return logger

if __name__ == "__main__":
    name="slave"
    cookieFileIndex = ""
    if(len(sys.argv)>1):
        name = sys.argv[1].strip().lower()
    if(len(sys.argv)>2):
        cookieFileIndex = sys.argv[2].strip().lower()
   
    logger=initLogger()
    logger.info('start ' + name + " " + cookieFileIndex)

    if (name=="master"):
        cookieFile = baseFolder+cookieFilename+cookieFileIndex+'.json'
        chromeProfilePath=chromeProfilePath+cookieFileIndex
        loadChromeAndWaitToLoad()
    elif (name=="slave"):
        loadAllsendBuyRequest()

    logger.info('Waiting...')

    #TODO 13990102:CreateUI For operation in order file
    #Done by linux network time is done: time : sudo ntpdate time.windows.com
    #done multi chrome with multi folder and ... with multi cookie loader from file
    #done Done with simple way :Mirtual exclution with cookieFile
    #Done Expire cookie examination
    #Expire auto pass typing
