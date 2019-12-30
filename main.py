from lxml import etree
from time import sleep
from datetime import datetime as dt
import requests
import argparse

parser = argparse.ArgumentParser(description='Placeholder')

parser.add_argument('--start-date', default='2020-12-31', dest="startDate")
parser.add_argument('--end-date', default='2012-1-1', dest="endDate")
parser.add_argument('--output', default='output.csv', dest="outputFileName")

args=vars(parser.parse_args())
def getOrdinal(dateStr):
    return dt.strptime(dateStr, r'%Y-%m-%d').date().toordinal()

def subCrawl(topDomainUrl, url):
    sleep(0.1)
    subResponse = requests.get(topDomainUrl + url)
    subHtmlText = subResponse.content.decode()
    subRoot = etree.HTML(subHtmlText)
    contentParsedResult = subRoot.xpath('//div[@class="editor content"]//*')
    # print(len(contentParsedResult))
    retValue = ""
    for i in subRoot.xpath('//div[@class="editor content"]'):
        if i.text != None:
            retValue += i.text.strip()
    for i in contentParsedResult:
        if i.text != None:
            retValue += i.text.strip()
    solidRetValue = ""
    for char in retValue:
        if char != "\"":
            solidRetValue += char
        else:
            solidRetValue += "\"\""
    # print(retValue)
    return solidRetValue

def masterCrawl(startDateStr, endDateStr):
    ofile = open(args['outputFileName'], "wt", encoding="UTF-8")
    topDomainUrl = "https://www.csie.ntu.edu.tw/news/"
    pageChangeUrl = "news.php?class=101&no="
    currentPage = 0
    startOrdinal = getOrdinal(startDateStr)
    endOrdinal = getOrdinal(endDateStr)
    if startOrdinal > endOrdinal:
        startOrdinal, endOrdinal = endOrdinal, startOrdinal
    testingCount = 0
    flag = True
    while flag:
        sleep(0.1)
        masterResponse = requests.get(
            topDomainUrl + pageChangeUrl + str(currentPage))
        masterHtmlText = masterResponse.content.decode()
        masterRoot = etree.HTML(masterHtmlText)
        dateParsedResult = masterRoot.xpath(
            '/html/body/div[1]/div/div[2]/div/div/div[2]/div/table/tbody/tr/td[1]')
        titleParsedResult = masterRoot.xpath(
            '/html/body/div[1]/div/div[2]/div/div/div[2]/div/table/tbody/tr/td[2]/a')
        subUrlParsedResult = masterRoot.xpath(
            '/html/body/div[1]/div/div[2]/div/div/div[2]/div/table/tbody/tr/td[2]//@href')
        for i in range(10):
            if getOrdinal(dateParsedResult[i].text) < startOrdinal:
                flag = False
                break
            if getOrdinal(dateParsedResult[i].text) > endOrdinal:
                continue
            #print(dateParsedResult[i].text, end=",")
            #print(titleParsedResult[i].text, end=",")
            content = subCrawl(topDomainUrl, subUrlParsedResult[i])
            # print(content)
            ofile.write("\"" + dateParsedResult[i].text + "\",\"" +
                        titleParsedResult[i].text + "\",\"" + content + "\"\n")

        testingCount += 1
        currentPage += 10
        #break
    ofile.close()

masterCrawl(args['startDate'], args['endDate'])
