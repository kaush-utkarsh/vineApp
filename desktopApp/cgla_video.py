import wx
import urllib
import urllib2
from cookielib import CookieJar
import time
from threading import Thread
import os
import xml.etree.ElementTree as ET
import os.path
import datetime
import os
import json

base_api_url = "http://54.85.157.242:5000/api/"
login_url = base_api_url + "login"
get_videos_url = base_api_url + "getvideos"
video_downloaded_url = base_api_url + "videodownloaded/"

class MyFrame(wx.Frame):

    def __init__(self, parent, id, title):
        print os.getcwd()
        #exeName = win32api.GetModuleFileName(win32api.GetModuleHandle(None))
        wx.Frame.__init__(self, parent, id, title)
        favicon = wx.Icon('logo_CG_Social.jpg',wx.BITMAP_TYPE_JPEG)
        self.SetIcon(favicon)
        self.dirpath = ""
        self.pathFilename = "dirPath.txt"
        self.fileSequenceName = "fileSeqno.txt"
        self.fileSequenceNo = 1
        id=wx.NewId()
        self.panel = wx.Panel(self, -1)
        jpg1 = wx.Image("logo.gif", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        # bitmap upper left corner is in the position tuple (x, y) = (5, 5)
        wx.StaticBitmap(self, -1, jpg1, (60, 30), (550, 50))
        self.panel.SetBackgroundColour('Light Gray')
        label1 = wx.StaticText(self.panel, -1, "Email:")
        label2 = wx.StaticText(self.panel, -1, "Password:")
        self.Email = wx.TextCtrl(self.panel, -1, "")
        self.Password = wx.TextCtrl(self.panel, -1, "")
        self.calc_btn = wx.Button(self.panel, -1, ' Login ')
        self.calc_btn.Bind(wx.EVT_BUTTON, self.login)


        # use gridbagsizer for layout of widgets
        sizer = wx.GridBagSizer(vgap=10, hgap=10)
        sizer.Add(label1, pos=(0, 0))
        sizer.Add(self.Email, pos=(0, 2))  # row 0, column 2
        sizer.Add(label2, pos=(1, 0))
        sizer.Add(self.Password, pos=(1, 2))
        sizer.Add(self.calc_btn, pos=(2, 1), span=(1, 2))
        border = wx.BoxSizer()
        border.Add(sizer, 0, wx.ALL, 225)
        self.panel.SetSizerAndFit(border)
        self.Fit()

        self.cj = CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))

    def send_request(self, url, data = None):
        if data:
            data = urllib.urlencode(data)
        response = self.opener.open(url, data)
        return json.loads(response.read())

    def login(self, event):
        login_thread = Thread(target = self.login_check)
        login_thread.start()

    def login_check(self):
        creds = {"email": self.Email.GetValue(), "password": self.Password.GetValue()}
        wx.CallAfter(self.makeList, self.send_request(login_url, creds).get("response", -1))

    def makeList(self, success):
        if success > 0:
            self.getDirPath()
            for child in self.panel.GetChildren():
                child.Destroy()
            cbtn = wx.Button(self.panel, label='Change Directory', pos=(60, 100), size=(130, -1))
            cbtn.Bind(wx.EVT_BUTTON, self.OnChange)
            cbtn = wx.Button(self.panel, label='Clear Log File', pos=(200, 100))
            cbtn.Bind(wx.EVT_BUTTON, self.OnClear)

            filedirpath = wx.StaticText(self.panel, -1, "Current Directory Path:", pos=(60,140))
            self.pathText = wx.TextCtrl(self.panel, -1, str(self.dirpath), pos=(200,140), size=(360, -1))
            self.result = wx.TextCtrl(self.panel, -1, size=(500, 250), style=wx.TE_MULTILINE, pos=(60,180))
            self.result.SetBackgroundColour('Black')
            self.timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.update, self.timer)
            self.SetSize((675, 500))
            self.SetTitle("")
            self.Show(True)
            self.OnDownload()
        else:
            self.SetTitle("Incorrect User details entered")

    def ShowOrHideTitle(self, e):
        sender = e.GetEventObject()
        isChecked = sender.GetValue()

        if isChecked:
            self.checkedVideos.append(self.cb.GetLabel())
        else:
            self.SetTitle('')

    def OnClear(self, e):
        self.result.SetValue("")

    def onEnter(self, event):
        # get the values from the input widgets
        Email = str(self.Email.GetValue())
        Password = float(self.Password.GetValue())

        self.Email.Clear()
        self.Password.Clear()
        cursor.close()

    def OnCloseMe(self, event):
        self.Close(True)

    def OnCloseWindow(self, event):
        self.Destroy()

    def change_directory(self):
        dialog = wx.DirDialog(None, "Choose a directory:",style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            print dialog.GetPath()
            dialog.Destroy()
            self.dirpath = dialog.GetPath() + "\\"
            self.writeDirPathToFile()
            self.pathText.SetValue(self.dirpath)

    def OnChange(self, e):
        self.change_directory()

    def writeDirPathToFile(self):
        fo = open(self.pathFilename, "w")
        fo.write(self.dirpath)
        fo.close()

    def getDirPath(self):
        if (os.path.exists(self.pathFilename)):
            with open(self.pathFilename) as fp:
                for line in fp:
                    self.dirpath = line
        else:
            self.change_directory()


    def update(self, event):
        if not hasattr(self, 'processing_thread') or not self.processing_thread.is_alive():
            self.processing_thread = Thread(target = self.startProcessing)
            self.processing_thread.start()

    def startProcessing(self):
        self.getVideos()
        for recordDict in self.videosList:
            # print self.videosList
            dest_path = self.dirpath + recordDict["prefix"]
            recordDict["video_filename"] = dest_path + "." + recordDict["video"].split("/")[-1].split("?")[0].split(".")[-1]
            recordDict["avatar_filename"] = dest_path + "." + recordDict["avatar"].split("/")[-1].split("?")[0].split(".")[-1]
            recordDict["xml_filename"] = dest_path + ".xml"
            recordDict["mov_filename"] = dest_path + ".mov"
            recordDict["wav_filename"] = dest_path + ".wav"
            self.downloadFiles(recordDict)
            self.result.SetForegroundColour("White")
            self.pos_y = self.pos_y + 20
            self.markVideosAsDownloaded(recordDict["video_id"])

    def OnDownload(self):
        self.getDirPath()
        self.pos_y = 180
        self.timer.Start(3000)

    def convertFiles(self,recordDict):
        # print "recordDict[standard]", recordDict["standard"]
        os.system("ffmpeg -y -i " + recordDict["video_filename"] + " -acodec pcm_s16le -ar 48000 -ac 2 -vol 0 -vcodec mjpeg -qscale:v 1 -qscale:a 1 -r " + str(recordDict["standard"])+ " " + recordDict["mov_filename"])
        self.result.AppendText(self.getCurrentTime() + "    " + recordDict["mov_filename"] + "    Converted" +  "\n")
        os.system("ffmpeg -y -i " + recordDict["video_filename"] + " -acodec pcm_s16le -ar 48000 -ac 2 -vcodec mjpeg -qscale:v 1 -qscale:a 1 -r " + str(recordDict["standard"]) + " " + recordDict["wav_filename"])
        self.createXML(recordDict)

    def getCurrentTime(self):
        return datetime.datetime.now().strftime('%H:%M:%S %b %d %Y')

    def downloadFiles(self,recordDict):
        f = urllib2.urlopen(recordDict["video"])
        data = f.read()
        with open(recordDict["video_filename"], "wb") as code:
            code.write(data)
        f = urllib2.urlopen(recordDict["avatar"])
        self.result.AppendText(self.getCurrentTime() + "    " + recordDict["video_filename"] + "    Downloaded" +  "\n")
        data = f.read()
        with open(recordDict["avatar_filename"], "wb") as code:
            code.write(data)
        self.Show(True)
        thread = Thread(target = self.convertFiles, args = (recordDict, ))
        thread.start()
        #self.convertFiles(recordDict)

    def getVideos(self):
        self.videosList = self.send_request(get_videos_url)

    def markVideosAsDownloaded(self, video_id):
        self.send_request(video_downloaded_url + str(video_id))

    def createXML(self, recordDict):
        post = ET.Element("post")

        site = ET.SubElement(post, "site")
        site.text = recordDict["site"]

        user = ET.SubElement(post, "user")

        UName = ET.SubElement(user, "UName")
        UName.text = recordDict["uName"]

        UID = ET.SubElement(user, "UID")
        UID.text = recordDict["uId"]

        fullname = ET.SubElement(user, "fullname")
        fullname.text = ""

        date = ET.SubElement(post, "date")
        date.text = recordDict["date"]

        ttext = ET.SubElement(post, "text")
        ttext.text = recordDict["text"]

        param = ET.SubElement(post, "param")
        param.text = ""

        video = ET.SubElement(post, "video")
        video.text = recordDict["video"]

        avatar = ET.SubElement(post, "avatar")
        avatar.text = recordDict["avatar_filename"]

        avpath = ET.SubElement(post, "avpath")
        avpath.text = ""

        videoparams = ET.SubElement(post, "videoparams")
        videoparams.text = ""

        vcrt = ET.SubElement(post, "vcrt")
        vcrt.text = ""

        tree = ET.ElementTree(post)
        tree.write(recordDict["xml_filename"])


app = wx.App()
frame = MyFrame(None, -1, "Login")
frame.Show()
app.MainLoop()

