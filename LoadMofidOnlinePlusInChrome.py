
import datetime
import logging
import threading
import time
from tinydb import TinyDB, Query
from tinydb import where
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import atexit
import os

class loadChromeAndWaitToLoad:
    def __init__(self, logger, cookieFileIndex):
        self.showUI = True
        self.loginWithMofid=True
        self.refreshUrl='https://onlineplus.mofidonline.com/Home/Default/page-1'
        self.refreshMinutes=15

        self.rootFolder=os.getcwd()+"/"
        self.baseFolder=self.rootFolder+"temp/"
        self.logger=logger
        self.cookieFilename='MofidOnlineCookieFile'
        self.cookieFileIndex = cookieFileIndex
        self.cookieFile = self.baseFolder+self.cookieFilename+self.cookieFileIndex+'.json'
        try:
            os.mkdir(self.baseFolder) 
        except:
            pass
        self.lockFile=self.cookieFile+".lock"

        self.chromeProfilePath=self.baseFolder+'ChromeProfile'+self.cookieFileIndex
        
        self.chromeWebDriverPath = '/usr/lib/chromium-browser/chromedriver'

        options = webdriver.ChromeOptions()
        if not (self.showUI):
            options.add_argument('headless')
            options.add_argument('window-size=1920x1080')
            options.add_argument("disable-gpu")
        options.add_argument("--log-level=3")
        options.add_argument("user-data-dir="+self.chromeProfilePath) #Path to your chrome profile
        self.driver = webdriver.Chrome(executable_path=self.chromeWebDriverPath, options=options)
        atexit.register(self.onClose)
        self.driver.get(self.refreshUrl)
        if not (self.loginWithMofid):
            username=self.driver.find_element_by_id("txtusername")
            password=self.driver.find_element_by_id("txtpassword")
            mofidAccount=self.getMofidAccountData()
            username.send_keys(mofidAccount["username"])
            password.send_keys(mofidAccount["password"])
            while(True):
                if (self.checkIsLogin()):
                    break

        self.autoRefreshChrome()

    def doOperationAt_Time(self, doOperation, params, comment\
        , hourTarget, minuteTarget, secondTarget, microSecondTarget):
        
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
            self.logger.info(timeNow)
            if (doOperation):
                if (params!=None):
                    doOperation(params)
                else:
                    doOperation() 
            
        SecondTimeTimerThread = threading.Thread(target=RealTimeTimerTriggerWorker)
        SecondTimeTimerThread.start()

    def getMofidAccountData(self):
        securitySettingFilename=self.rootFolder+'securitySetting.json'
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

    def checkIsLogin(self):
        #<a class="signout " href="/Account/Logout">
        inputStr="//a[@class='signout ' and @href='/Account/Logout']"
        signOutElems = self.driver.find_elements_by_xpath(inputStr) 
        if (signOutElems):
            return True
        return False
    
    def onClose(self):
        self.logger.info('Exit') 
        if (self.driver):
            self.driver.close()
        
    def autoRefreshChrome(self):
        def saveCookie2File():
            cookies=self.driver.get_cookies()
            self.logger.info('cookies:'+str(cookies))
            try:
                db = TinyDB(self.cookieFile)
                db.purge_tables()
                db.insert_multiple(cookies)
                db.close()
            except Exception as err:
                self.logger.error(f'Error in save cookie File: {err}') 
        def refresh():
            try:
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.driver.refresh()
                self.logger.info(str(datetime.datetime.now())+" Soft Refreshed..")
            except Exception as err:
                self.driver.get(self.refreshUrl)
                self.logger.info(str(datetime.datetime.now())+" Hard Refreshed..")
        def loginWithMofidAccount():
            while(True):
                refresh()
                time.sleep(2)
                if (self.checkIsLogin()):
                    break 
                self.driver.get(self.refreshUrl)
                elem = self.driver.find_element_by_class_name("mofid__input-button")
                elem.click()

                counter=0
                mofidLoginWindowExist=False
                while(True):
                    if (len(self.driver.window_handles)==2):
                        mofidLoginWindowExist=True
                        break
                    else:
                        time.sleep(1)
                        counter+=1
                        if counter>10:break
                if (mofidLoginWindowExist):
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    time.sleep(1)
                    username=self.driver.find_element_by_id("Username")
                    password=self.driver.find_element_by_id("Password")
                    loginButton=self.driver.find_element_by_id("submit_btn")
                    mofidAccount=self.getMofidAccountData()
                    username.send_keys(mofidAccount["username"])
                    password.send_keys(mofidAccount["password"])
                    loginButton.click()
                self.driver.switch_to.window(self.driver.window_handles[0])
                if (self.checkIsLogin()):
                    break
                time.sleep(10)
                if (self.checkIsLogin()):
                    break    
                time.sleep(45)
                if (self.checkIsLogin()):
                    break   
            self.driver.switch_to_default_content()   
    
        if not (self.checkIsLogin()):
            if not (self.loginWithMofid):
                exit(0)
            else:
                loginWithMofidAccount()
        
        from filelock import Timeout, FileLock
        lock = FileLock(self.lockFile)
        with lock:
            refresh()
            saveCookie2File()

        targetTime = datetime.datetime.now() + datetime.timedelta(minutes=self.refreshMinutes)
        self.doOperationAt_Time(self.autoRefreshChrome, None, "Chrome refresh Triggered", \
            targetTime.hour, targetTime.minute, targetTime.second, 0.0)

if __name__ == "__main__":
    name="masterTest"
    cookieFileIndex = "-one"
    def initLogger():
        import sys
        logger = logging.getLogger(name+cookieFileIndex)
        logFile= 'logger.log'
        fileHandler = logging.FileHandler(logFile)
        formatter = logging.Formatter("%(asctime)s [%(name)-11.11s] [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler) 
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel(logging.INFO)       
        return logger
    logger=initLogger()
    logger.info('start ' + name + " " + cookieFileIndex)

    loadChromeAndWaitToLoad(logger, "-ooo")