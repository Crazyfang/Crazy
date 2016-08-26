# -*- coding: utf-8 -*-
import re
import sys
import urllib2
import logging
import requests
import os
import time
import socket
socket.setdefaulttimeout(5)
reload(sys)
sys.setdefaultencoding('utf-8')

#mainlist=[]             #第一层总页数
secondlist = []           #第二层总页数
mark = ''
Sign = []
length = 0
num = 0

#读取已缓存图片编号
def ReadSignFromFile(url):
    if os.path.isfile(url):
        try:
            file = open(url)
            adjust = file.readline()
            while adjust:
                Sign.append(adjust)
                adjust = file.readline()
            length = len(Sign)
            file.close()
            print Sign
        except Exception, e:
            print e
    else:
        print "The file path is illegality!"

#读取网页源码
def getUrl_multiTry(url):
    maxTryNum = 10
    html = ''
    for tries in range(maxTryNum):
        try:
            request = urllib2.Request(url)
            request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')
            response = urllib2.urlopen(request)
            html = response.read()
            break
        except:
            if tries <(maxTryNum-1):
                continue
            else:
                logging.error("Has tried %d times to access url %s, all failed!", maxTryNum, url)
                break
    return html

#第一层页面全部读取
def MainList(html):
    # file=open('E:\\sign.txt','a')
    global secondlist
    global num
    mainurl = re.compile('<a href="(.*?).html">')
    sign = re.compile('\d{1,7}')
    mainurl_list = re.findall(mainurl,html)
    for i in range(0, len(mainurl_list)):
        signs=re.findall(sign, mainurl_list[i])
        signs[0] = signs[0]+'\n'
        if length == 0:
            html = getUrl_multiTry(mainurl_list[i]+".html")
            if html:
                RecursiveOfQuery(html, mainurl_list[i]+".html")
                # mainlist.append(mainurl_list[i]+".html")
                Sign.append(signs[0])
                if len(secondlist) != 1:
                    for k in range(0, len(secondlist)):
                        html = getUrl_multiTry(secondlist[k])
                        if html:
                            TurnsDownLoad(html, k)
                        else:
                            print u'读取网页失败！'
                    secondlist = []
                else:
                    secondlist = []
                WriteResidueData()
            else:
                print u'读取网页失败！'
        else:
            if signs[0] not in Sign:
                html = getUrl_multiTry(mainurl_list[i]+".html")
                if html:
                    print mainurl_list[i]+".html"
                    RecursiveOfQuery(html, mainurl_list[i]+".html")
                    Sign.append(signs[0])
                    if len(secondlist) != 1:
                        for k in range(0, len(secondlist)):
                            html = getUrl_multiTry(secondlist[k])
                            if html:
                                TurnsDownLoad(html, k)
                            else:
                                print u'读取网页失败！'
                        secondlist = []
                    else:
                        secondlist = []
                    WriteResidueData()
                else:
                    print u'读取网页失败！'
            else:
                print 'The Same ID,Jump out!!'

        # file.write(signs[0]+'\n')
    # file.close()

def WriteResidueData():
    global length
    file = open(u'E:\\爬虫图片收集\\美色网\\sign.txt','a')
    for i in range(length, len(Sign)):
        file.write(Sign[i])
    file.close()
    length = len(Sign)
    print 'Save Success!'

#第二层页面全部读取
def RecursiveOfQuery(html,str):
    MaxPage = re.compile('var countPage = "(.*?)";')
    ss='.html'
    # NextPage=re.compile('var right = "(.*?)";')
    CurrentPage = re.compile('var page = "(.*?)";')
    MaxPages = re.findall(MaxPage,html)
    # NextPages=re.findall(NextPage,html)
    secondlist.append(str)
    print str
    CurrentPages=re.findall(CurrentPage, html)
    if int(MaxPages[0]) > 1:
        for i in range(2, int(MaxPages[0])+1):
            str = str.replace(ss, '_%s.html' % i)
            ss = '_%s.html' % i
            secondlist.append(str)
            print str
    else:
        print 'It is empty pages!!!!!!'

#轮流下载图片
def TurnsDownLoad(html,k):
    lianjie = re.compile('<img class="petImg" src="(.*?)" />')
    lianjies = re.findall(lianjie, html)
    DownPicture(lianjies[0], k)
    print lianjies[0]

#下载图片
def DownPicture(url,k):
    response = requests.get(url, stream=True)
    image = response.content
    date = time.strftime('%H-%M-%S', time.localtime(time.time()))
    DstDir = u'E:\\爬虫图片收集\\美色网\\图片\\'+date+"-%d"%k+".jpg"
    print("保存文件"+DstDir+"\n")
    try:
        with open(DstDir, "wb") as jpg:
            jpg.write(image)
            jpg.close()
    except IOError:
        print("IO Error\n")


if __name__ == '__main__':
    urllist = ['http://mm.xmeise.com/xingge/', 'http://mm.xmeise.com/bijini/', 'http://mm.xmeise.com/nvyou/']
    if not os.path.exists(u'E:\\爬虫图片收集\\美色网\\图片'):
        os.makedirs(u'E:\\爬虫图片收集\\美色网\\图片')
        print 'Directory Creat Successful!'
    if not os.path.exists(u'E:\\爬虫图片收集\\美色网\\sign.txt'):
        files = open(u'E:\\爬虫图片收集\\美色网\\sign.txt','w')
        files.close()
        print 'File Creat Successful!'
    try:
        ReadSignFromFile(u'E:\\爬虫图片收集\\美色网\\sign.txt')
        print length
        for url in urllist:
            UrlOfHead = 'http://mm.xmeise.com'
            # lianjie=re.compile('<img class="petImg" src="(.*?)" />')
            MainMaxPage = re.compile('<a class="next" href="(.*?)">&raquo;')
            html = getUrl_multiTry(url)
            if html:
                MainMaxPages = re.findall(MainMaxPage, html)
                MainList(html)

                while MainMaxPages:
                    url = UrlOfHead+MainMaxPages[0]
                    html = getUrl_multiTry(url)
                    if html:
                        MainMaxPages = re.findall(MainMaxPage, html)
                        MainList(html)
                    else:
                        print u'读取网页失败！'
            else:
                print u'读取网页失败！'
            print "下载成功！"
    except Exception, e:
        print e
