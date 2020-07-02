#python3 -c 'import datetime;import os;print(datetime.datetime.now());os.system("ping -c 10 google.com")'

import threading
import datetime
import time
import sys
import logging
import os

rootFolder=os.getcwd()+"/"
baseFolder=rootFolder+"temp/"   
try:
    os.mkdir(baseFolder) 
except:
    pass
cookieFilename='MofidOnlineCookieFile'
cookieFile = baseFolder+cookieFilename+'.json'
lockFile=cookieFile+".lock"


orderFile = rootFolder+'orderList.json'

def initLogger():
    logger = logging.getLogger(name+cookieFileIndex)
    logFile=rootFolder+'logger.log'
    fileHandler = logging.FileHandler(logFile)
    formatter = logging.Formatter("%(asctime)s [%(name)-11.11s] [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler) 
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)       
    return logger

if __name__ == "__main__":
    name="master"
    cookieFileIndex = "-one"
    if(len(sys.argv)>1):
        name = sys.argv[1].strip().lower()
    if(len(sys.argv)>2):
        cookieFileIndex = sys.argv[2].strip().lower()
   
    logger=initLogger()
    logger.info('start ' + name + " " + cookieFileIndex)

    if (name=="master"):
        from LoadMofidOnlinePlusInChrome import loadChromeAndWaitToLoad
        loadChromeAndWaitToLoad(logger, cookieFileIndex)
    elif (name=="slave"):
        from sendRequestFromOrderJsonFile import sendRequestFromOrderJsonFile
        sendRequestFromOrderJsonFile(logger, cookieFileIndex)
    elif (name=="Monitoring"):
        startDateTime = "08:30:00.000000"
        endDateTime = "12:30:00.000000"
        symbolISIN = "IRO1TAMN0001"
        orderCondition=null
        monitoringAndSendRequest(logger, symbolISIN, startDateTime, endDateTime, orderCondition)
    logger.info('Waiting...')

    #TODO  13990102:CreateUI For operation in order file
    #Done: create a mofid login with out capcha
    #Done by linux network time is done: time : sudo ntpdate time.windows.com
    #done multi chrome with multi folder and ... with multi cookie loader from file
    #done Done with simple way :Mirtual exclution with cookieFile
    #Done Expire cookie examination
    #Expire auto pass typing


