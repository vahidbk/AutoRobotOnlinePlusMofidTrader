import sys
from tinydb import TinyDB, Query
from tinydb import where
import requests
from bs4 import BeautifulSoup
import requests.packages.urllib3
import jsons
import threading
import datetime
import time
import logging
import os

# Start Common Variables
rootFolder=os.getcwd()+"/"
baseFolder=rootFolder+"temp/"   
try:
    os.mkdir(baseFolder) 
except:
    pass
cookieFilename='MofidOnlineCookieFile'
cookieFile = baseFolder+cookieFilename+'.json'
lockFile=cookieFile+".lock"
# End Common Variables

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

def sendOrderRequest(logger, orderTypeInput, orderCountInput, orderPriceInput, orderisinInput, cookieFileIndexInput, orderCommentInput):
    
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

def sendOrderRequestByDictionary(orderData):
    logger=orderData["logger"]
    orderTypeInput=orderData["type"]
    orderCountInput=orderData["orderCount"]
    orderPriceInput=orderData["orderPrice"]
    orderisinInput=orderData["isin"]
    cookieFileIndexInput=orderData["cookieFileIndex"]
    orderCommentInput=orderData["comment"]
    sendOrderRequest(logger, orderTypeInput, orderCountInput, orderPriceInput, orderisinInput, cookieFileIndexInput, orderCommentInput)

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
