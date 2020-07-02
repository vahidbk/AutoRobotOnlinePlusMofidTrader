from tinydb import TinyDB, Query
from tinydb import where
import logging
import os

def sendRequestFromOrderJsonFile(logger, cookieFileIndex):
    rootFolder=os.getcwd()+"/"
    orderFile = rootFolder+'orderList.json'

    from RealTimer import RealTimer
    realTimer = RealTimer(logger)
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
        orderData["logger"]=logger
        from OnlinePlusRequests import sendOrderRequestByDictionary
        realTimer.add(sendOrderRequestByDictionary, orderData, orderData["comment"]\
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
                orderData["logger"]=logger
                realTimer.add(sendOrderRequestByDictionary, customOrderData, orderData["comment"]+":"+str(counter)\
                    , hourTarget, minuteTarget, secondTarget, microSecondTarget)
                
    orderFileDB.close()
    realTimer.start()
   
if __name__ == "__main__":
    name="slaveTest"
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
    sendRequestFromOrderJsonFile(logger, cookieFileIndex)