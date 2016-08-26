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
from Tkinter import Tk, Button, mainloop, Frame, YES, X
from Tkinter import *

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
        self.PicturePath = u"E:\\爬虫图片收集\\5422\\图片"         # 图片保存路径
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
            FirstHtml = re.compile('href="(http://www.5442.com/meinv/\d{8}/\d{1,8}\.html)"')
            ID = re.compile('http://www.5442.com/meinv/\d{8}/(.*?).html')
            try:
                FirstHtmls = re.findall(FirstHtml,htmlcode)
                self.FirstPage = FirstHtmls
                print self.FirstPage
                for i in range(0, len(self.FirstPage)):
                    IDs = re.findall(ID, self.FirstPage[i])
                    if IDs[0]+"\n" not in self.Sign:
                        file = open(u"E:\\爬虫图片收集\\5422\\sign.txt","a")
                        print self.FirstPage[i]
                        self.GetTheSecondPage(self.FirstPage[i])
                        file.write(IDs[0]+"\n")
                        self.Sign.append(IDs[0]+"\n")
                        print IDs[0] + "  Save Success!!!"
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
        Link = re.compile('<img src=\'(.+?\.jpg)\'')
        HtmlCode = self.getUrl_multiTry(url)
        if HtmlCode:
            Links = re.findall(Link,HtmlCode)
            date = time.strftime('%H-%M-%S',time.localtime(time.time()))
            if len(Links) > 1:
                for i in range(0, len(Links)):
                    name = date + "-%d" % number + "-%d" % i + ".jpg"
                    savepath = self.PicturePath + "\\" + name
                    urllib.urlretrieve(Links[i], savepath)
                    print name + ' save success!'
            elif len(Links)==1:
                name = date+"-%d" %number+".jpg"
                savepath = self.PicturePath + "\\" + name
                urllib.urlretrieve(Links[0], savepath)
                print name + ' save success!'
            else:
                pass
        else:
            print u'网页读取失败！'

    def ReadOldSign(self):
        """
            功能：爬图类读取已下载图集编号函数
            :参数名    类型          描述
            :self      instance     实例本身
        """
        if not os.path.exists(u"E:\\爬虫图片收集\\5422\\sign.txt"):
            file = open(u"E:\\爬虫图片收集\\5422\\sign.txt",'w')
            file.close()
        file = open(u"E:\\爬虫图片收集\\5422\\sign.txt")
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
        urls = ''
        for i in range(1, 494):
            urls = url.replace("_1.html", "_%d.html" % i)
            print u'读取第%d页'%i
            self.GetTheFirstPage(urls)

class SearchAimData(Frame):
    """
        搜索目标文件，有则打开，找不到则提示不存在
    """
    def __init__(self, master):
        """
            功能:初始化
            :参数名    类型          描述
            :self      instance     实例本身
            :master    instance     父控件对象
        """
        Frame.__init__(self)
        self.initGUI()
        self.PicturePath = u"E:\\爬虫图片收集\\5422\\图片"         # 图片保存路径
        self.FirstPage = []                                          # 图集编号所处第一层网页列表
        self.Sign = []                                               # 下载过的图集编号列表
        self.DirectoryCreate()                                       # 调用文件夹检测存在及创建函数
        self.ReadOldSign()                                           # 调用读取已下载图集编号函数

    def initGUI(self):
        """
            初始化界面
        """
        # self.win = Tk()
        # self.win.title('下图系统')
        # self.win.geometry('470x500')

        self.btn = Button(self, text='点击下载', command=self.process)
        self.pause = Button(self, text='点击暂停', command=self.click)
        self.txt = Text(self)
        self.txt.pack()
        self.btn.pack()
        self.pause.pack()
        self.pack(side=TOP, fill=X)
        # self.win.mainloop()

    def process(self):
        '''
            处理点击事件,开始查找匹配
        '''
        self.GetTheAllPhoto('http://www.5442.com/meinv/list_1_1.html')

    def click(self):
        os.system("pause")

    def DirectoryCreate(self):
        if not os.path.exists(self.PicturePath):                   # 判断文件夹是否存在
            os.makedirs(self.PicturePath)
            self.txt.insert(END, self.PicturePath + "    创建成功！\n")
            self.txt.update()
            self.txt.see(END)

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
                if tries < (maxTryNum-1):
                    continue
                else:
                    self.txt.insert(END, "Has tried %d times to access url %s, all failed!\n", maxTryNum, url)
                    self.txt.update()
                    self.txt.see(END)
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
            FirstHtml = re.compile('href="(http://www.5442.com/meinv/\d{8}/\d{1,8}\.html)"')
            ID = re.compile('http://www.5442.com/meinv/\d{8}/(.*?).html')
            try:
                FirstHtmls = re.findall(FirstHtml, htmlcode)
                self.FirstPage = FirstHtmls
                self.txt.insert(END, self.FirstPage)
                self.txt.insert(END, '\n')
                self.txt.update()
                self.txt.see(END)
                for i in range(0, len(self.FirstPage)):
                    IDs = re.findall(ID, self.FirstPage[i])
                    if IDs[0]+"\n" not in self.Sign:
                        file = open(u"E:\\爬虫图片收集\\5422\\sign.txt","a")
                        self.txt.insert(END, self.FirstPage[i]+"\n")
                        self.txt.update()
                        self.txt.focus_force()
                        self.GetTheSecondPage(self.FirstPage[i])
                        file.write(IDs[0]+"\n")
                        self.Sign.append(IDs[0]+"\n")
                        self.txt.insert(END, IDs[0] + "  Save Success!!!\n")
                        self.txt.update()
                        self.txt.see(END)
                        file.close()
                    else:
                        self.txt.insert(END, "The Same ID" + " " + IDs[0] + ", Jump Out!!!\n")
                        self.txt.update()
                        self.txt.see(END)

            except Exception, err:
                self.txt.insert(END, err)
                self.txt.update()
                self.txt.focus_force()
        else:
            self.txt.insert(END, u'网页读取失败！\n')
            self.txt.update()
            self.txt.see(END)

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
            self.txt.insert(END, MaxPages[0]+'\n')
            self.txt.update()
            self.txt.see(END)
            for i in range(1, int(MaxPages[0])+1):
                if i==1:
                    self.DownLoadPicture(url, i)
                else:
                    urls = url.replace(".html", "_%d.html" % i)
                    self.DownLoadPicture(urls, i)
        else:
            self.txt.insert(END, u'网页读取失败！\n')
            self.txt.update()
            self.txt.see(END)

    def DownLoadPicture(self, url, number):
        """
            功能：爬图类下载图片函数
            :参数名    类型          描述
            :self      instance     实例本身
            :url       string       网站地址
            :number    int          图片所在图集中的序号
        """
        Link = re.compile('<img src=\'(.+?\.jpg)\'')
        HtmlCode = self.getUrl_multiTry(url)
        if HtmlCode:
            Links = re.findall(Link,HtmlCode)
            date = time.strftime('%H-%M-%S', time.localtime(time.time()))
            if len(Links) > 1:
                for i in range(0, len(Links)):
                    name = date + "-%d" % number + "-%d" % i + ".jpg"
                    savepath = self.PicturePath + "\\" + name
                    urllib.urlretrieve(Links[i], savepath)
                    self.txt.insert(END, name + ' save success!\n')
                    self.txt.update()
                    self.txt.see(END)

            elif len(Links) == 1:
                name = date+"-%d" %number+".jpg"
                savepath = self.PicturePath + "\\" + name
                urllib.urlretrieve(Links[0], savepath)
                self.txt.insert(END, name + ' save success!\n')
                self.txt.update()
                self.txt.see(END)
            else:
                pass
        else:
            self.txt.insert(END, u'网页读取失败！\n')
            self.txt.update()
            self.txt.see(END)

    def ReadOldSign(self):
        """
            功能：爬图类读取已下载图集编号函数
            :参数名    类型          描述
            :self      instance     实例本身
        """
        if not os.path.exists(u"E:\\爬虫图片收集\\5422\\sign.txt"):
            file = open(u"E:\\爬虫图片收集\\5422\\sign.txt",'w')
            file.close()
        file = open(u"E:\\爬虫图片收集\\5422\\sign.txt")
        try:
            OldSign = file.readline()
            while OldSign:
                self.Sign.append(OldSign)
                OldSign = file.readline()
            self.txt.insert(END, self.Sign)
            self.txt.insert(END, '\n')
            self.txt.update()
            self.txt.see(END)
        except Exception, err:
            self.txt.insert(END, err)
            self.txt.update()
            self.txt.see(END)
        finally:
            file.close()

    def GetTheAllPhoto(self, url):
        """
            功能：爬图类自动轮番下载所有图集函数
            :参数名    类型          描述
            :self      instance     实例本身
            :url       string       网站第一页地址
        """
        urls = ''
        for i in range(1, 494):
            urls = url.replace("_1.html", "_%d.html" % i)
            self.txt.insert(END, u'读取第%d页\n'%i)
            self.txt.update()
            self.txt.see(END)
            self.GetTheFirstPage(urls)

if __name__ == "__main__":
    url = 'http://www.5442.com/meinv/list_1_1.html'
    urls = 'http://www.5442.com/meinv/20160715/33692_1.html'

    root = Tk()
    root.title('爬图软件')
    SearchAimData(root)
    root.mainloop()

