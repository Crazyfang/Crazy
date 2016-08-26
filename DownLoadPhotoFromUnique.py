#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
import sys
import urllib2
import urllib
import logging
import os
import time
import socket

socket.setdefaulttimeout(5)
reload(sys)
sys.setdefaultencoding('utf-8')

class DownPhotoAuto():

    def __init__(self):
        """
            功能:爬图类初始化函数
            :参数名    类型          描述
            :self      instance     实例本身
        """
        self.PicturePath = u"E:\\爬虫图片收集\\唯一网\\图片"         # 图片保存路径
        self.FirstPage = []                                          # 图集编号所处第一层网页列表
        self.Sign = []                                               # 下载过的图集编号列表
        self.DirectoryCreate()                                       # 调用文件夹检测存在及创建函数
        self.ReadOldSign()                                           # 调用读取已下载图集编号函数

    def DirectoryCreate(self):
        """
            功能：爬图类文件夹检测是否存在及创建函数
            :参数名    类型          描述
            :self      instance     实例本身
        """
        if not os.path.exists(self.PicturePath):                   # 判断文件夹是否存在
            os.makedirs(self.PicturePath)
            print self.PicturePath + "    创建成功！"

    def getUrl_multiTry(self, url):
        """
            功能：爬图类网站源码读取函数
            :参数名    类型          描述
            :self      instance     实例本身
            :url       string       网站地址
        """
        maxTryNum = 10
        html = ""
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

    def GetTheFirstPage(self, url):
        """
            功能：爬图类读取第一层网页图集编号函数
            :参数名    类型          描述
            :self      instance     实例本身
            :url       string       网站地址
        """
        htmlcode = self.getUrl_multiTry(url)
        if htmlcode:
            FirstHtml = re.compile('<a target="_blank" href="(http://.+?\.html)">')
            ID = re.compile('\d{1,8}')
            try:
                FirstHtmls = re.findall(FirstHtml,htmlcode)
                self.FirstPage = FirstHtmls
                print self.FirstPage
                for i in range(0, len(self.FirstPage)):
                    IDs = re.findall(ID, self.FirstPage[i])
                    if IDs[0]+"\n" not in self.Sign:
                        file = open(u"E:\\爬虫图片收集\\唯一网\\sign.txt","a")
                        print self.FirstPage[i]
                        self.GetTheSecondPage(self.FirstPage[i])
                        file.write(IDs[0]+"\n")
                        self.Sign.append(IDs[0]+"\n")
                        print IDs[0] + "Save Success!!!"
                        file.close()
                    else:
                        print "The Same ID" + " " + IDs[0] + ", Jump Out!!!"
            except Exception, err:
                print err
        else:
            print u'网页读取失败！'

    def GetTheSecondPage(self, url):
        """
            功能：爬图类读取第二层网页图片编号函数
            :参数名    类型          描述
            :self      instance     实例本身
            :url       string       网站地址
        """
        htmlcode = self.getUrl_multiTry(url)
        if htmlcode:
            MaxPage = re.compile('<a>共(.*?)页: </a>'.encode('gb2312'))
            MaxPages = re.findall(MaxPage, htmlcode)
            urls = ""
            print MaxPages
            for i in range(1, int(MaxPages[0])+1):
                if i==1:
                    self.DownLoadPicture(url, i)
                else:
                    urls = url.replace(".html", "_%d.html" % i)
                    self.DownLoadPicture(urls, i)
        else:
            print u'网页读取失败！'

    def DownLoadPicture(self, url, number):
        """
            功能：爬图类下载图片函数
            :参数名    类型          描述
            :self      instance     实例本身
            :url       string       网站地址
            :number    int          图片所在图集中的序号
        """
        Link = re.compile(' src="(.+?\.jpg)"')
        HtmlCode = self.getUrl_multiTry(url)
        if HtmlCode:
            Links = re.findall(Link,HtmlCode)
            date = time.strftime('%H-%M-%S',time.localtime(time.time()))
            name = date+"-%d"%number+".jpg"
            savepath = self.PicturePath + "\\" + name
            urllib.urlretrieve(Links[0], savepath)
            print name + ' save success!'
        else:
            print u'网页读取失败！'

    def ReadOldSign(self):
        """
            功能：爬图类读取已下载图集编号函数
            :参数名    类型          描述
            :self      instance     实例本身
        """
        file = open(u"E:\\爬虫图片收集\\唯一网\\sign.txt")
        try:
            OldSign = file.readline()
            while OldSign:
                self.Sign.append(OldSign)
                OldSign = file.readline()
            print self.Sign
        except Exception, err:
            print err
        finally:
            file.close()

    def GetTheAllPhoto(self, url):
        """
            功能：爬图类自动轮番下载所有图集函数
            :参数名    类型          描述
            :self      instance     实例本身
            :url       string       网站第一页地址
        """
        urls=''
        for i in range(1, 599):
            urls = url.replace("_1.html", "_%d.html" % i)
            self.GetTheFirstPage(urls)

if __name__ == '__main__':
    url = "http://www.mmonly.cc/mmtp/list_9_3.html"
    urls = 'http://www.mmonly.cc/mmtp/xgmn/114691_3.html'

    test = DownPhotoAuto()
    test.GetTheAllPhoto("http://www.mmonly.cc/mmtp/list_9_1.html")
