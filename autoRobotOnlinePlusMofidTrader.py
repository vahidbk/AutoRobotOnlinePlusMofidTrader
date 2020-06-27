#python3 -c 'import datetime;import os;print(datetime.datetime.now());os.system("ping -c 10 google.com")'

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
import os

import sqlite3

rootFolder=os.getcwd()+"/"
baseFolder=rootFolder+"temp/"   
try:
    os.mkdir(baseFolder) 
except:
    pass

logFile=rootFolder+'logger.log'
refreshUrl='https://onlineplus.mofidonline.com/Home/Default/page-1'
refreshMinutes=15

chromeWebDriverPath = '/usr/lib/chromium-browser/chromedriver'


cookieFilename='MofidOnlineCookieFile'
cookieFile = baseFolder+cookieFilename+'.json'
chromeProfilePath=baseFolder+'ChromeProfile'
orderFile = rootFolder+'orderList.json'
lockFile=cookieFile+".lock"

showUI = True
epsilonSecond4RealTimer=10
loginWithMofid=True



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
                    else:
                        time.sleep(0.000001)
                if (seconds-secondsTarget<epsilonSecond4RealTimer):
                    doOperation(params)
                else:
                    logger.info("TimerRejected :"+str(params))   
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

    def getMofidAccountData():
        securitySettingFilename=rootFolder+'securitySetting.json'
        username="TypeUserNameIn:"+securitySettingFilename
        password="TypePasswordIn:"+securitySettingFilename
        mofidAccountTable="mofidAccount"
        try:
            db = TinyDB(securitySettingFilename)
            userTable = db.table(mofidAccountTable)
            user = userTable.all()
            username=user[0]["Username"]
            password=user[0]["Password"]
            db.close()
        except:
            print("Error in username and password Easy Trader.")
            db.purge_table(mofidAccountTable)
            userTable = db.table(mofidAccountTable)
            userTable.insert({"Username":username, "Password":password})
            db.close()
        return {"username":username, "password":password}

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
    options.add_argument("--log-level=3")
    options.add_argument("user-data-dir="+chromeProfilePath) #Path to your chrome profile
    driver = webdriver.Chrome(executable_path=chromeWebDriverPath, options=options)
    atexit.register(onClose)
    driver.get(refreshUrl)
    if not (loginWithMofid):
        username=driver.find_element_by_id("txtusername")
        password=driver.find_element_by_id("txtpassword")
        mofidAccount=getMofidAccountData()
        username.send_keys(mofidAccount["username"])
        password.send_keys(mofidAccount["password"])
        while(True):
            if (checkIsLogin()):
                break
        
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
            try:
                driver.switch_to.window(driver.window_handles[0])
                driver.refresh()
                logger.info(str(datetime.datetime.now())+" Soft Refreshed..")
            except Exception as err:
                driver.get(refreshUrl)
                logger.info(str(datetime.datetime.now())+" Hard Refreshed..")
        def loginWithMofidAccount():
            while(True):
                refresh()
                time.sleep(2)
                if (checkIsLogin()):
                    break 
                driver.get(refreshUrl)
                elem = driver.find_element_by_class_name("mofid__input-button")
                elem.click()

                counter=0
                mofidLoginWindowExist=False
                while(True):
                    if (len(driver.window_handles)==2):
                        mofidLoginWindowExist=True
                        break
                    else:
                        time.sleep(1)
                        counter+=1
                        if counter>10:break
                if (mofidLoginWindowExist):
                    driver.switch_to.window(driver.window_handles[1])
                    time.sleep(1)
                    username=driver.find_element_by_id("Username")
                    password=driver.find_element_by_id("Password")
                    loginButton=driver.find_element_by_id("submit_btn")
                    mofidAccount=getMofidAccountData()
                    username.send_keys(mofidAccount["username"])
                    password.send_keys(mofidAccount["password"])
                    loginButton.click()
                driver.switch_to.window(driver.window_handles[0])
                if (checkIsLogin()):
                    break
                time.sleep(10)
                if (checkIsLogin()):
                    break    
                time.sleep(45)
                if (checkIsLogin()):
                    break   
            driver.switch_to_default_content()   
    
        if not (checkIsLogin()):
            if not (loginWithMofid):
                exit(0)
            else:
                loginWithMofidAccount()
        
        from filelock import Timeout, FileLock
        lock = FileLock(lockFile)
        with lock:
            refresh()
            saveCookie2File()

        targetTime = datetime.datetime.now() + datetime.timedelta(minutes=refreshMinutes)
        doOperationAt_Time(autoRefreshChrome, None, "Chrome refresh Triggered", \
            targetTime.hour, targetTime.minute, targetTime.second, 0.0,\
                0,0,0,0)
    autoRefreshChrome()


def loadAllsendBuyRequest():
    def sendBuyRequestNow(orderData):
        def loadCookieFromFile(filename):
            from filelock import Timeout, FileLock
            lock = FileLock(lockFile)
            with lock:
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
            
            if (orderData["type"].lower()=="sell"):
                typeOrder="86"
            else:
                typeOrder="65"
                
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
                ,"orderSide":typeOrder
                ,"orderValidity":"74"
                ,"orderValiditydate":"null"
                ,"shortSellIsEnabled":"false"
                ,"shortSellIncentivePercent":"0"
            }
            headers = {\
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
            }
            localCookieFilename = baseFolder+cookieFilename+orderData["cookieFileIndex"]+'.json'
            cookies = loadCookieFromFile(localCookieFilename)
            def requestWorker():
                dateTimeRequest=datetime.datetime.now()
                response = requests.post(sendOrderurl\
                    , data=jsons.dumps(postData), headers=headers, cookies=cookies\
                    , verify = False, timeout=(10, 20))
                dateTimeResponse=datetime.datetime.now()
                logger.info("Calc:\t"+orderData["cookieFileIndex"]+"\t"\
                    + str("Sym:" + (orderData["isinName"]))+"\t"\
                    + str("Vol:" + (orderData["orderCount"]))+"\t"\
                    + str("Request:%.6f" % (dateTimeResponse.second+dateTimeResponse.microsecond*0.000001))+"\t"\
                    + str("Response:%.6f" % ((dateTimeResponse-dateTimeRequest).microseconds*0.000001))+"\t"\
                    + str("Elapsed:%.6f" % (response.elapsed.total_seconds()))+"\t"
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

#Todo compelete this function
def monitoringAndSendRequest(symbolISIN, startDateTime, EndDateTime, orderConditions):
    def loadCookieFromFile(filename):
        from filelock import Timeout, FileLock
        lock = FileLock(lockFile)
        with lock:
            db = TinyDB(filename)
            cookiesDB = db.all()
            cookies={}
            for cookieDB in cookiesDB:
                cookies[cookieDB["name"]]=cookieDB["value"]
            db.close()
        return cookies
    def sendRequest(orderTypeInput, orderCountInput, orderPriceInput, orderisinInput, cookieFileIndexInput, orderCommentInput):
        
        requests.packages.urllib3.disable_warnings()
        try:
            sendOrderurl="https://onlineplus.mofidonline.com/Customer/SendOrder"
            
            if (orderTypeInput.lower()=="sell"):
                typeOrder="86"
            else:
                typeOrder="65"
                
            postData={\
                "IsSymbolCautionAgreement":"false"
                ,"CautionAgreementSelected":"false"
                ,"IsSymbolSepahAgreement":"false"
                ,"SepahAgreementSelected":"false"
                ,"orderCount":orderCountInput
                ,"orderPrice":orderPriceInput
                ,"FinancialProviderId":"1"
                ,"minimumQuantity":""
                ,"maxShow":"0"
                ,"orderId":"0"
                ,"isin":orderisinInput
                ,"orderSide":typeOrder
                ,"orderValidity":"74"
                ,"orderValiditydate":"null"
                ,"shortSellIsEnabled":"false"
                ,"shortSellIncentivePercent":"0"
            }
            headers = {\
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
            }
            localCookieFilename = baseFolder+cookieFilename+cookieFileIndexInput+'.json'
            cookies = loadCookieFromFile(localCookieFilename)
            def requestWorker():
                dateTimeRequest=datetime.datetime.now()
                response = requests.post(sendOrderurl\
                    , data=jsons.dumps(postData), headers=headers, cookies=cookies\
                    , verify = False, timeout=(10, 20))
                dateTimeResponse=datetime.datetime.now()
                logger.info("Calc:\t"+cookieFileIndexInput+"\t"\
                    + str("Sym:" + orderisinInput)+"\t"\
                    + str("Vol:" + orderCountInput)+"\t"\
                    + str("Request:%.6f" % (dateTimeResponse.second+dateTimeResponse.microsecond*0.000001))+"\t"\
                    + str("Response:%.6f" % ((dateTimeResponse-dateTimeRequest).microseconds*0.000001))+"\t"\
                    + str("Elapsed:%.6f" % (response.elapsed.total_seconds()))+"\t"\
                    + str(jsons.loads(response.content)["MessageDesc"])+"\t"\
                    + str(orderCommentInput))
            threading.Thread(target=requestWorker).start()

        except Exception as err:
            logger.error(f'Other error occurred: {err}') 
    def monitoring(symbolISIN):
        def getInfoSymbol(symbolISIN):
            info= {\
                'id': 'XXXXXXXXXXXX 139XX/XX/XX - XX:XX:XX',
                'isin': 'XXXXXXXXXXXX',\
                'lastTradePrice': 0,\
                'closePrice': 0,\
                'highRangePrice': 0,\
                'lowRangePrice': 0,\
                'yesterdayClosePrice': 0,\
                'DateTime': '139XX/XX/XX - XX:XX:XX',\
                'Date': '139XX/XX/XX',\
                'Time': 'XX:XX:XX',\
                'closePointRelativePrice': 0,\
                'closePointRelativePercent': 0,\
                'lastPointRelativePrice': 0,\
                'lastPointRelativePercent': 0,\
                'buyToToSellPower1Row': 0,\
                'buyToToSellPower5Rows': 0,\
                'realBuyVolume': 0,\
                'realBuyNumber': 0,\
                'realSellVolume': 0,\
                'realSellNumber': 0,\
                'legalBuyVolume': 0,\
                'legalBuyNumber': 0,\
                'legalSellVolume': 0,\
                'legalSellNumber': 0,\
                'buyToSellPowerToday': 0,\
                'buyToSellLegalPowerToday': 0,\
                'legalBuyPercent': 0,\
                'legalSellPercent': 0}
            try:
                headers = {\
                            "origin":"https://onlineplus.mofidonline.com"\
                            ,"sec-fetch-dest":"empty"\
                            ,"user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/80.0.3987.163 Chrome/80.0.3987.163 Safari/537.36"\
                            ,"accept":"*/*"\
                            ,"sec-fetch-site":"cross-site"\
                            ,"sec-fetch-mode": "cors"\
                            ,"referer":"https://onlineplus.mofidonline.com/Home/Default/page-1"\
                            ,"accept-encoding":"gzip, deflate, br"\
                            ,"accept-language":"en-US,en;q=0.9,fa;q=0.8"\
                            }
                url='https://core.tadbirrlc.com//StockFutureInfoHandler.ashx?{"Type":"getLightSymbolInfoAndQueue","la":"fa","nscCode":"'+symbolISIN+'"}&jsoncallback='

                response = requests.get(url, headers=headers, verify = False, timeout=(10, 20))

                stockFutureInfoHandler = (jsons.loads(response.content))
                # info={}
                info['isin'] = stockFutureInfoHandler['symbolinfo']['nc']
                info['lastTradePrice'] = stockFutureInfoHandler['symbolinfo']['ltp']
                info['closePrice'] = stockFutureInfoHandler['symbolinfo']['cp']
                info['highRangePrice'] = stockFutureInfoHandler['symbolinfo']['ht']
                info['lowRangePrice'] = stockFutureInfoHandler['symbolinfo']['lt']
                info['yesterdayClosePrice'] = stockFutureInfoHandler['symbolinfo']['pcp']
                info['DateTime'] = stockFutureInfoHandler['symbolinfo']['ltd']
                info['id'] = info['isin'] + ' ' + info['DateTime']
                info['Date'] = info['DateTime'][0:0+10]
                info['Time'] = info['DateTime'][13:13+8]
                info['closePointRelativePrice'] = stockFutureInfoHandler['symbolinfo']['cpv']
                info['closePointRelativePercent'] = stockFutureInfoHandler['symbolinfo']['cpvp']
                info['lastPointRelativePrice'] = stockFutureInfoHandler['symbolinfo']['lpv']
                info['lastPointRelativePercent'] = stockFutureInfoHandler['symbolinfo']['lpvp']


                bestBuyQuantity = float(stockFutureInfoHandler['symbolqueue']['Value'][0]['BestBuyQuantity'])+1
                noBestBuy = float(stockFutureInfoHandler['symbolqueue']['Value'][0]['NoBestBuy']) + 1
                bestSellQuantity = float(stockFutureInfoHandler['symbolqueue']['Value'][0]['BestSellQuantity'])+1
                noBestSell = float(stockFutureInfoHandler['symbolqueue']['Value'][0]['NoBestSell']) + 1
                buyToToSellPower = float(bestBuyQuantity/noBestBuy)/(bestSellQuantity/noBestSell)
                info['buyToToSellPower1Row']=buyToToSellPower

                bestBuyQuantity = 0
                noBestBuy = 0
                bestSellQuantity = 0
                noBestSell = 0
                for counter in range(0,4):
                    bestBuyQuantity += float(stockFutureInfoHandler['symbolqueue']['Value'][counter]['BestBuyQuantity'])+1
                    noBestBuy += float(stockFutureInfoHandler['symbolqueue']['Value'][counter]['NoBestBuy']) + 1
                    bestSellQuantity += float(stockFutureInfoHandler['symbolqueue']['Value'][counter]['BestSellQuantity'])+1
                    noBestSell += float(stockFutureInfoHandler['symbolqueue']['Value'][counter]['NoBestSell']) + 1

                buyToToSellPower5Rows = float(bestBuyQuantity/noBestBuy)/(bestSellQuantity/noBestSell)
                info['buyToToSellPower5Rows']=buyToToSellPower5Rows

                # sendOrderurl='https://onlineplus.mofidonline.com/Handlers/GetAccountRemain.ashx'
                # response = requests.get(sendOrderurl, headers=headers, verify = False, timeout=(10, 20))
                # accountRemain = (jsons.loads(response.content))
                # print(accountRemain)


                #TODO: try except is not exist
                url='https://core.tadbirrlc.com//AlmasDataHandler.ashx?{"Type":"getIndInstTrade","la":"Fa","nscCode":"'+symbolISIN+'","ZeroIfMarketIsCloesed":true}&jsoncallback='
                response = requests.get(url, headers=headers, verify = False, timeout=(10, 20))
                IndInstTrade = (jsons.loads(response.content))

                realBuyVolume = int(IndInstTrade['IndBuyVolume'])
                realBuyNumber = int(IndInstTrade['IndBuyNumber'])
                realSellVolume = int(IndInstTrade['IndSellVolume'])
                realSellNumber = int(IndInstTrade['IndSellNumber'])

                legalBuyVolume = int(IndInstTrade['InsBuyVolume'])
                legalBuyNumber = int(IndInstTrade['InsBuyNumber'])
                legalSellVolume = int(IndInstTrade['InsSellVolume'])
                legalSellNumber = int(IndInstTrade['InsSellNumber'])
                realLegalDate = IndInstTrade['day']

                info['realBuyVolume'] = realBuyVolume
                info['realBuyNumber'] =realBuyNumber 
                info['realSellVolume'] = realSellVolume
                info['realSellNumber'] = realSellNumber

                info['legalBuyVolume'] = legalBuyVolume 
                info['legalBuyNumber'] = legalBuyNumber
                info['legalSellVolume'] = legalSellVolume
                info['legalSellNumber'] = legalSellNumber

                buyToSellPowerToday = float(realBuyVolume/realBuyNumber+1)/float(realSellVolume/realSellNumber+1)
                buyToSellLegalPowerToday = float(legalBuyVolume+1)/float(legalSellVolume+1)
                legalBuyPercent=(legalBuyVolume+1)/(legalBuyVolume+realBuyVolume+1)
                legalSellPercent=(legalSellVolume+1)/(legalSellVolume+realSellVolume+1)

                info['buyToSellPowerToday'] = buyToSellPowerToday
                info['buyToSellLegalPowerToday'] = buyToSellLegalPowerToday
                info['legalBuyPercent'] = legalBuyPercent
                info['legalSellPercent'] = legalSellPercent
            except Exception as err:
                #TODO:correct this after log!!
                pass
            return info
        def saveInfoSymbolToDB(datas):
            conn = sqlite3.connect(r"InfoSymbol.db")
            c = conn.cursor()
            CreateSymbolsTableQuery=\
                """CREATE TABLE IF NOT EXISTS InfoSymbols(
                id TEXT PRIMARY KEY,
                isin TEXT,
                lastTradePrice Integer,
                closePrice Integer,
                highRangePrice Integer,
                lowRangePrice Integer,
                yesterdayClosePrice Integer,
                DateTime TEXT,
                Date TEXT,
                Time TEXT,
                closePointRelativePrice FLOAT,
                closePointRelativePercent FLOAT,
                lastPointRelativePrice FLOAT,
                lastPointRelativePercent FLOAT,
                buyToToSellPower1Row FLOAT,
                buyToToSellPower5Rows FLOAT,
                realBuyVolume INTEGER,
                realBuyNumber INTEGER,
                realSellVolume INTEGER,
                realSellNumber INTEGER,
                legalBuyVolume INTEGER,
                legalBuyNumber INTEGER,
                legalSellVolume INTEGER,
                legalSellNumber INTEGER,
                buyToSellPowerToday FLOAT,
                buyToSellLegalPowerToday FLOAT,
                legalBuyPercent FLOAT,
                legalSellPercent FLOAT
                );"""
            c = conn.cursor()
            c.execute(CreateSymbolsTableQuery)
            conn.commit()
            c.execute("""insert or replace INTO InfoSymbols VALUES (
                            :id,
                            :isin,
                            :lastTradePrice,
                            :closePrice,
                            :highRangePrice,
                            :lowRangePrice,
                            :yesterdayClosePrice,
                            :DateTime,
                            :Date,
                            :Time,
                            :closePointRelativePrice,
                            :closePointRelativePercent,
                            :lastPointRelativePrice,
                            :lastPointRelativePercent,
                            :buyToToSellPower1Row,
                            :buyToToSellPower5Rows,
                            :realBuyVolume,
                            :realBuyNumber,
                            :realSellVolume,
                            :realSellNumber,
                            :legalBuyVolume,
                            :legalBuyNumber,
                            :legalSellVolume,
                            :legalSellNumber,
                            :buyToSellPowerToday,
                            :buyToSellLegalPowerToday,
                            :legalBuyPercent,
                            :legalSellPercent)""", datas)
            conn.commit()
            conn.close()

        def loadInfoSymbolListFromDB():
            conn = sqlite3.connect(r"InfoSymbol.db")
            c = conn.cursor()
            c.execute("SELECT * FROM InfoSymbols")
            data=c.fetchall()
            conn.close()
            return data

        datas = getInfoSymbol("IRO1TAMN0001")
        saveInfoSymbolToDB(datas)
        datas = getInfoSymbol("IRO1KVIR0001")
        saveInfoSymbolToDB(datas)
                
        return False

    while(True):
        #todo: input parametes of function must correct
        #todo: input parametes of function must connect to wordpress
        time.sleep(1)
        timeNow = datetime.datetime.now().replace(year=2020, month=1, day=1)
        timeStartTarget = datetime.datetime.strptime(startDateTime, '%H:%M:%S.%f').replace(year=2020, month=1, day=1)
        timeEndTarget = datetime.datetime.strptime(endDateTime, '%H:%M:%S.%f').replace(year=2020, month=1, day=1)

        if (timeNow<timeStartTarget or timeNow>timeEndTarget):
            continue
        else:
            if (monitoring(symbolISIN)):
                # sendRequest(orderTypeInput, orderCountInput, orderPriceInput, orderisinInput, cookieFileIndexInput, orderCommentInput)
                break

if __name__ == "__main__":
    name="Monitoring"
    cookieFileIndex = "-one"
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
    elif (name=="Monitoring"):
        startDateTime = "08:30:00.000000"
        endDateTime = "12:30:00.000000"
        monitoringAndSendRequest(0, startDateTime, endDateTime, 0)
    logger.info('Waiting...')

    #TODO  13990102:CreateUI For operation in order file
    #Done: create a mofid login with out capcha
    #Done by linux network time is done: time : sudo ntpdate time.windows.com
    #done multi chrome with multi folder and ... with multi cookie loader from file
    #done Done with simple way :Mirtual exclution with cookieFile
    #Done Expire cookie examination
    #Expire auto pass typing
