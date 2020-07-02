import logging
import threading
import datetime
import time

epsilonSecond4RealTimer=10

class RealTimer:

    def __init__(self, logger):
        self.logger=logger
        
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
                    self.logger.info("TimerRejected :"+str(params))   
        self.sortedList = sortSortedListBySecondTarget(self.sortedList)
        threading.Thread(target=RealTimeTimerTriggerWorker).start()

    def add(self, doOperation, params, comment\
        , hourTarget, minuteTarget, secondTarget, microSecondTarget):

        secondsTarget=secondTarget+60*(minuteTarget+60*hourTarget)+microSecondTarget
        self.sortedList.append([secondsTarget, doOperation, params, comment])
        self.logger.info("triggerAt: "+str(secondsTarget) +" Or:"+ str(hourTarget)+":"+ str(minuteTarget)+":"+ str(secondTarget)+","+ str(microSecondTarget)+" Do:"+str(params))
