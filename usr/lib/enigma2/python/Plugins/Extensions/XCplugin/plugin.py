#25.06.2019
#######################
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#by ))^^(( & MMark -thanks aime_jeux and other friends
#for convertion bouquet credits 
#Thanks to @author: Dave Sully, Doug Mackay
#for use e2m3u2bouquet.e2m3u2bouquet -- Enigma2 IPTV m3u to bouquet parser
#@copyright:  2017 All rights reserved.
#@license:    GNU GENERAL PUBLIC LICENSE version 3
#@deffield  
#CONVERT TEAM TO ALL FAVORITES LIST MULTIVOD + EPG
# Open the epgimporter plugin via extension's menu.
# Press the blue button to select the sources.
# Select the entry e2m3uBouquet and press the OK button
# Save it with the green button
# Run a manual import using the yellow button manual.
# Save the input with the green button.
# After a while should you the events imported.
# It takes a while so be patient.
########################################


from enigma import *
from Components.ActionMap import ActionMap, HelpableActionMap, NumberActionMap
from Components.AVSwitch import AVSwitch
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import *
from Components.Console import Console as iConsole
from Components.Converter.StringList import StringList
from Components.FileList import FileList   
from Components.Input import Input
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.Pixmap import Pixmap
from Components.PluginComponent import plugins
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.ServiceList import ServiceList
from Components.Sources.List import List
from Components.Sources.Progress import Progress
from Components.Sources.Source import Source
from Components.Sources.StaticText import StaticText
from Components.Task import Task, Job, job_manager as JobManager, Condition
from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console
from Screens.InfoBar import MoviePlayer, InfoBar
from Screens.InfoBarGenerics import *
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from Screens.MovieSelection import MovieSelection
from Screens.Screen import Screen
from Screens.Standby import Standby,TryQuitMainloop
from Screens.TaskView import JobView
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools import Notifications, ASCIItranslit
from Tools.BoundFunction import boundFunction
from Tools.Directories import fileExists, copyfile, pathExists
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap
from datetime import datetime, date
from os import environ as SetValue, getenv as ReturnValue
from os import environ, listdir, path, readlink, system, rename
from twisted.web.client import downloadPage #, getPage, http
from urllib import quote_plus
from xml.etree.cElementTree import fromstring, ElementTree
import xml.etree.cElementTree
import base64
import hashlib
import os, re, glob
import socket
import gettext
import sys
import urllib
import urllib as ul
import urllib2
import time

from Components.config import config, ConfigSelection, getConfigListEntry, NoSave, ConfigText, ConfigDirectory
from Components.ConfigList import *
from Screens.LocationBox import LocationBox


global nochange
nochange = False

# VERSION
version=" 2.1"
currversion = '2.1'
namefolder='XC-Lite'
descriptionplug='XtreamCode Lite Version '


# SETTINGS
PLUGIN_PATH = '/usr/lib/enigma2/python/Plugins/Extensions/XCplugin'
patch_e2m3u2bouquet = PLUGIN_PATH + '/bouquet/'
SKIN_PATH = PLUGIN_PATH
HD = getDesktop(0).size()
BRAND = '/usr/lib/enigma2/python/boxbranding.so'
BRANDP = '/usr/lib/enigma2/python/Plugins/PLi/__init__.pyo'
BRANDPLI ='/usr/lib/enigma2/python/Tools/StbHardware.pyo'
VIDEO_FMT_PRIORITY_MAP = {'38': 1, '37': 2, '22': 3, '18': 4, '35': 5, '34': 6}
NTIMEOUT = 10
socket.setdefaulttimeout(NTIMEOUT)

#tmdb
filterlist = PLUGIN_PATH + '/cfg/filterlist.txt'        
if os.path.isfile(filterlist):
    global filtertmdb
    try:
        with open(filterlist) as f:
            lines = [line.rstrip('\n') for line in open(tmdblist)]
            start = ('": ' + '"' + '",' + ' "')
            mylist = start.join(lines)
            end = ('{"' + mylist + '": ' + '"' + '"' + "}")

            dict = eval(filtertmdb)
            filtertmdb = "".join( end.splitlines())
            
            filtertmdb = dict
    except:

        filtertmdb = {'x264': '', '1080p': '', '1080i': '', '720p': '', 'VOD': '', 'vod': '', 'Ac3-evo': '', 'Hdrip': '', 'Xvid': ''}

#frossie	:CLEAN EPG WORD	
def charRemove(text):
        char = ['1080p',
		 '2018',
		 '2019',
		 '2020',
         '480p',
         '4K',
         '720p',
         'ANIMAZIONE',
         'APR',
         'AVVENTURA',
         'BIOGRAFICO',
		 'BDRip',
         'BluRay',
         'CINEMA',
         'COMMEDIA',
         'DOCUMENTARIO',
         'DRAMMATICO',		 
         'FANTASCIENZA',
         'FANTASY',
		 'FEB',
         'GEN',
		 'GIU',
         'HDCAM',
         'HDTC',
         'HDTS',
         'LD',			 
         'MAFIA',
         'MAG',
         'MARVEL',
		 'MD',
         'ORROR',	
		 'NEW_AUDIO',
         'POLIZ',	
         'R3',
		 'R6',
         'SD',
         'SENTIMENTALE',
		 'TC',
         'TEEN',
         'TELECINE',
         'TELESYNC',
		 'THRILLER',
		 'Uncensored',
		 'V2',
         'WEBDL',
         'WEBRip',
		 'WEB',
         'WESTERN',
		 '-',
		 '_',
		 '.',
		 '+',
         '[',
         ']']
		 
        myreplace = text
        for ch in char:
            myreplace = myreplace.replace(ch, '').replace('  ', ' ').replace('   ', ' ').strip()
        return myreplace
		
		
#
def ReloadBouquet():
    eDVBDB.getInstance().reloadServicelist()
    eDVBDB.getInstance().reloadBouquets() 

#
def isExtEplayer3Available():
    return os.path.isfile(eEnv.resolve('$bindir/exteplayer3'))

#
def isGstPlayerAvailable():
    return os.path.isfile(eEnv.resolve('$bindir/gst-launch-1.0'))

#
def OnclearMem():
        system("sync")
        system("echo 3 > /proc/sys/vm/drop_caches")

#        
def remove_line(filename, what):
    if os.path.isfile(filename):
        file_read = open(filename).readlines()
        file_write = open(filename, 'w')
        for line in file_read:
            if what not in line:
                file_write.write(line)
        file_write.close()

try:
	import servicewebts
	print 'OK servicewebts'
except Exception as ex:
	print ex
	print 'ERROR servicewebts'
        
# #
# def mountm3uf():
    # pthm3uf = []
    # if os.path.isfile('/proc/mounts'):
        # for line in open('/proc/mounts'):
# #            if '/dev/sd' in line or '/dev/disk/by-uuid/' in line or '/dev/mmc' in line or '/dev/mtdblock' in line:
            # if '/dev/sd' in line or '/dev/disk/by-uuid/' in line or '/dev/mmc' in line or '/dev/mtdblock' in line:
                # drive = line.split()[1].replace('\\040', ' ') + '/'
                # if drive== "/media/hdd/" :
                    # drive = drive.replace('/media/hdd/', '/media/hdd/xc')
                    # if not os.path.exists('/media/hdd/xc'):
                        # system('mkdir /media/hdd/xc')
                # if drive== "/media/usb/" :
                    # drive = drive.replace('/media/usb/', '/media/usb/xc')
                    # if not os.path.exists('/media/usb/xc'):
                        # system('mkdir /media/usb/xc')                    
                # if drive== "/omb/" :
                    # drive = drive.replace('/media/omb/', '/media/omb/')
                    # if not os.path.exists('/media/omb/xc'):
                        # system('mkdir /media/omb/xc')                     
                # if drive== "/media/ba/" :
                    # drive = drive.replace('/media/ba/', '/media/ba/')   
                    # if not os.path.exists('/media/ba/xc'):
                        # system('mkdir /media/ba/xc')  
                        
                # if not drive in pthm3uf:
                    # pthm3uf.append(drive)
    # system('mkdir /etc/enigma2/xc')
    # pthm3uf.append('/etc/enigma2/xc')
    # return pthm3uf


# def mount_movie():
    # pthmovie = []
    # if os.path.isfile('/proc/mounts'):
        # for line in open('/proc/mounts'):
# #x nas suspend  if '/dev/sd' in line or '/dev/disk/by-uuid/' in line or '/dev/mmc' in line or '/dev/mtdblock' in line:
            # if '/dev/sd' in line or '/dev/disk/by-uuid/' in line or '/dev/mmc' in line or '/dev/mtdblock' in line:
                # drive = line.split()[1].replace('\\040', ' ') + '/'
                # if drive== "/media/hdd/" :
                    # if not os.path.exists('/media/hdd/movie'):
                        # system('mkdir /media/hdd/movie')

                # if drive== "/media/usb/" :
                    # if not os.path.exists('/media/usb/movie'):
                        # system('mkdir /media/usb/movie')                    

                # if drive== "/media/omb/" :
                    # drive = drive.replace('/media/omb/', '/media/omb/')
                    # if not os.path.exists('/media/omb/movie'):
                        # system('mkdir /media/omb/movie')                     

                # if drive== "/media/ba/" :
                    # drive = drive.replace('/media/ba/', '/media/ba/')   
                    # if not os.path.exists('/media/ba/movie'):
                        # system('mkdir /media/ba/movie') 
                # if not drive in pthmovie:
                    # pthmovie.append(drive)
    # system('mkdir /tmp/movie')
    # pthmovie.append('/tmp/')    
    # if os.path.exists('/media/net/NAS'):    
        # pthmovie.append('/media/net/NAS') 
		
		
	# #jogistyle	
    # if os.path.exists('/media/net/autonet/FRITZNAS/hddnas/movie'):    
        # pthmovie.append('/media/net/autonet/FRITZNAS/hddnas') 		
		
		
    # return pthmovie    


# def mount_picon():
    # pthpicon = []
    # if os.path.isfile('/proc/mounts'):
        # for line in open('/proc/mounts'):
            # if '/dev/sd' in line or '/dev/disk/by-uuid/' in line or '/dev/mmc' in line or '/dev/mtdblock' in line:
                # drive = line.split()[1].replace('\\040', ' ') + '/'

                # if drive== "/media/hdd/" :
                    # drive = drive.replace('/media/hdd/', '/media/hdd/picon/')
                    # if not os.path.exists('/media/hdd/picon'):
                        # system('mkdir /media/hdd/picon')

                # if drive== "/media/usb/" :
                    # drive = drive.replace('/media/usb/', '/media/usb/picon/')
                    # if not os.path.exists('/media/usb/picon'):
                        # system('mkdir /media/usb/picon')                    

                # if not drive in pthpicon: 
                    # pthpicon.append(drive)

    # pthpicon.append('/picon/')        
    # pthpicon.append('/usr/share/enigma2/picon/')
    # return pthpicon       
   
    
# CONFIG
config.plugins.XCplugin = ConfigSubsection()
config.plugins.XCplugin.hostaddress = ConfigText(default = "exampleserver.com:8888")
config.plugins.XCplugin.user = ConfigText(default = "Enter Username", visible_width = 50, fixed_size = False)
config.plugins.XCplugin.passw = ConfigPassword(default = "******", fixed_size = False, censor = '*')
# config.plugins.XCplugin.user = NoSave(ConfigText(default = "Enter Username", visible_width = 50, fixed_size = False))
# config.plugins.XCplugin.passw = NoSave(ConfigPassword(default = "******", fixed_size = False, censor = '*'))

if os.path.exists ('/usr/lib/enigma2/python/Plugins/SystemPlugins/ServiceApp') and isExtEplayer3Available :
    config.plugins.XCplugin.services = ConfigSelection(default='Gstreamer', choices=['Gstreamer', 'Exteplayer3'])
else:
    config.plugins.XCplugin.services = ConfigSelection(default='Gstreamer', choices=[('Gstreamer')])
config.plugins.XCplugin.typelist = ConfigSelection(default='Multi Live & VOD', choices=['Multi Live & VOD', 'Multi Live/Single VOD', 'Combined Live/VOD' ])    
config.plugins.XCplugin.bouquettop = ConfigSelection(default='Bottom', choices=['Bottom', 'Top'])
config.plugins.XCplugin.picons = ConfigYesNo(default=False)
# config.plugins.XCplugin.pthpicon = ConfigSelection(choices = mount_picon())
# config.plugins.XCplugin.pthmovie = ConfigSelection(choices = mount_movie())
# config.plugins.XCplugin.pthxmlfile = ConfigSelection(default='/etc/enigma2/xc', choices=['/etc/enigma2/xc', '/media/hdd/xc', '/media/usb/xc'])
config.plugins.XCplugin.pthpicon = ConfigDirectory(default = '/media/usb/picon')
config.plugins.XCplugin.pthmovie = ConfigDirectory(default='/media/usb/movie')
config.plugins.XCplugin.pthxmlfile = ConfigDirectory(default='/etc/enigma2/xc')
config.plugins.XCplugin.typem3utv = ConfigSelection(default = "MPEGTS to TV", choices = ["M3U to TV","MPEGTS to TV"])
config.plugins.XCplugin.strtmain = ConfigYesNo(default=True)
config.plugins.XCplugin.LivePlayer = ConfigYesNo(default=True)



# SCREEN PATH SETTING
iconpic = PLUGIN_PATH + '/plugin.png' #cvs
if HD.width() > 1280:
    CHANNEL_NUMBER = [3, 7, 60, 50, 0]
    CHANNEL_NAME = [70, 7, 1500, 50, 1]
    FONT_0 = ('Regular', 32)
    FONT_1 = ('Regular', 32)
    BLOCK_H = 50
    SKIN_PATH = PLUGIN_PATH + '/skin/fhd'
    if fileExists(BRAND) or fileExists(BRANDP):   
        iconpic = SKIN_PATH + '/plugin.png'

else:
    CHANNEL_NUMBER = [3, 5, 40, 40, 0]
    CHANNEL_NAME = [55, 5, 900, 40, 1]
    FONT_0 = ('Regular', 20)
    FONT_1 = ('Regular', 20)
    BLOCK_H = 30
    SKIN_PATH = PLUGIN_PATH + '/skin/hd'
    if fileExists(BRAND) or fileExists(BRANDP):   
        iconpic = SKIN_PATH + '/plugin.png'
   
#
global piclogo, pictmp, xmlname, urlinfo
piclogo = SKIN_PATH + '/iptvlogo.jpg'
pictmp = '/tmp/poster.jpg'
urlinfo = ''
xmlname = ''

def clear_img():
    if fileExists('/tmp/poster.jpg'):
        debug('DELETE .JPG')
        path = '/tmp'

        cmd = 'rm -f %s/*.jpg' % path
        debug(cmd, 'CMD')
        try:
            status = os.popen(cmd).read()
            debug(status, 'delete 1')
            system("cd / && cp -f " + piclogo + ' /tmp/poster.jpg')        

        except Exception as ex:
            print ex
            print 'ex delete 1'
            try:
                result = commands.getoutput(cmd)
                debug(result, 'delete 2')
            except Exception as ex:
                print ex
                print 'ex delete 2'

system("cd / && cp -f " + piclogo + ' /tmp/poster.jpg')
global PICONSPATH
PICONSPATH = config.plugins.XCplugin.pthpicon.value

#for aime_jeux    
Path_Movies = config.plugins.XCplugin.pthmovie.value #+'movie/'
Path_XML = config.plugins.XCplugin.pthxmlfile.value #+ '/'


# CONFIG XC
class xc_config(Screen, ConfigListScreen):
        def __init__(self, session):

                if fileExists(BRAND) or fileExists(BRANDP):
                   skin = SKIN_PATH + '/xc_config_open.xml'
                else:
                   skin = SKIN_PATH + '/xc_config.xml'
                f = open(skin, 'r')
                self.skin = f.read()
                f.close()        
                Screen.__init__(self, session)
                self.setup_title = _("XtreamCode-Config")
                self.onChangedEntry = [ ]
                self.session = session				
                self["key_blu"] = Label(_("User Files")) 
                self['key_yellow'] = Label(_("Import") + " Server")
                self['key_yellow'].hide()
                info = ''
                self.downloading = False                 
                self['info2'] = Label(info)
                self['Helplab'] = Label(_("Help"))             
                self['playlist'] = Label()
                self['version'] = Label(_(' V.%s Lite' % version)) 
                self["description"] = Label(_(' '))
                self["key_red"] = Label(_("Back"))
                self["key_green"] = Label(_("Save"))
                self["actions"] =ActionMap(['setupActions', 'HelpActions', 'OkCancelActions', 'DirectionActions', 'ColorActions', 'VirtualKeyboardActions', 'ActiveCodeActions','InfobarChannelSelection'],
                {
                        "red": self.extnok,
                        # "0": self.iptv_sh,
                        "cancel": self.extnok,
                        "left": self.keyLeft,
                        "right": self.keyRight,
                        'help': self.help,
                        # 'yellow': self.ImportInfosServer,#ADD  
                        'yellow': self.iptv_sh,#ADD                         
                        "green": self.cfgok,
                        "blue":self.Team,
                        'showVirtualKeyboard': self.KeyText,
                        # "ok": self.Ok_edit
                        "ok": self.ok						
						
                }, -1)		
                self.list = []				
                ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)				
                self.createSetup() 
                self.showhide()                
                self.ConfigText() 
                self.onLayoutFinish.append(self.layoutFinished)
				
        def iptv_sh(self):        
            self.session.openWithCallback(self.importIptv_sh, MessageBox, _('Import Your Server iptv.sh?') , type=MessageBox.TYPE_YESNO, timeout = 10, default = False)
      
        def importIptv_sh(self, result):
            if result:
                iptvsh = '/etc/enigma2/iptv.sh'
                if fileExists(iptvsh):            
                    # if config.plugins.XCplugin.hostaddress.value == 'exampleserver.com:8888' :    
                    f1 = open(iptvsh, 'r+')
                    fpage = f1.read()
                    print fpage
                    regexcat = 'USERNAME="(.*?)".*?PASSWORD="(.*?)".*?url="http://(.*?)/get.php.*?'
                    match = re.compile(regexcat, re.DOTALL).findall(fpage)
                    for usernamesh, passwordsh, urlsh in match:
                            print 'URL: ', urlsh 
                            print 'USERNAME: ', usernamesh
                            print 'PASSWORD: ', passwordsh 
                            urlsh = urlsh.replace('"', '')
                            usernamesh = usernamesh.replace('"', '')
                            passwordsh = passwordsh.replace('"', '')
                            print 'urlsh: ', urlsh 
                            print 'usernamesh: ', usernamesh
                            print 'passwordsh: ', passwordsh                     
                            config.plugins.XCplugin.hostaddress.setValue(urlsh)
                            config.plugins.XCplugin.user.setValue(usernamesh)
                            config.plugins.XCplugin.passw.setValue(passwordsh) 
                            print 'host ', config.plugins.XCplugin.hostaddress.value 
                            
                    xtream_e2portal_url = 'http://' + config.plugins.XCplugin.hostaddress.value + '/enigma2.php'   #con config.value
                    username = config.plugins.XCplugin.user.value  #con config.value
                    password = config.plugins.XCplugin.passw.value  #con config.value
                
                    filesave = 'xc_' + config.plugins.XCplugin.user.value + '.xml' 
                    filesave = filesave.replace(':','_')
                    filesave = filesave.lower()
                    pth= config.plugins.XCplugin.pthxmlfile.value 
                    print 'pth:', pth                
                    f5 = open(pth + filesave, "w") 
                    f5.write(str('<?xml version="1.0" encoding="UTF-8" ?>\n' + '<items>\n' + '<plugin_version>' + currversion + '</plugin_version>\n' +'<xtream_e2portal_url><![CDATA[http://'+ config.plugins.XCplugin.hostaddress.value + '/enigma2.php]]></xtream_e2portal_url>\n' + '<username>' + config.plugins.XCplugin.user.value + '</username>\n' + '<password>' + config.plugins.XCplugin.passw.value + '</password>\n'+ '</items>'))
                    f5.close()  
                    self.ConfigText()                    
                else:
                    self.mbox = self.session.open(MessageBox, (_('Missing %s !') % iptvsh), MessageBox.TYPE_INFO, timeout=4)                    

        #
        def layoutFinished(self):
            self.setTitle(self.setup_title)
              

        def help(self):
            self.session.open(xc_help)
        
        #
        def createSetup(self):
            global xmlname
            self.editListEntry = None
            self.list = []
            indent = '- '
            xmlname = ''
            self.list.append(getConfigListEntry(_("Link in Main Menu  "), config.plugins.XCplugin.strtmain, _("Display XCplugin in Main Menu")))            
            self.list.append(getConfigListEntry(_('Server URL'), config.plugins.XCplugin.hostaddress, _("Enter Server_Url:Port without 'http://' your_domine:8000"))) 
            self.list.append(getConfigListEntry(_('Server Username'), config.plugins.XCplugin.user, _("Enter Username"))) 
            self.list.append(getConfigListEntry(_('Server Password'), config.plugins.XCplugin.passw, _("Enter Password"))) 
            xmlname = config.plugins.XCplugin.hostaddress.value
            self.list.append(getConfigListEntry(_("Services Type"), config.plugins.XCplugin.services, _("Configure service Reference Gstreamer or Exteplayer3")))
            self.list.append(getConfigListEntry(_("LivePlayer Active "), config.plugins.XCplugin.LivePlayer, _("Live Player for Stream .ts: set No for Record Live")))     
            self.list.append(getConfigListEntry(_("Folder user file .xml"), config.plugins.XCplugin.pthxmlfile, _("Configure folder containing .xml files\nPress 'OK' to change location.")))
            self.list.append(getConfigListEntry(_("Media Folder "), config.plugins.XCplugin.pthmovie, _("Configure folder containing movie/media files\nPress 'OK' to change location.")))
            self.list.append(getConfigListEntry(_("Bouquet style "), config.plugins.XCplugin.typelist, _("Configure the type of conversion in the favorite list")))
            if config.plugins.XCplugin.typelist.value == 'Combined Live/VOD' :
                self.list.append(getConfigListEntry(_("Conversion type Output "), config.plugins.XCplugin.typem3utv, _("Configure type of stream to be downloaded by conversion")))
            self.list.append(getConfigListEntry(_("Place IPTV bouquets at "), config.plugins.XCplugin.bouquettop, _("Configure to place the bouquets of the converted lists")))
            self.list.append(getConfigListEntry(_("Picons IPTV "), config.plugins.XCplugin.picons, _("Download Picons ?")))            
            if config.plugins.XCplugin.picons.value:
                self.list.append(getConfigListEntry(_("Picons IPTV bouquets to "), config.plugins.XCplugin.pthpicon, _("Configure folder containing picons files\nPress 'OK' to change location.")))
            self["config"].list = self.list
            self["config"].setList(self.list)

        #                
        def changedEntry(self):
            for x in self.onChangedEntry:
                    x()        

        #
        def getCurrentEntry(self):
            return self["config"].getCurrent()[0]
        # #
        # def showhide(self):
            # if fileExists('/tmp/xc.txt'):
                # self['key_yellow'].show()
                # self['info2'].setText('you can import information server from /tmp/xc.txt')
            # else:
                # self['key_yellow'].hide()
                # self['info2'].setText('')
        #
        def showhide(self):
            if fileExists('/etc/enigma2/iptv.sh'):
                self['key_yellow'].show()
                self['info2'].setText('import server from /etc/enigma2/iptv.sh')
            else:
                self['key_yellow'].hide()
                self['info2'].setText('')
				
        #
        def getCurrentValue(self):
            return str(self["config"].getCurrent()[1].getText())

        #
        def createSummary(self):
            from Screens.Setup import SetupSummary
            return SetupSummary
   
        #
        def keyLeft(self):
            ConfigListScreen.keyLeft(self)
            print "current selection:", self["config"].l.getCurrentSelection()
            self.createSetup()
            self.showhide()

        #
        def keyRight(self):
            ConfigListScreen.keyRight(self)
            print "current selection:", self["config"].l.getCurrentSelection()
            self.createSetup()
            self.showhide()
           
        #
        # def Ok_edit(self):    
            # ConfigListScreen.keyRight(self)
            # print "current selection:", self["config"].l.getCurrentSelection()
            # self.createSetup()
            # self.showhide()
            
        #
        def ok(self):    
            ConfigListScreen.keyOK(self)
            sel = self['config'].getCurrent()[1]
            if sel and sel == config.plugins.XCplugin.pthmovie:
                self.setting = 'pthmovie'
                self.openDirectoryBrowser(config.plugins.XCplugin.pthmovie.value)
            if sel and sel == config.plugins.XCplugin.pthxmlfile:
                self.setting = 'pthxmlfile'
                self.openDirectoryBrowser(config.plugins.XCplugin.pthxmlfile.value)
            if sel and sel == config.plugins.XCplugin.pthpicon:
                self.setting = 'pthpicon'
                self.openDirectoryBrowser(config.plugins.XCplugin.pthpicon.value)				
            else:
                pass


        def openDirectoryBrowser(self, path):
            try:
                self.session.openWithCallback(
                 self.openDirectoryBrowserCB,
                 LocationBox,
                 windowTitle=_('Choose Directory:'),
                 text=_('Choose directory'),
                 currDir=str(path),
                 bookmarks=config.movielist.videodirs,
                 autoAdd=False,
                 editDir=True,
                 inhibitDirs=['/bin', '/boot', '/dev', '/home', '/lib', '/proc', '/run', '/sbin', '/sys', '/var'],
                 minFree=15)
            except Exception as e:
                print ('openDirectoryBrowser get failed: ', str(e))


        def openDirectoryBrowserCB(self, path):
                if path is not None:
                    if self.setting == 'pthmovie':
                        config.plugins.XCplugin.pthmovie.setValue(path)
                    if self.setting == 'pthxmlfile':
                        config.plugins.XCplugin.pthxmlfile.setValue(path)
                    if self.setting == 'pthpicon':
                        config.plugins.XCplugin.pthpicon.setValue(path)						
						
                return

		#        
        def cfgok(self):
            if config.plugins.XCplugin.picons.value and config.plugins.XCplugin.pthpicon.value == '/usr/share/enigma2/picon/':
                if not os.path.exists('/usr/share/enigma2/picon'):    
                    system('mkdir /usr/share/enigma2/picon') 

            if config.plugins.XCplugin.pthxmlfile.value == '/media/hdd/xc' :
                if not os.path.exists('/media/hdd'):
                    self.mbox = self.session.open(MessageBox, _('/media/hdd NOT DETECTED!'), MessageBox.TYPE_INFO, timeout=4)
                    return
            if config.plugins.XCplugin.pthxmlfile.value == '/media/usb/xc' :
                if not os.path.exists('/media/usb'):
                    self.mbox = self.session.open(MessageBox, _('/media/usb NOT DETECTED!'), MessageBox.TYPE_INFO, timeout=4)
                    return
            self.check_xcplugin_xml()
            self.xml_plugin()
            self.save()
            

        def check_xcplugin_xml(self):
            if not os.path.exists(config.plugins.XCplugin.pthxmlfile.value):
                system('mkdir ' + config.plugins.XCplugin.pthxmlfile.value)
            if not fileExists(config.plugins.XCplugin.pthxmlfile.value  + 'xc_e2_plugin.xml'):
                filesave = 'xc_e2_plugin.xml' 
                pth= config.plugins.XCplugin.pthxmlfile.value 
                print 'pth:', pth                
                f5 = open(pth + filesave, "w") 
                f5.write(str('<?xml version="1.0" encoding="UTF-8" ?>\n' + '<items>\n' + '<plugin_version>' + currversion + '</plugin_version>\n' +'<xtream_e2portal_url><![CDATA[http://exampleserver.com:8888/enigma2.php]]></xtream_e2portal_url>\n' + '<username>Enter Username</username>\n' + '<password>Enter Password</password>\n'+ '</items>'))
                f5.close()
                
        def xml_plugin(self):
            filesave = 'xc_' + config.plugins.XCplugin.user.value + '.xml' 
            
            filesave = filesave.replace(':','_')
            filesave = filesave.lower()
            
            pth= config.plugins.XCplugin.pthxmlfile.value 
            print 'pth:', pth                
            f5 = open(pth + filesave, "w") 
            f5.write(str('<?xml version="1.0" encoding="UTF-8" ?>\n' + '<items>\n' + '<plugin_version>' + currversion + '</plugin_version>\n' +'<xtream_e2portal_url><![CDATA[http://'+ config.plugins.XCplugin.hostaddress.value + '/enigma2.php]]></xtream_e2portal_url>\n' + '<username>' + config.plugins.XCplugin.user.value + '</username>\n' + '<password>' + config.plugins.XCplugin.passw.value + '</password>\n'+ '</items>'))
            f5.close()        


        #
        def save(self):
            global nochange
            if self['config'].isChanged():
                for x in self['config'].list:
                    x[1].save()
                configfile.save()
                nochange = False
                self.mbox = self.session.open(MessageBox, _('Settings saved successfully !'), MessageBox.TYPE_INFO, timeout=5)
            nochange = True
            self.close()
        #

        def KeyText(self):
            sel = self['config'].getCurrent()
            if sel:
                self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self['config'].getCurrent()[0], text=self['config'].getCurrent()[1].value)

        def VirtualKeyBoardCallback(self, callback = None):
            if callback is not None and len(callback):
                self['config'].getCurrent()[1].value = callback
                self['config'].invalidate(self['config'].getCurrent())
            return                

        #

        def cancelConfirm(self, result):
            if not result:
                return
            for x in self['config'].list:
                x[1].cancel()
            self.close()

        def extnok(self):
            if self['config'].isChanged():
                self.session.openWithCallback(self.cancelConfirm, MessageBox, _('Really close without saving settings?'))
            else:

                self.close()
             
           
        def ImportInfosServer(self):
            if fileExists('/tmp/xc.txt'):
                    f = file('/tmp/xc.txt',"r")
                    chaine = f.readlines()
                    f.close()
                    url = chaine[0].replace('\n','').replace('\t','').replace('\r','')
                    user = chaine[1].replace('\n','').replace('\t','').replace('\r','')
                    pswrd = chaine[2].replace('\n','').replace('\t','').replace('\r','')
                    filesave = 'xc_' + user + '.xml' 
                    
                    filesave = filesave.replace(':','_')
                    filesave = filesave.lower()                    
                    
                    pth= config.plugins.XCplugin.pthxmlfile.value 
                    print 'pth:', pth                
                    f5 = open(pth + filesave, "w") 
                    f5.write(str('<?xml version="1.0" encoding="UTF-8" ?>\n' + '<items>\n' + '<plugin_version>' + currversion + '</plugin_version>\n' +'<xtream_e2portal_url><![CDATA[http://'+ url + '/enigma2.php]]></xtream_e2portal_url>\n' + '<username>' + user + '</username>\n' + '<password>' + pswrd + '</password>\n'+ '</items>'))
                    f5.close()
                    config.plugins.XCplugin.hostaddress.setValue(url)
                    config.plugins.XCplugin.user.setValue(user)
                    config.plugins.XCplugin.passw.setValue(pswrd)                    
                    self.mbox = self.session.open(MessageBox, _('File Imported to Config and Saved to %s !' % filesave ), MessageBox.TYPE_INFO, timeout=5)
                    self.ConfigText()                    
            else:
                self.mbox = self.session.open(MessageBox, _('File does not exist /tmp/xc.txt!'), MessageBox.TYPE_INFO, timeout=5)                
                

        def ConfigText(self):
            ##
            global STREAMS
            STREAMS = iptv_streamse()
            STREAMS.read_config()

            if STREAMS.xtream_e2portal_url and STREAMS.xtream_e2portal_url != 'exampleserver.com:8888' :
                STREAMS.get_list(STREAMS.xtream_e2portal_url)            
                self['playlist'].setText(STREAMS.playlistname)
            return    
            

        def Team(self):
            self.session.open(OpenServer)        
            self.onShown.append(self.ConfigText)    

# STREAM IPTV                  
class iptv_streamse():

    def __init__(self):
        global MODUL
        self.iptv_list = []
        self.plugin_version = ''
        self.list_index = 0
        self.iptv_list_tmp = []
        self.list_index_tmp = 0
        self.playlistname_tmp = ''
        self.video_status = False
        self.server_oki = True
        self.playlistname = ''
        self.next_page_url = ''
        self.next_page_text = ''
        self.prev_page_url = ''
        self.prev_page_text = ''
        self.url = ''
        self.xtream_e2portal_url = ''
        self.username = ''
        self.password = '' 
        self.xtream_e2portal_url = 'http://' + config.plugins.XCplugin.hostaddress.value + '/enigma2.php'   #con config.value or get_Value
        self.username = config.plugins.XCplugin.user.value  #con config.value
        self.password = config.plugins.XCplugin.passw.value  #con config.value
        # self.use_rtmpw = False
        if config.plugins.XCplugin.services.value == 'Gstreamer':
            esr_id = '4097'
        else:
            esr_id = '5002'          
        self.esr_id = esr_id    
        self.play_vod = False
        self.play_iptv = False
        self.xml_error = ''
        self.ar_id_start = 3
        self.ar_id_player = 3
        self.ar_id_end = 3
        self.iptv_list_history = []
        self.ar_start = True
        self.clear_url = ''
        self.img_loader = False
        self.images_tmp_path = '/tmp'
        self.moviefolder = config.plugins.XCplugin.pthmovie.value #+ 'movie/'
        self.trial = ''
        self.banned_text = ''
        self.trial_time = 30
        self.timeout_time = 10
        self.cont_play = True
        self.systems = ''
        self.playhack = ''
        self.url_tmp = ''
        self.next_page_url_tmp = ''
        self.next_page_text_tmp = ''
        self.prev_page_url_tmp = ''
        self.prev_page_text_tmp = ''
        self.disable_audioselector = False
        # MODUL = html_parser_moduls()
        if config.plugins.XCplugin.hostaddress.value != 'exampleserver.com:8888' :
            MODUL = html_parser_moduls()

            
    def MoviesFolde(self):
        return self.moviefolder

    #
    def getValue(self, definitions, default):
        ret = ''
        Len = len(definitions)
        return Len > 0 and definitions[Len - 1].text or default

    #

    def read_config(self):
        try:
            tree = ElementTree()
            xtream_e2portal_url = 'http://' + config.plugins.XCplugin.hostaddress.value + '/enigma2.php'            
            self.xtream_e2portal_url = xtream_e2portal_url
            self.url = self.xtream_e2portal_url

            username = config.plugins.XCplugin.user.value
            if username and username != '':
                self.username = username
            password = config.plugins.XCplugin.passw.value
            if password and password != '':
                self.password = password
            xmlname = config.plugins.XCplugin.hostaddress.value
            self['Text'].setText(xmlname)
            SetValue['MyServer'] = STREAMS.playlistname
            self['playlist'].setText(STREAMS.playlistname)    
            plugin_version = xml.findtext('plugin_version')
            if plugin_version and plugin_version != '':
                self.plugin_version = plugin_version
            self.img_loader = self.getValue(xml.findall('images_tmp'), False)
            self.images_tmp_path = self.getValue(xml.findall('images_tmp_path'), self.images_tmp_path)

            print '-----------CONFIG NEW-----------'

            print 'XCplugin Mod. E2 Plugin v. %s Lite' % version
            print '-----------CONFIG NEW END----------'

        except Exception as ex:
            print '++++++++++ERROR READ CONFIG+++++++++++++'
            print ex

    #
    def reset_buttons(self):
        self.next_page_url = None
        self.next_page_text = ''
        self.prev_page_url = None
        self.prev_page_text = ''
        return

    #

    def get_list(self, url = None):
        self.xml_error = ''
        self.url = url
        self.clear_url = url
        self.list_index = 0
        iptv_list_temp = []
        xml = None
        self.next_request = 0
        try:
            print '!!!!!!!!-------------------- URL %s' % url
            if url.find('username') > -1:
                self.next_request = 1
            if any([url.find('.ts') > -1, url.find('.mp4') > -1]):
                self.next_request = 2
            xml = self._request(url)
            if xml:
                self.next_page_url = ''
                self.next_page_text = ''
                self.prev_page_url = ''
                self.prev_page_text = ''
                self.playlistname = xml.findtext('playlist_name').encode('utf-8')
                self.next_page_url = xml.findtext('next_page_url')
                next_page_text_element = xml.findall('next_page_url')
                if next_page_text_element:
                    self.next_page_text = next_page_text_element[0].attrib.get('text').encode('utf-8')
                self.prev_page_url = xml.findtext('prev_page_url')
                prev_page_text_element = xml.findall('prev_page_url')
                if prev_page_text_element:
                    self.prev_page_text = prev_page_text_element[0].attrib.get('text').encode('utf-8')
                chan_counter = 0
                for channel in xml.findall('channel'):
                    chan_counter = chan_counter + 1
                    name = channel.findtext('title').encode('utf-8')
                    name = base64.b64decode(name)
                    piconname = channel.findtext('logo')
                    description = channel.findtext('description')
                    desc_image = channel.findtext('desc_image')
                    img_src = ''
                    if description != None:
                        description = description.encode('utf-8')
                        if desc_image:
                            img_src = desc_image
                        description = base64.b64decode(description)
                        description = description.replace('<br>', '\n')
                        description = description.replace('<br/>', '\n')
                        description = description.replace('</h1>', '</h1>\n')
                        description = description.replace('</h2>', '</h2>\n')
                        description = description.replace('&nbsp;', ' ')
                        description4playlist_html = description
                        text = re.compile('<[\\/\\!]*?[^<>]*?>')
                        description = text.sub('', description)
                    stream_url = channel.findtext('stream_url')
                    playlist_url = channel.findtext('playlist_url')
                    category_id = channel.findtext('category_id')
                    ts_stream = channel.findtext('ts_stream')
                    chan_tulpe = (chan_counter,
                     name,
                     description,
                     piconname,
                     stream_url,
                     playlist_url,
                     category_id,
                     img_src,
                     description4playlist_html,
                     ts_stream,)
                    iptv_list_temp.append(chan_tulpe)

        except Exception as ex:
            print ex
            self.xml_error = ex
            print '!!!!!!!!!!!!!!!!!! ERROR: XML to LISTE'

        if len(iptv_list_temp):
            self.iptv_list = iptv_list_temp
        else:
            print 'ERROR IPTV_LIST_LEN = %s' % len(iptv_list_temp)
        return

    #
    def _request(self, url):
        if config.plugins.XCplugin.hostaddress.value != 'exampleserver.com:8888' :
            url = url.strip(' \t\n\r')
            if self.next_request == 1:
                url = url
            elif self.next_request == 0:
                url = url + '?' + 'username=' + self.username + '&password=' + self.password
            else:
                url = url    
            print url
            ######global
            global urlinfo
            urlinfo = url
            print "urlinfo:", urlinfo   
            
            try:

                #
                # user_agent= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                 # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
                
                # req = urllib2.Request(url, None, user_agent)
                #########
			
                req = urllib2.Request(url, None, {'User-agent': 'Xtream-Codes Enigma2 Plugin',
                 'Connection': 'Close'})
				 

                if self.server_oki == True:
                    xmlstream = urllib2.urlopen(req, timeout=NTIMEOUT).read()
                res = fromstring(xmlstream)
            except Exception as ex:
                print ex
                print 'REQUEST Exception'
                res = None
                self.xml_error = ex
            return res


        ####

        else:
            res = None
            return res	
        

try:
    from Tools.Directories import fileExists, pathExists
    from Components.Network import iNetwork
except Exception as ex:
    print ex
    print 'IMPORT ERROR'

try:
    import commands
except Exception as ex:
    print ex



#
class IPTVInfoBarShowHide():
    """ InfoBar show/hide control, accepts toggleShow and hide actions, might start
    fancy animations. """
    STATE_HIDDEN = 0
    STATE_HIDING = 1
    STATE_SHOWING = 2
    STATE_SHOWN = 3

    def __init__(self):
        self['ShowHideActions'] = ActionMap(['InfobarShowHideActions'], {'toggleShow': self.toggleShow,
         'hide': self.hide}, 0)
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStart: self.serviceStarted})
        self.__state = self.STATE_SHOWN
        self.__locked = 0
        self.hideTimer = eTimer()
        try:
            self.hideTimer_conn = self.hideTimer.timeout.connect(self.doTimerHide)
        except:
            self.hideTimer.callback.append(self.doTimerHide)

        self.hideTimer.start(5000, True)
        self.onShow.append(self.__onShow)
        self.onHide.append(self.__onHide)


    #
    def serviceStarted(self):
        if self.execing:
            if config.usage.show_infobar_on_zap.value:
                self.doShow()


    #
    def __onShow(self):
        self.__state = self.STATE_SHOWN
        self.startHideTimer()


    #
    def startHideTimer(self):
        if self.__state == self.STATE_SHOWN and not self.__locked:
            idx = config.usage.infobar_timeout.index
            if idx:
                self.hideTimer.start(idx * 1500, True)


    #
    def __onHide(self):
        self.__state = self.STATE_HIDDEN


    #
    def doShow(self):
        self.show()
        self.startHideTimer()


    #
    def doTimerHide(self):
        self.hideTimer.stop()
        if self.__state == self.STATE_SHOWN:
            self.hide()


    #
    def toggleShow(self):
        if self.__state == self.STATE_SHOWN:
            self.hide()
            self.hideTimer.stop()
        elif self.__state == self.STATE_HIDDEN:
            self.show()


    #
    def lockShow(self):
        self.__locked = self.__locked + 1
        if self.execing:
            self.show()
            self.hideTimer.stop()


    #
    def unlockShow(self):
        self.__locked = self.__locked - 1
        if self.execing:
            self.startHideTimer()

    #
    def debug(obj, text = ''):
        # print datetime.fromtimestamp(time()).strftime('[%H:%M:%S]')
        print text + ' %s\n' % obj

# DOWNLOAD MANAGER

class downloadJob(Job):

    def __init__(self, toolbox, cmdline, filename, filetitle):
        Job.__init__(self, 'Download: %s' % filetitle)
        self.filename = filename
        self.toolbox = toolbox
        self.retrycount = 0
        downloadTask(self, cmdline, filename)

    def retry(self):
        self.retrycount += 1
        self.restart()

    def cancel(self):
        self.abort()

# DOWNLOAD TASKS

class downloadTask(Task):
    ERROR_CORRUPT_FILE, ERROR_RTMP_ReadPacket, ERROR_SEGFAULT, ERROR_SERVER, ERROR_UNKNOWN = range(5)

    #
    def __init__(self, job, cmdline, filename):
        Task.__init__(self, job, _('Downloading ...'))
        self.postconditions.append(downloadTaskPostcondition())
        self.setCmdline(cmdline)
        self.filename = filename
        self.toolbox = job.toolbox
        self.error = None
        self.lasterrormsg = None
        return

    #


    def processOutput(self, data):
        try:
            if data.endswith('%)'):
                startpos = data.rfind('sec (') + 5
                if startpos and startpos != -1:
                    self.progress = int(float(data[startpos:-4]))
            elif data.find('%') != -1:
                tmpvalue = data[:data.find('%')]
                tmpvalue = tmpvalue[tmpvalue.rfind(' '):].strip()
                tmpvalue = tmpvalue[tmpvalue.rfind('(') + 1:].strip()
                self.progress = int(float(tmpvalue))
            else:
                Task.processOutput(self, data)
        except Exception as errormsg:
            print 'Error processOutput: ' + str(errormsg)
            Task.processOutput(self, data)

    #


    def processOutputLine(self, line):
        line = line[:-1]
        self.lasterrormsg = line
        if line.startswith('ERROR:'):
            if line.find('RTMP_ReadPacket') != -1:
                self.error = self.ERROR_RTMP_ReadPacket
            elif line.find('corrupt file!') != -1:
                self.error = self.ERROR_CORRUPT_FILE
                system('rm -f %s' % self.filename)
            else:
                self.error = self.ERROR_UNKNOWN
        elif line.startswith('wget:'):
            if line.find('server returned error') != -1:
                self.error = self.ERROR_SERVER
        elif line.find('Segmentation fault') != -1:
            self.error = self.ERROR_SEGFAULT

    #


    def afterRun(self):
        if self.getProgress() == 0 or self.getProgress() == 100:
            message = 'Movie successfully transfered to your HDD!' + '\n' + self.filename
            web_info(message)

# DOWNLOAD RECOVERY
class downloadTaskPostcondition(Condition):
    RECOVERABLE = True

    #
    def check(self, task):
        if task.returncode == 0 or task.error is None:
            return True
        else:
            return False
            return

    #
    def getErrorMessage(self, task):
        return {task.ERROR_CORRUPT_FILE: _('Video Download Failed!\n\nCorrupted Download File:\n%s' % task.lasterrormsg),
         task.ERROR_RTMP_ReadPacket: _('Video Download Failed!\n\nCould not read RTMP-Packet:\n%s' % task.lasterrormsg),
         task.ERROR_SEGFAULT: _('Video Download Failed!\n\nSegmentation fault:\n%s' % task.lasterrormsg),
         task.ERROR_SERVER: _('Video Download Failed!\n\nServer returned error:\n%s' % task.lasterrormsg),
         task.ERROR_UNKNOWN: _('Video Download Failed!\n\nUnknown Error:\n%s' % task.lasterrormsg)}[task.error]

        


VIDEO_ASPECT_RATIO_MAP = {0: '4:3 Letterbox',
 1: '4:3 PanScan',
 2: '16:9',
 3: '16:9 Always',
 4: '16:10 Letterbox',
 5: '16:10 PanScan',
 6: '16:9 Letterbox'}
 

#

def nextAR():
    try:

        STREAMS.ar_id_player += 3
        if STREAMS.ar_id_player > 6:
            STREAMS.ar_id_player = 3          

        eAVSwitch.getInstance().setAspectRatio(STREAMS.ar_id_player)
        print 'STREAMS.ar_id_player NEXT %s' % VIDEO_ASPECT_RATIO_MAP[STREAMS.ar_id_player]
        return VIDEO_ASPECT_RATIO_MAP[STREAMS.ar_id_player]
    except Exception as ex:
        print ex
        return 'nextAR ERROR %s' % ex

#
def prevAR():
    try:
        STREAMS.ar_id_player -= 3
        if STREAMS.ar_id_player == -1:
            STREAMS.ar_id_player = 3

        eAVSwitch.getInstance().setAspectRatio(STREAMS.ar_id_player)
        print 'STREAMS.ar_id_player PREV %s' % VIDEO_ASPECT_RATIO_MAP[STREAMS.ar_id_player]
        return VIDEO_ASPECT_RATIO_MAP[STREAMS.ar_id_player]
    except Exception as ex:
        print ex
        return 'prevAR ERROR %s' % ex

#
def web_info(message):
    try:
        message = quote_plus(str(message))
        cmd = "wget -qO - 'http://127.0.0.1/web/message?type=2&timeout=10&text=%s' 2>/dev/null &" % message
        debug(cmd, 'CMD -> Console -> WEBIF')
        os.popen(cmd)
    except:
        print 'web_info ERROR'

#
def channelEntryIPTVplaylist(entry):
    menu_entry = [entry, (eListboxPythonMultiContent.TYPE_TEXT,
      CHANNEL_NUMBER[0],
      CHANNEL_NUMBER[1],
      CHANNEL_NUMBER[2],
      CHANNEL_NUMBER[3],
      CHANNEL_NUMBER[4],
      RT_HALIGN_CENTER,
      '%s' % entry[0]), (eListboxPythonMultiContent.TYPE_TEXT,
      CHANNEL_NAME[0],
      CHANNEL_NAME[1],
      CHANNEL_NAME[2],
      CHANNEL_NAME[3],
      CHANNEL_NAME[4],
      RT_HALIGN_LEFT,
      entry[1])]
    return menu_entry


# XC-PLUGIN MAIN
class xc_Main(Screen):

    def __init__(self, session):
        global STREAMS
        # STREAMS = iptv_streamse()
        self.session = session
        skin = SKIN_PATH + '/xc_Main.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()        
        Screen.__init__(self, session)    
        self.channel_list = STREAMS.iptv_list
        self.index = STREAMS.list_index
        self.banned = False
        self.banned_text = ''
        self.mlist = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.mlist.l.setFont(0, gFont(FONT_0[0], FONT_0[1]))
        self.mlist.l.setFont(1, gFont(FONT_1[0], FONT_1[1]))
        self.mlist.l.setItemHeight(BLOCK_H)
        self.go()        
        self['exp']= Label('')        
        self['info'] = Label()   
        self['playlist'] = Label()
        self['description'] = Label()        
        self['DownVOD'] = Label(_("Download"))
        self['state'] = Label('') 
        self['version'] = Label(_(' V.%s Lite' % version)) 
        self['key_red'] = Label(_("Close"))
        self["key_green"] = Label(_("Create") + " Bouquet") 
        self["key_yellow"] = Label(_("Remove") + " Bouquet")
        self["key_blu"] = Label(_("Load") + " M3U File")        
        self.icount = 0
        self.errcount = 0
        self.onShown.append(self.show_all)
        self['poster'] = Pixmap()
        self.picload = ePicLoad()
        self.picfile = ''
        self['Text'] = Label('')
        self.update_desc = True
        self.pass_ok = False
        self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
        self.checkinf()        
        self['actions'] = HelpableActionMap(self, 'nStreamPlayerPlaylist', {'homePlaylist': self.start_portal,
         'ok': self.ok,
         # 'iptv' : self.iptv_sh,
         'check_download_vod' : self.check_download_vod,
         'taskManager': self.taskManager,
         'xcPlay': self.xcPlay,
         'showMediaPlayer' : self.showMediaPlayer,
         'showMovies' : self.showMovies,
         'help': self.help,
         'listUpdate' : self.update_list, #tv
         'save_list': self.msg_save_tv, 
         'removelist': self.removelist, 
         'exitPlugin': self.exitY,
         'exit_box': self.exitY,         
         'info': self.userinfo, #self.info, #info
         'moreInfo': self.show_more_info, #epg
         'menu': self.config,
         'power': self.power}, -1)
        self.temp_index = 0
        self.temp_channel_list = None
        self.temp_playlistname = None
        self.url_tmp = None
        self.video_back = False
        self.passwd_ok = False
        xmlname = config.plugins.XCplugin.hostaddress.value
        self['Text'].setText(xmlname)
        SetValue['MyServer'] = STREAMS.playlistname
        self['playlist'].setText(STREAMS.playlistname)

        
    def config(self):
        # system("cd / && cp -f " + piclogo + ' %s/poster.jpg' % STREAMS.images_tmp_path) 
        self.session.open(xc_config)
        # # self.onShown.append(self.update_list)
        # self.onShown.append(self.checkinf)
        # nochange = True
        if nochange == False :
            self.onShown.append(self.start_portal)
        
        
       
    def checkinf(self):
            url_info = urlinfo.replace('enigma2.php','player_api.php')
            print "url_info2 = ", url_info   
            try:
                fpage = urllib2.urlopen(url_info).read()
                print  "fpage =", fpage
                fp = eval(fpage)
                user_info = fp['user_info']
                print  "user_info =", user_info
                status = user_info['status']
                # self['check'].setText('Status: ' + status) 
                exp_date = user_info['exp_date']
                tconv = datetime.fromtimestamp(float(exp_date)).strftime('%c')
                self['exp'].setText('Exp date: ' + str(tconv)) 
                # max_connections = user_info['max_connections']
                # self['max_connect'].setText('Max Connections: ' +  str(max_connections))                 
                # active_cons = user_info['max_connections']
                # self['active_cons'].setText('User Active: ' +  str(active_cons))                  
                
            except Exception as ex:
                print ex
                print 'ERROR user_info'           
                # self['check'].setText('Status: no authorised!')
                self['exp'].setText('No Info')
                # self['max_connect'].setText('playlist/user') 
                # self['active_cons'].setText('no authorised!') 
            # self.update_list()     
            # print 'checkinf'            


    def userinfo(self):
        self.session.open(ShowInfo)
        

    def info(self):
        about = ('\nXCplugin E2 Plugin - v. %s\n\nby Lululla Info: lululla.altervista.org \n\nSkin By: MMARK Info e2skin.blogspot.it \n\n*** Please report any bugs you find ***\n\nThanks to corvoboys.com - linuxsat-support.com \nTo: Diamondear, MMark, Bliner_Key, Pcd \nTo: M2boom, Gutemine, Pauldb\nand all those i forgot to mention.') % version
        self.session.open(MessageBox, about, type=MessageBox.TYPE_INFO)        

    #
    def exitY(self):
            # clear_img()
            # OnclearMem()      
            if os.path.exists('/tmp/e2m3u2bouquet.py'):
                os.remove('/tmp/e2m3u2bouquet.py')
            if os.path.exists('/tmp/e2m3u2bouquet.pyo'):
                os.remove('/tmp/e2m3u2bouquet.pyo')                
            if STREAMS.playhack == '':
                self.session.nav.stopService()
                STREAMS.play_vod = False
                self.session.nav.playService(self.oldService)                
            print 'STREAMS.ar_id_end %i' % STREAMS.ar_id_end
            self.close()   


    #        
    def go(self):
        self.mlist.setList(map(channelEntryIPTVplaylist, self.channel_list))
        self.mlist.onSelectionChanged.append(self.update_description)
        self['feedlist'] = self.mlist

    #

    def showMediaPlayer(self):
            try:
                from Plugins.Extensions.MediaPlayer.plugin import MediaPlayer
                self.session.open(MediaPlayer)
                no_plugin = False
            except Exception, e:
                self.session.open(MessageBox, _("The MediaPlayer plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )

    # Show Lists Download
    def showMovies(self):  
            try:
                self.session.open(MovieSelection)
            except:
                pass


    def help(self):
        self.session.open(xc_help)

    #
    def update_list(self):
            global STREAMS
            STREAMS = iptv_streamse()
            STREAMS.read_config()
            if STREAMS.xtream_e2portal_url != 'exampleserver.com:8888' :
                STREAMS.get_list(STREAMS.xtream_e2portal_url)
                self.update_channellist()
                print 'update_list'

    #
    def taskManager(self): #shows list list downloaded
        self.session.open(xc_StreamTasks)

    #
    def xcPlay(self):
        self.session.open(xc_Play) 



###################################            
    def show_more_info(self):
        try:

            # if STREAMS.xtream_e2portal_url and STREAMS.xtream_e2portal_url != '' or 'exampleserver.com:8888' :
            if STREAMS.xtream_e2portal_url != '' or 'exampleserver.com:8888' :
                selected_channel = self.channel_list[self.mlist.getSelectionIndex()] 

                if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/TMBD/plugin.pyo"):
                    from Plugins.Extensions.TMBD.plugin import TMBD         #TMDB v.8.3           
                    if selected_channel[2] != None:
                        text = re.compile('<[\\/\\!]*?[^<>]*?>')
                        text_clear = ''
                        text_clear = text.sub('', selected_channel[1])
                        text=text_clear

                        if '.ts' in str(selected_channel[4]):
                                HHHHH = self.show_more_info_Title(selected_channel)
                                self.session.open(TMBD, HHHHH, False)
                        else:
                                text = charRemove(text)
                                self.session.open(TMBD, text, False) 

                elif fileExists('/usr/lib/enigma2/python/Plugins/Extensions/tmdb/plugin.pyo'):
                    from Plugins.Extensions.tmdb.tmdb import tmdbScreen #tmdb 7.3

                    if selected_channel[2] != None:
                        text = re.compile('<[\\/\\!]*?[^<>]*?>')
                        text_clear = ''
                        text_clear = text.sub('', selected_channel[1])
                        text=text_clear
                        #================
                        global service
                        target = text
                        filtertmdb
                        robj = re.compile('|'.join(filtertmdb.keys()))
                        service = robj.sub(lambda m: filtertmdb[m.group(0)], target)
                        service = service.replace("("," ").replace(")","").replace("."," ").replace("[","").replace("]","").replace("-"," ").replace("_"," ").replace("+"," ")
                        service = re.sub("[0-9][0-9][0-9][0-9]", "", service)     
                        #================
                        if '.ts' in str(selected_channel[4]):
                            HHHHH = self.show_more_info_Title(selected_channel)
                            self.session.open(tmdbScreen, HHHHH, 2)
                        else:
                            service = charRemove(service)						
                            self.session.open(tmdbScreen, service, 2)                                


                elif os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/IMDb/plugin.pyo'):
                    from Plugins.Extensions.IMDb.plugin import IMDB
                
                    if selected_channel[2] != None:
                        text = re.compile('<[\\/\\!]*?[^<>]*?>')
                        text_clear = ''
                        text_clear = text.sub('', selected_channel[1])
                        text=text_clear
                        if '.ts' in str(selected_channel[4]):
                            HHHHH = self.show_more_info_Title(selected_channel)
                            self.session.open(IMDB, HHHHH)
                        else:
                            text = charRemove(text)						
                            self.session.open(IMDB, text)

                elif selected_channel[2] != None:
                    text = re.compile('<[\\/\\!]*?[^<>]*?>')
                    text_clear = ''
                    text_clear = text.sub('', selected_channel[2])
                    self.session.open(xc_Epg, text_clear)
                else:
                    message = (_('No valid list '))
                    web_info(message) 
            else:
                message = (_('Please enter correct parameters in Config\n no valid list '))
                web_info(message) 


        except Exception as ex:
            print ex
            print 'ERROR show_more_info'


            
    def show_more_info_Title(self,truc):
        text_clear_1 = ''
        try:
            if truc[1] != None:
                self.descr = truc
                text = re.compile('<[\\/\\!]*?[^<>]*?>')
                AAA = self.descr[2].split("]")[1:][0]
                BBB = AAA.split("(")[:1][0]
                text_clear_1 = text.sub('', BBB).replace(' ',' ').replace('\n',' ').replace('\t',' ').replace('\r',' ')
                # return
            else:
                text_clear_1 = 'No Even'
        except Exception as ex:
            text_clear = 'mkach'
        return text_clear_1            



############################################

    # REC
    def check_download_vod(self):
        self.vod_entry = STREAMS.iptv_list[self.index]
        if self.temp_index > -1:
            self.index = self.temp_index
        self.vod_entry = STREAMS.iptv_list[self.index]    
        selected_channel = STREAMS.iptv_list[self.index]
        stream_url = selected_channel[4]
        playlist_url = selected_channel[5]    
        self.title = selected_channel[1]
        if playlist_url != None:
            message = (_('No Video to Download!!\nplaylist_url != None'))
            web_info(message) 
        # elif stream_url != None:
            # self.vod_url = stream_url
            # #if self.vod_url.split('.')[-1].lower() != 'ts' : 
            # self.session.openWithCallback(self.download_vod, MessageBox, _('DOWNLOAD VIDEO?\n%s' % self.title) , type=MessageBox.TYPE_YESNO, timeout = 15, default = False)
            # #else:
            # #    message = (_('Live Player Active in Setting: set No for Record Live'))
            # #    web_info(message)    


        elif stream_url != None:
            self.vod_url = stream_url
            if self.vod_url.split('.')[-1].lower() != 'ts': 
               self.session.openWithCallback(self.download_vod, MessageBox, _('DOWNLOAD VIDEO?\n%s' % self.title) , type=MessageBox.TYPE_YESNO, timeout = 15, default = False)
            else:
                message = (_('Live Player Active in Setting: set No for Record Live'))
                web_info(message)    

        else:
            message = (_('No Video to Download\Record!!'))
            web_info(message)     

    #
    def download_vod(self, result):
        if result:
            try: 
                movie = config.plugins.XCplugin.pthmovie.value #+ 'movie/'            
                self['state'].setText('Download VOD')
                useragent = "--header='User-Agent: QuickTime/7.6.2 (qtver=7.6.2;os=Windows NT 5.1Service Pack 3)'"
                ende = 'mp4'
                if self.vod_url.split('.')[-1].lower() == 'flv':
                    ende = 'flv'                
                title_translit = cyr2lat(self.title)
                filename = ASCIItranslit.legacyEncode(title_translit + '.') + ende
                filename = filename.replace('(', '_')
                filename = filename.replace(')', '_')
                filename = filename.replace('#', '')
                filename = filename.replace('+', '_')
                filename = filename.replace('\'', '_')
                filename = filename.replace("'", "_")
                filename = filename.encode('utf-8') 
                cmd = "wget %s -c '%s' -O '%s%s'" % (useragent, self.vod_url, movie, filename)
                JobManager.AddJob(downloadJob(self, cmd, movie + filename, self.title))
                self.createMetaFile(filename)
                self.LastJobView()
                self.mbox = self.session.open(MessageBox, _('[DOWNLOAD] ' + self.title), MessageBox.TYPE_INFO, timeout=10)

            except Exception as ex:
                print ex
                print 'ERROR download_vod'


    #
    def LastJobView(self):
        currentjob = None
        for job in JobManager.getPendingJobs():
            currentjob = job

        if currentjob is not None:
            self.session.open(JobView, currentjob)

    #
    def createMetaFile(self, filename):
        try:
            movie = config.plugins.XCplugin.pthmovie.value #+ 'movie/'
            text = re.compile('<[\\/\\!]*?[^<>]*?>')
            text_clear = ''
            if self.vod_entry[2] != None:
                text_clear = text.sub('', self.vod_entry[2])
            serviceref = eServiceReference(4097, 0, movie + filename)
            metafile = open('%s%s.meta' % (movie, filename), 'w') 
            metafile.write('%s\n%s\n%s\n%i\n' % (serviceref.toString(),
             self.title.replace('\n', ''),
             text_clear.replace('\n', ''),
             time()))
            metafile.close()
        except Exception as ex:
            print ex
            print 'ERROR metaFile'


    #
    def button_updater(self):

        xmlname = config.plugins.XCplugin.hostaddress.value
        self['Text'].setText(xmlname)
        SetValue['MyServer'] = STREAMS.playlistname
        self['playlist'].setText(STREAMS.playlistname)



    # Switch PicView PLI/CVS     
    def decodeImage(self):
        try:
            x = self['poster'].instance.size().width()
            y = self['poster'].instance.size().height()
            picture = self.picfile
            picload = self.picload
            sc = AVSwitch().getFramebufferScale()
            self.picload.setPara((x, y, sc[0], sc[1], 0, 0, '#00000000'))
            if fileExists(BRAND)or fileExists(BRANDP):
                self.picload.PictureData.get().append(boundFunction(self.showImage)) ### OPEN
            else:
                self.picload_conn = self.picload.PictureData.connect(self.showImage) ### CVS
            self.picload.startDecode(self.picfile)
        except Exception as ex:
            print ex
            print 'ERROR decodeImage'
              
    # Switch PicView PLI/CVS
    def showImage(self, picInfo = None):
        self['poster'].show()
        try:
            ptr = self.picload.getData()
            if ptr:
                if fileExists(BRAND) or fileExists(BRANDP):
                    self['poster'].instance.setPixmap(ptr.__deref__())  ### OPEN
                else:
                    self['poster'].instance.setPixmap(ptr)                ### CVS
        except Exception as ex:
            print ex
            print 'ERROR showImage'
    #        
    def image_downloaded(self, id):
        self.decodeImage()


    #                
    def downloadError(self, raw):
        try:

            system("cd / && cp -f " + piclogo + ' %s/poster.jpg' % STREAMS.images_tmp_path) 
            self.decodeImage()
        except Exception as ex:
            print ex
            print 'exe downloadError'

    #
    def update_description(self):
        self.index = self.mlist.getSelectionIndex()
        if self.update_desc:
            try:
                self['info'].setText('')
                self['description'].setText('')
                system("cd / && cp -f " + piclogo + ' %s/poster.jpg' % STREAMS.images_tmp_path) 
                selected_channel = self.channel_list[self.index]
                if selected_channel[7] != '':
                    if selected_channel[7].find('http') == -1:
                        self.picfile = selected_channel[7]

                        self.decodeImage()
                        print 'LOCAL DESCR IMG'
                    else:
                        if STREAMS.img_loader == False:
                            self.picfile = '%s/poster.jpg' % STREAMS.images_tmp_path
                        else:
                            m = hashlib.md5()
                            m.update(selected_channel[7])
                            cover_md5 = m.hexdigest()
                            self.picfile = '%s/%s.jpg' % (STREAMS.images_tmp_path, cover_md5)

                        if os.path.exists(self.picfile) == False or STREAMS.img_loader == False:
                            downloadPage(selected_channel[7], self.picfile).addCallback(self.image_downloaded).addErrback(self.downloadError)
                        else:
                            self.decodeImage()

                if selected_channel[2] != None:
                    description = selected_channel[2]
                    description_2 = description.split(' #-# ')
                    if description_2:
                        self['description'].setText(description_2[0])
                        if len(description_2) > 1:
                            self['info'].setText(description_2[1])
                    else:
                        self['description'].setText(description)
            except Exception as ex:
                print ex
                print 'exe update_description'



    #        
    def start_portal(self):
        if STREAMS.playhack == '':
            self.session.nav.stopService()
            self.session.nav.playService(self.oldService)
            
        system("cd / && cp -f " + piclogo + ' %s/poster.jpg' % STREAMS.images_tmp_path)           
        
        self.index = 0

     
        self['poster'].hide()
        self.picload = ePicLoad()
        self.picfile = piclogo #SKIN_PATH + '/iptvlogo.jpg'           
        self['poster'].instance.setPixmapFromFile(piclogo) #(SKIN_PATH + '/iptvlogo.jpg')
        self.decodeImage()
        self['poster'].show()
        self['state'].setText('')
        self.update_list()
        print 'start_portal'
        self.checkinf() 



    #
    def update_channellist(self):
        print '--------------------- UPDATE CHANNEL LIST ----------------------------------------'
        if STREAMS.xml_error != '':
            print '### update_channellist ######URL#############'
            print STREAMS.clear_url

        self.channel_list = STREAMS.iptv_list
        self.update_desc = False
        self.mlist.setList(map(channelEntryIPTVplaylist, self.channel_list))
        self.mlist.moveToIndex(0)
        self.update_desc = True
        self.update_description() 
        self.button_updater()

    #

    def show_all(self):
        try:
            if self.passwd_ok == False:
                self.channel_list = STREAMS.iptv_list
                self.mlist.moveToIndex(self.index)
                self.mlist.setList(map(channelEntryIPTVplaylist, self.channel_list))
                self.mlist.selectionEnabled(1)
                self.button_updater()
            self.passwd_ok = False
        except Exception as ex:
            print ex
            print 'EXX showall'

    #            
    def ok(self):
        if STREAMS.xml_error != '':
            self.index_tmp = self.mlist.getSelectionIndex()

        else:
            selected_channel = self.channel_list[self.mlist.getSelectionIndex()]
            STREAMS.list_index = self.mlist.getSelectionIndex()
            title = selected_channel[1]

            if selected_channel[0] != '[H]':
                # title = datetime.fromtimestamp(time()).strftime('[%H:%M:%S %d/%m]   ') + selected_channel[1]
                title = ('[-]   ') + selected_channel[1]
            selected_channel_history = ('[H]',
             title,
             selected_channel[2],
             selected_channel[3],
             selected_channel[4],
             selected_channel[5],
             selected_channel[6],
             selected_channel[7],
             selected_channel[8],
             selected_channel[9])
            STREAMS.iptv_list_history.append(selected_channel_history)
            self.temp_index = -1

            if selected_channel[9] != None:
                self.temp_index = self.index
                #self.myPassInput()

            else:
                self.ok_checked()
                # self.ok_preview()



    def ok_checked(self):
        try:
            if self.temp_index > -1:
                self.index = self.temp_index
            global selected_channel    
            selected_channel = STREAMS.iptv_list[self.index]
            global stream_url, title
            stream_url = selected_channel[4]
            playlist_url = selected_channel[5]
            if playlist_url != None:
                STREAMS.get_list(playlist_url)
                self.update_channellist()
            elif stream_url != None:
                if stream_url.find('.ts') > 0:
                    self.set_tmp_list()
                    title = str(selected_channel[2])
                    self.passa()                  
                else:
                    self.set_tmp_list()
                    title = str(selected_channel[2])
                    self.passa()
            # return


        except Exception as ex:
            print ex
            print 'ok_checked'
            
            ##############
        

########### lower()
    def passa(self):
        if config.ParentalControl.configured.value:
            a = '+18', 'ADULTI', 'ADULT', 'ADULTS', 'AMATIX', 'BRAZZ', 'BRAZZERS', 'CANDY' 'COLMAX', 'DARING', 'HOT', 'HOTCLUB', 'HUST', 'HUSTL', 'LIFE TV', 'CENTOXCENTO', 'SCT', 'AMATEUR', 'EVIL ANGEL', 'SESTO SENSO', 'LIBID', 'LOV', 'MAN X', 'MAN-X', 'MANX', 'PENTHOUSE', 'PINK SHOW', 'PINK X', 'PINK-SHOW', 'PINK-X', 'PINKSHOW', 'PINKX', 'PLATINUM', 'PLAYB', 'PORN', 'RED LIGHT', 'RED-LIGHT', 'REDLIGHT','REALITY KINGS', 'SEX', 'SPICE', 'STARS', 'VENUS', 'VIVID', 'XX', 'XXL', 'XXX', 'CAZZO', 'FIGA', 'CULO', 'SEXTREME', 'XMUVI', 'DUSK', 'ARABEST', 'LIVECHANNEL', 'BLUE', 'PLAYBOY', 'adulti', 'adult', 'adults', 'amatix', 'brazz', 'brazzers', 'candy' 'colmax', 'daring', 'hotclub', 'hust', 'hustl', 'life tv', 'centoxcento', 'sct', 'amateur', 'evil angel', 'sesto senso', 'libid', 'lov', 'man x', 'man-x', 'manx', 'penthouse', 'pink show', 'pink x', 'pink-show', 'pink-x', 'pinkshow', 'pinkx', 'platinum', 'playb', 'porn', 'red light', 'red-light', 'redlight','reality kings', 'sex', 'spice', 'stars', 'venus', 'vivid', 'xx', 'xxl', 'xxx', 'cazzo', 'figa', 'culo', 'sextreme', 'xmuvi', 'dusk', 'arabest', 'livechannel', 'blue', 'playboy', 'hot', 'Adulti', 'Adult', 'Adults', 'Amatix', 'Brazz', 'Brazzers', 'Candy' 'Colmax', 'Daring', 'Hotclub', 'Hust', 'Hustl', 'Life Tv', 'Centoxcento', 'Sct', 'Amateur', 'Evil Angel', 'Sesto Senso', 'Libid', 'Lov', 'Man X', 'Man-X', 'Manx', 'Penthouse', 'Pink Show', 'Pink X', 'Pink-Show', 'Pink-X', 'Pinkshow', 'Pinkx', 'Platinum', 'Playb', 'Porn', 'Red Light', 'Red-Light', 'Redlight','Reality Kings', 'Sex', 'Spice', 'Stars', 'Venus', 'Vivid', 'Xx', 'Xxl', 'Xxx', 'Cazzo', 'Figa', 'Culo', 'Sextreme', 'Xmuvi', 'Dusk', 'Arabest', 'Livechannel', 'Blue', 'Playboy', 'Hot'
           
            if any(s in str(selected_channel[1] or selected_channel[2] or selected_channel[4] or selected_channel[5] or selected_channel[6] or selected_channel[8]) for s in a):
                self.allow()  
            else:
                self.pinEntered(True)
        else:
            self.pinEntered(True)     
   

    def allow(self):            
            from Screens.InputBox import PinInput
            self.session.openWithCallback(self.pinEntered, PinInput, pinList = [config.ParentalControl.setuppin.value], triesEntry = config.ParentalControl.retries.servicepin, title = _("Please enter the parental control pin code"), windowTitle = _("Enter pin code"))


    def pinEntered(self, result):
        if result:
            if stream_url.find('.ts') > 0:

                STREAMS.video_status = True
                STREAMS.play_vod = False
                print '------------------------ LIVE ------------------'
                if config.plugins.XCplugin.LivePlayer.value == False :
                   self.session.openWithCallback(self.check_standby, xc_Player)
                else:
                   self.session.openWithCallback(self.check_standby, nIPTVplayer)
            else:
                STREAMS.video_status = True
                STREAMS.play_vod = True
                print '----------------------- MOVIE ------------------'
                self.session.openWithCallback(self.check_standby, xc_Player)            
        else:
            self.session.open(MessageBox, _("The pin code you entered is wrong."), type=MessageBox.TYPE_ERROR, timeout=5)

############# 

    #
    def check_standby(self, myparam = None):
        debug(myparam, 'check_standby')
        if myparam:
            self.power()
        return
    #
    def power(self):
        self.session.nav.stopService()
        self.session.open(Standby)
        return
    #
    def set_tmp_list(self):
        self.index = self.mlist.getSelectionIndex()
        STREAMS.list_index = self.index
        STREAMS.list_index_tmp = STREAMS.list_index
        STREAMS.iptv_list_tmp = STREAMS.iptv_list
        STREAMS.playlistname_tmp = STREAMS.playlistname
        STREAMS.url_tmp = STREAMS.url
        STREAMS.next_page_url_tmp = STREAMS.next_page_url
        STREAMS.next_page_text_tmp = STREAMS.next_page_text
        STREAMS.prev_page_url_tmp = STREAMS.prev_page_url
        STREAMS.prev_page_text_tmp = STREAMS.prev_page_text
        
    #
    def load_from_tmp(self):
        debug('load_from_tmp')
        STREAMS.iptv_list = STREAMS.iptv_list_tmp
        STREAMS.list_index = STREAMS.list_index_tmp
        STREAMS.playlistname = STREAMS.playlistname_tmp
        STREAMS.url = STREAMS.url_tmp
        STREAMS.next_page_url = STREAMS.next_page_url_tmp
        STREAMS.next_page_text = STREAMS.next_page_text_tmp
        STREAMS.prev_page_url = STREAMS.prev_page_url_tmp
        STREAMS.prev_page_text = STREAMS.prev_page_text_tmp
        self.index = STREAMS.list_index

#####        

    def msg_save_tv(self):
        #Multi Live/Single VOD o Multi Live & VOD
        if config.plugins.XCplugin.typelist.value == 'Multi Live & VOD':
            dom = 'Multi Live & VOD'
            self.session.openWithCallback(self.createCfgxml,MessageBox,_("Convert Playlist to:  %s ?")% dom, MessageBox.TYPE_YESNO, timeout = 10, default = False)
        if config.plugins.XCplugin.typelist.value == 'Multi Live/Single VOD':
            dom = 'Multi Live/Single VOD'        
            self.session.openWithCallback(self.createCfgxml,MessageBox,_("Convert Playlist to:  %s ?")% dom, MessageBox.TYPE_YESNO, timeout = 10, default = False) 
        if config.plugins.XCplugin.typelist.value == 'Combined Live/VOD':
            dom = 'Combined Live/VOD'        
            self.session.openWithCallback(self.save_tv,MessageBox,_("Convert Playlist to:  %s ?")% dom, MessageBox.TYPE_YESNO, timeout = 10, default = False)  
        else:
            return
            
    def msg_save_tv_old(self):
            dom = (_('Combined Live/VOD'))     
            self.session.openWithCallback(self.save_tv,MessageBox,_("Convert Playlist to: %s ?")% dom, MessageBox.TYPE_YESNO, timeout = 7, default = False) 
            
    def save_tv(self, result):
        if result:
            self.save_old()
 
    def createCfgxml(self, result):
        if result:
            # #Convert Playlist to:  Multi Live/Single VOD VOD
            # if not fileExists('/tmp/userinfo.txt'): 
               # return
            # else:
                # file1 = "/tmp/userinfo.txt"
                # f1=open(file1,"r+")
                # txt1 = f1.read()
                # items = txt1.split("###")
                # host = items[0]
                # port = items[1]
                # usr = items[2]
                # passw = items[3]
                dest = '/tmp/e2m3u2bouquet.py'
                destx = '/tmp/e2m3u2bouquet.pyo'
                if os.path.exists(dest):
                    os.remove(dest)
                if os.path.exists(destx):
                    os.remove(destx)                    
                system('cp -f /usr/lib/enigma2/python/Plugins/Extensions/XCplugin/bouquet/e2m3u2bouquet.py /tmp')
                system('chmod -R 777 %s' % dest)
                system('cd /tmp')
                # print 'Host = ', host 
                # print 'Port= ', port 
                # print 'usr= ', usr 
                # print 'passw= ', passw
                
                usern = config.plugins.XCplugin.user.value
                passwo = config.plugins.XCplugin.passw.value
                
                allbqt = '0'
                iptvtypes = '0'   
                if config.plugins.XCplugin.typelist.value == 'Multi Live & VOD':
                    multivod = '1'
                else:
                    multivod = '0' 
                if config.plugins.XCplugin.bouquettop.value and config.plugins.XCplugin.bouquettop.value == 'Top':
                    bouquettop = '1'
                else:
                    bouquettop = '0'  #Bottom              

                PICONSPATH = config.plugins.XCplugin.pthpicon.value
                if config.plugins.XCplugin.picons.value:
                    picons = '1'  
                else:
                    picons = '0'                 
                #createCfgxml options
                if not os.path.exists('/etc/enigma2/e2m3u2bouquet'):
                    system('mkdir /etc/enigma2/e2m3u2bouquet')
                configfile = ('/etc/enigma2/e2m3u2bouquet/config.xml')
                if os.path.exists(configfile):
                    os.remove(configfile)


                m3uurl = urlinfo.replace('enigma2.php','get.php')
                print "m3uurl = ", m3uurl  
                epgurl = urlinfo.replace('enigma2.php','xmltv.php')
                print "epgurl = ", epgurl  
            
                f6= open(configfile, "w+")
                f6.write(str('<config>\n' + 
                            '    <supplier>\n' +
                            '        <name>' + namefolder + '</name>\n' + 
                            '        <enabled>1</enabled>\n' +
                            '        <m3uurl><![CDATA[' + m3uurl + '&type=m3u_plus&output=ts' + ']]></m3uurl>\n' +
                            '        <epgurl><![CDATA[' + epgurl + ']]></epgurl>\n' +   
                            
                            '        <username><![CDATA['+ usern + ']]></username>\n' +
                            '        <password><![CDATA['+ passwo + ']]></password>\n' +
                            
                            '        <iptvtypes>' + iptvtypes + '</iptvtypes>\n' +
                            '        <multivod>' + multivod + '</multivod>\n' +
                            '        <allbouquet>' + allbqt + '</allbouquet>\n' +
                            '        <picons>' + picons +'</picons>\n' +
                            '        <iconpath>' + PICONSPATH + '</iconpath>\n' +
                            '        <xcludesref>0</xcludesref>\n' + 
                            '        <bouqueturl></bouqueturl>\n' + 
                            '        <bouquetdownload>0</bouquetdownload>\n' +
                            '        <bouquettop>' + bouquettop + '</bouquettop>\n' + 
                            '    </supplier>\n' + 
                            '</config>\n'))
                f6.close            
                dom = STREAMS.playlistname #host
                com = 'python /tmp/e2m3u2bouquet.py'
                self.session.open(Console, _('Conversion %s in progress: ') % dom, ['%s' % com], closeOnSuccess=True)

   
                
    def removelist(self):
        self.session.openWithCallback(self.removelistok,MessageBox, _('Remove all XC Plugin bouquets?'), MessageBox.TYPE_YESNO, timeout = 15, default = True) 

    def removelistok(self, result):
        if result:
            dest = '/tmp/e2m3u2bouquet.py'
            destx = '/tmp/e2m3u2bouquet.pyo'
            if os.path.exists(dest):
                os.remove(dest)
            if os.path.exists(destx):
                os.remove(destx)                    
            system('cp -f /usr/lib/enigma2/python/Plugins/Extensions/XCplugin/bouquet/e2m3u2bouquet.py /tmp')
            system('chmod -R 777 %s' % dest)
            system('cd /tmp')

            com = 'python /tmp/e2m3u2bouquet.py -U'
            self.session.open(Console, _('Uninstall Team in progress: '), ['%s' % com], closeOnSuccess=False)
       
    def save_old(self):
        if config.plugins.XCplugin.typem3utv.value == 'MPEGTS to TV':
            pthTv = '/etc/enigma2/'
            xc1 = STREAMS.playlistname
            tag='suls_iptv_'
            namebouquet = xc1
            namebouquet = namebouquet.encode('utf-8') 
            xc12 = urlinfo.replace('enigma2.php','get.php')
            print "xc12 = ", xc12 
            xc2 = '&type=dreambox&output=mpegts'                
            if os.path.isfile('%suserbouquet.%s%s_.tv' % (pthTv, tag, namebouquet)):
                os.remove('%suserbouquet.%s%s_.tv' % (pthTv, tag, namebouquet)) 
            try:
                urlX = xc12 + xc2   
                webFile = urllib.urlopen(urlX)
                localFile = open(('%suserbouquet.%s%s_.tv' % (pthTv, tag, namebouquet)), 'w') 
                localFile.write(webFile.read())
                webFile.close()
                system('sleep 3')
            except Exception as ex:
                print ex
                print 'exe save_tv'
            in_bouquets = 0

            xcname = 'userbouquet.%s%s_.tv' % (tag, namebouquet)            
            # xcname = 'userbouquet.%s_.tv' % namebouquet
            if os.path.isfile('/etc/enigma2/bouquets.tv'):
                for line in open('/etc/enigma2/bouquets.tv'):
                    if xcname in line:
                        in_bouquets = 1
                if in_bouquets is 0:
                #####
                    new_bouquet = open('/etc/enigma2/new_bouquets.tv', 'w')
                    file_read = open('/etc/enigma2/bouquets.tv' ).readlines()                
                    if config.plugins.XCplugin.bouquettop.value == 'Top': #and config.plugins.XCplugin.bouquettop.value == 'Top':
                        #top  
                        new_bouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % xcname)  
                        for line in file_read:
                            new_bouquet.write(line)
                        new_bouquet.close()
                    else:
                        for line in file_read:
                            new_bouquet.write(line)                        
                        #bottom                          
                        new_bouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % xcname)  
                        new_bouquet.close()
                    system('cp -rf /etc/enigma2/bouquets.tv /etc/enigma2/backup_bouquets.tv')
                    system('mv -f /etc/enigma2/new_bouquets.tv /etc/enigma2/bouquets.tv')

        else:
            pthMovie = config.plugins.XCplugin.pthmovie.value #+ 'movie/'#'%s' % config.plugins.XCplugin.pthmovie.value
            xc1 = STREAMS.playlistname
            tag='suls_iptv_'
            namebouquet = xc1
            namebouquet = namebouquet.encode('utf-8') 

            xc12 = urlinfo.replace('enigma2.php','get.php')
            print "xc12 = ", xc12 
            xc2 = '&type=m3u_plus&output=ts'
            if os.path.isfile(pthMovie + namebouquet + ".m3u"):
                os.remove(pthMovie + namebouquet + ".m3u")    
            try:            
                urlX = xc12 + xc2   
                webFile = urllib.urlopen(urlX)
                localFile = open(('%s%s.m3u' % (pthMovie, namebouquet)), 'w') 
                localFile.write(webFile.read())
                system('sleep 5')                    
                webFile.close()
            except Exception as ex:
                print ex
                print 'exe save_tv'

            pth2 = pthMovie
            namebouquet = pth2 + '%s.m3u' % namebouquet.encode('utf-8')
            name = namebouquet.replace('.m3u', '').replace(pth2, '')
            pth =  config.plugins.XCplugin.pthmovie.value #+ 'movie/' #'%s' % config.plugins.XCplugin.pthmovie.value


            xcname = 'userbouquet.%s%s_.tv' % (tag, name)            
            # xcname = 'userbouquet.%s_.tv' % name
            self.iConsole = iConsole()
            desk_tmp = hls_opt = ''
            in_bouquets = 0
            if os.path.isfile('/etc/enigma2/%s' % xcname):
                os.remove('/etc/enigma2/%s' % xcname)
            with open('/etc/enigma2/%s' % xcname, 'w') as outfile:
                outfile.write('#NAME %s\r\n' % name.capitalize())
                for line in open(pth + '%s.m3u' % name.encode('utf-8')):
                    if line.startswith('http://') or line.startswith('https://'):
                        outfile.write('#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s' % line.replace(':', '%3a'))
                        outfile.write('#DESCRIPTION %s' % desk_tmp)
                    elif line.startswith('#EXTINF'):
                        desk_tmp = '%s' % line.split(',')[-1]
                    elif '<stream_url><![CDATA' in line:
                        outfile.write('#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s\r\n' % line.split('[')[-1].split(']')[0].replace(':', '%3a'))
                        outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
                    elif '<title>' in line:
                        if '<![CDATA[' in line:
                            desk_tmp = '%s\r\n' % line.split('[')[-1].split(']')[0]
                        else:
                            desk_tmp = '%s\r\n' % line.split('<')[1].split('>')[1]
                outfile.close()

            if os.path.isfile('/etc/enigma2/bouquets.tv'):
                for line in open('/etc/enigma2/bouquets.tv'):
                    if xcname in line:
                        in_bouquets = 1
                if in_bouquets is 0:
                #####
                    new_bouquet = open('/etc/enigma2/new_bouquets.tv', 'w')
                    file_read = open('/etc/enigma2/bouquets.tv' ).readlines()                 
                    if config.plugins.XCplugin.bouquettop.value == 'Top': #and config.plugins.XCplugin.bouquettop.value == 'Top':
                        # new_bouquet = open('/etc/enigma2/new_bouquets.tv', 'w')
                            #top  
                        new_bouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % xcname)  
                        for line in file_read:
                            new_bouquet.write(line)
                        new_bouquet.close()

                    else: #if config.plugins.XCplugin.bouquettop.value and config.plugins.XCplugin.bouquettop.value == 'Bottom':

                        for line in file_read:
                            new_bouquet.write(line)                        
                            #bottom                          
                        new_bouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % xcname)  
                        new_bouquet.close()
                    system('cp -rf /etc/enigma2/bouquets.tv /etc/enigma2/backup_bouquets.tv')
                    system('mv -f /etc/enigma2/new_bouquets.tv /etc/enigma2/bouquets.tv')

        self.mbox = self.session.open(MessageBox, _('Reload Playlists in progress...') + '\n\n\n' + _('wait please...'), MessageBox.TYPE_INFO, timeout=8)
        ReloadBouquet()                      


# XC PLAYER
class xc_Player(Screen, InfoBarBase, IPTVInfoBarShowHide, InfoBarSeek, InfoBarAudioSelection, InfoBarSubtitleSupport):
    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    ENABLE_RESUME_SUPPORT = True
    ALLOW_SUSPEND = True


    #
    def __init__(self, session, recorder_sref = None):
        self.session = session
        self.recorder_sref = None
        if fileExists(BRAND) or fileExists(BRANDP):
            skin = SKIN_PATH + '/xc_Player.xml'
        else:
            skin = SKIN_PATH + '/xc_PlayerTs.xml' 
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()        
        Screen.__init__(self, session) 
        InfoBarBase.__init__(self, steal_current_service=True)
        IPTVInfoBarShowHide.__init__(self)
        InfoBarSeek.__init__(self, actionmap='InfobarSeekActions')
        if STREAMS.disable_audioselector == False:
            InfoBarAudioSelection.__init__(self)
        InfoBarSubtitleSupport.__init__(self)
        self.InfoBar_NabDialog = Label()
        self.service = None
        self['state'] = Label('')
        self['cont_play'] = Label('')
        self['key_record'] = Label('Record')
        self.cont_play = STREAMS.cont_play

        self['cover'] = Pixmap()
        if fileExists(BRAND) or fileExists(BRANDP):
            self.picload = ePicLoad()
        #self.picload = ePicLoad()
        self.picfile = ''
        if recorder_sref:
            self.recorder_sref = recorder_sref
            self.session.nav.playService(recorder_sref)
        else:
            self.vod_entry = STREAMS.iptv_list[STREAMS.list_index]
            self.vod_url = self.vod_entry[4]
            self.title = self.vod_entry[1]
            self.descr = self.vod_entry[2]
            self.cover = self.vod_entry[3]
        self.TrialTimer = eTimer()
        try:
            self.TrialTimer_conn = self.TrialTimer.timeout.connect(self.trialWarning)
        except:
            self.TrialTimer.callback.append(self.trialWarning)
        print 'evEOF=%d' % iPlayableService.evEOF
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evSeekableStatusChanged: self.__seekableStatusChanged,
          iPlayableService.evStart: self.__serviceStarted,
          iPlayableService.evEOF: self.__evEOF})
        self['actions'] = HelpableActionMap(self, 'nStreamPlayerVOD', {'exitVOD': self.exit,
          'moreInfo': self.info2,
          'nextAR': self.nextAR,
          'prevAR': self.prevAR,
          'record': self.record, #rec
          'stopVOD': self.stopnew,
          'autoplay': self.timeshift_autoplay,
          'restartVideo': self.restartVideo,#Auto Reconnect mod         
          'prevVideo': self.prevVideo,
          'nextVideo': self.nextVideo,
          'help': self.help,
          'power': self.power_off}, -1)
        self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onFirstExecBegin.append(self.play_vod)
        self.onShown.append(self.setCover)  
        self.onPlayStateChanged.append(self.__playStateChanged)
        self.StateTimer = eTimer()
        try:
            self.StateTimer_conn = self.StateTimer.timeout.connect(self.trialWarning)
        except:
            self.StateTimer.callback.append(self.trialWarning)
        if STREAMS.trial != '':
            self.StateTimer.start(STREAMS.trial_time * 1000, True)
        self.state = self.STATE_PLAYING
        self.timeshift_url = None
        self.timeshift_title = None
        self.onShown.append(self.show_info)
        self.error_message = ''



    def setCover(self):
        try:
            vod_entry = STREAMS.iptv_list[STREAMS.list_index]
            self['cover'].instance.setPixmapFromFile(piclogo)
            if self.vod_entry[7] != '':
                if vod_entry[7].find('http') == -1:
                    self.picfile = PLUGIN_PATH + '/img/playlist/' + vod_entry[7]
                    self.decodeImage()
                    print 'LOCAL IMG VOD'
                else:
                    if STREAMS.img_loader == False:
                        self.picfile = '%s/poster.jpg' % STREAMS.images_tmp_path
                    else:
                        m = hashlib.md5()
                        m.update(self.vod_entry[7])
                        cover_md5 = m.hexdigest()
                        self.picfile = '%s/%s.jpg' % (STREAMS.images_tmp_path, cover_md5)
                    if os.path.exists(self.picfile) == False or STREAMS.img_loader == False:
                        downloadPage(self.vod_entry[7], self.picfile).addCallback(self.image_downloaded).addErrback(self.image_error)
                    else:
                        self.decodeImage()
        except Exception as ex:
            print ex
            print 'update COVER'


#

    def decodeImage(self):
        try:
            x = self['cover'].instance.size().width()
            y = self['cover'].instance.size().height()
            picture = self.picfile
            picload = self.picload
            sc = AVSwitch().getFramebufferScale()
            self.picload.setPara((x, y, sc[0], sc[1], 0, 0, '#00000000'))
            if fileExists(BRAND)or fileExists(BRANDP):
                self.picload.PictureData.get().append(boundFunction(self.showImage)) ## OPEN
            else:
                self.picload_conn = self.picload.PictureData.connect(self.showImage) ## CVS
            self.picload.startDecode(self.picfile)
        except Exception as ex:
            print ex
            print 'ERROR decodeImage'

    #
    def showImage(self, picInfo = None):
        self['cover'].show()
        try:
            ptr = self.picload.getData()
            if ptr:
                if fileExists(BRAND) or fileExists(BRANDP):
                    self['cover'].instance.setPixmap(ptr.__deref__())  ### OPEN

                else:
                    self['cover'].instance.setPixmap(ptr)                ### CVS
        except Exception as ex:
            print ex
            print 'ERROR showImage'

    #            

    def image_downloaded(self, id):
        self.decodeImage()


    #
    def downloadError(self, raw):
        try:
            system("cd / && cp -f " + piclogo + ' %s/poster.jpg' % STREAMS.images_tmp_path)



        except Exception as ex:
            print ex
            print 'exe downloadError'

    #        

    def showAfterSeek(self):
        if isinstance(self, IPTVInfoBarShowHide):
            self.doShow()



    def timeshift_autoplay(self):
        if self.timeshift_url:
            try:
                self.reference = eServiceReference(4097, 0, self.timeshift_url)
                self.reference.setName(self.timeshift_title)
                self.session.nav.playService(self.reference)
            except Exception as ex:
                print ex
                print 'EXC timeshift 1'

        else:
            if self.cont_play:
                self.cont_play = False
                self['cont_play'].setText('Auto Play OFF')

            else:
                self.cont_play = True
                self['cont_play'].setText('Auto Play ON')

            STREAMS.cont_play = self.cont_play



    # Key red  

    def timeshift(self):
        if self.timeshift_url:
            try:
                self.reference = eServiceReference(4097, 0, self.timeshift_url)
                self.reference.setName(self.timeshift_title)
                self.session.nav.playService(self.reference)
            except Exception as ex:
                print ex
                print 'EXC timeshift 2'

    # Key    

    def autoplay(self):
        if self.cont_play:
            self.cont_play = False
            self['cont_play'].setText('Auto Play OFF')
            self.session.open(MessageBox, 'Auto Play OFF', type=MessageBox.TYPE_INFO, timeout=3)
        else:
            self.cont_play = True
            self['cont_play'].setText('Auto Play ON')
            self.session.open(MessageBox, 'Auto Play ON', type=MessageBox.TYPE_INFO, timeout=3)
        STREAMS.cont_play = self.cont_play

    #
    def show_info(self):
        if STREAMS.play_vod == True:
            self['state'].setText(' PLAY     >')
        self.hideTimer.start(5000, True)
        if self.cont_play:
            self['cont_play'].setText('Auto Play ON')
        else:
            self['cont_play'].setText('Auto Play OFF')

    #


    def help(self):
        self.session.open(xc_help)

    # 2 - Auto Reconnect mod	
    def restartVideo(self):
        try:
            index = STREAMS.list_index
            video_counter = len(STREAMS.iptv_list)
            if index < video_counter:
                if STREAMS.iptv_list[index][4] != None:
                    STREAMS.list_index = index
                    self.player_helper()
        except Exception as ex:
            print ex
            print 'EXC restartVideo'
        return     

    #
    def nextVideo(self):
        try:
            index = STREAMS.list_index + 1
            video_counter = len(STREAMS.iptv_list)
            if index < video_counter:
                if STREAMS.iptv_list[index][4] != None:
                    STREAMS.list_index = index
                    self.player_helper()
        except Exception as ex:
            print ex
            print 'EXC nextVideo'


    #
    def prevVideo(self):
        try:
            index = STREAMS.list_index - 1
            if index > -1:
                if STREAMS.iptv_list[index][4] != None:
                    STREAMS.list_index = index
                    self.player_helper()
        except Exception as ex:
            print ex
            print 'EXC prevVideo'


    #
    def player_helper(self):
        self.show_info()
        if self.vod_entry:
            self.vod_entry = STREAMS.iptv_list[STREAMS.list_index]
            self.vod_url = self.vod_entry[4]
            self.title = self.vod_entry[1]
            self.descr = self.vod_entry[2]
        STREAMS.play_vod = False
        STREAMS.list_index_tmp = STREAMS.list_index
        self.setCover()
        self.play_vod()

    # Key rec    


    def record(self):
        try:
            if STREAMS.trial != '':
                self.session.open(MessageBox, 'Trialversion dont support this function', type=MessageBox.TYPE_INFO, timeout=10)
            else:
                movie = config.plugins.XCplugin.pthmovie.value #+ 'movie/'
                self.vod_entry = STREAMS.iptv_list[STREAMS.list_index]
                self.vod_url = self.vod_entry[4]
                self.title = self.vod_entry[1]
                self.descr = self.vod_entry[2]
                self.session.open(MessageBox, (_('BLUE = START PLAY RECORDED VIDEO')), type=MessageBox.TYPE_INFO, timeout=5)
                self.session.nav.stopService()
                self['state'].setText('RECORD')
                useragent = "--header='User-Agent: QuickTime/7.6.2 (qtver=7.6.2;os=Windows NT 5.1Service Pack 3)'"
                ende = 'mp4'
                if self.vod_entry[4].split('.')[-1].lower() == 'flv' or self.vod_url.split('.')[-1].lower() == 'flv':
                    ende = 'flv'
                title_translit = cyr2lat(self.title)
                filename = ASCIItranslit.legacyEncode(title_translit + '.') + ende
                #replace caratteri unicode
                filename = filename.replace('(', '_')
                filename = filename.replace(')', '_')
                filename = filename.replace('#', '')
                filename = filename.replace('+', '_')
                filename = filename.replace('\'', '_')
                filename = filename.replace("'", "_")
                filename = filename.encode('utf-8') 
                cmd = "wget %s -c '%s' -O '%s%s'" % (useragent, self.vod_url, movie, filename)
                JobManager.AddJob(downloadJob(self, cmd, movie + filename, self.title))
                self.createMetaFile(filename)
                self.LastJobView()

                self.timeshift_url = movie + filename 
                self.timeshift_title = '[REC] ' + self.title 
        except Exception as ex:
            print ex
            print 'ERROR record'

    #
    def LastJobView(self):
        currentjob = None
        for job in JobManager.getPendingJobs():
            currentjob = job
        if currentjob is not None:
            self.session.open(JobView, currentjob)
            
    #


    def createMetaFile(self, filename):
        try:
            movie = config.plugins.XCplugin.pthmovie.value #+ 'movie/'
            text = re.compile('<[\\/\\!]*?[^<>]*?>')
            text_clear = ''
            if self.vod_entry[2] != None:
                text_clear = text.sub('', self.vod_entry[2])
            serviceref = eServiceReference(4097, 0, movie + filename)
            metafile = open('%s%s.meta' % (movie, filename), 'w')  
            metafile.write('%s\n%s\n%s\n%i\n' % (serviceref.toString(),
             self.title.replace('\n', ''),
             text_clear.replace('\n', ''),
             time()))
            metafile.close()
        except Exception as ex:
            print ex
            print 'ERROR metaFile'

    #

    def __evEOF(self):
        if self.cont_play:
            self.restartVideo()


    #
    def __seekableStatusChanged(self):
        print 'seekable status changed!'


    #
    def __serviceStarted(self):
        self['state'].setText(' PLAY     >')
        self['cont_play'].setText('Auto Play OFF')
        self.state = self.STATE_PLAYING

    #
    def doEofInternal(self, playing):
        if not self.execing:
            return
        if not playing:
            return
        print 'doEofInternal EXIT OR NEXT'


    #
    def stopnew(self):
        if STREAMS.playhack == '':
            self.exit()

    #
    def power_off(self):
        self.close(1)

    #        
    def exit(self):
        if STREAMS.playhack == '':
            self.session.nav.stopService()
            STREAMS.play_vod = False
            self.session.nav.playService(self.oldService)            

        OnclearMem()
        self.close()

    #
    def nextAR(self):
        message = nextAR()
        self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=3)

    #
    def prevAR(self):
        message = prevAR()
        self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=3)

    #
    def trialWarning(self):
        self.StateTimer.start(STREAMS.trial_time * 1000, True)
        self.session.open(MessageBox, STREAMS.trial, type=MessageBox.TYPE_INFO, timeout=STREAMS.trial_time)

###################################            
            
    def info2(self):
        try:
        # # if STREAMS.xtream_e2portal_url and STREAMS.xtream_e2portal_url != '' or 'exampleserver.com:8888' :
            # if STREAMS.xtream_e2portal_url != '' or 'exampleserver.com:8888' :
                # selected_channel = self.channel_list[self.mlist.getSelectionIndex()] 

                if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/TMBD/plugin.pyo"):
                    from Plugins.Extensions.TMBD.plugin import TMBD         #TMDB v.8.3           
                    if selected_channel[2] != None:
                        text = re.compile('<[\\/\\!]*?[^<>]*?>')
                        text_clear = ''
                        text_clear = text.sub('', selected_channel[1])
                        text=text_clear

                        if '.ts' in str(selected_channel[4]):
                                HHHHH = self.show_more_info_Title(selected_channel)
                                self.session.open(TMBD, HHHHH, False)
                        else:
                                self.session.open(TMBD, text, False) 

                elif fileExists('/usr/lib/enigma2/python/Plugins/Extensions/tmdb/plugin.pyo'):
                    from Plugins.Extensions.tmdb.tmdb import tmdbScreen #tmdb 7.3

                    if selected_channel[2] != None:
                        text = re.compile('<[\\/\\!]*?[^<>]*?>')
                        text_clear = ''
                        text_clear = text.sub('', selected_channel[1])
                        text=text_clear
                        #================
                        global service
                        target = text
                        filtertmdb
                        robj = re.compile('|'.join(filtertmdb.keys()))
                        service = robj.sub(lambda m: filtertmdb[m.group(0)], target)
                        service = service.replace("("," ").replace(")","").replace("."," ").replace("[","").replace("]","").replace("-"," ").replace("_"," ").replace("+"," ")
                        service = re.sub("[0-9][0-9][0-9][0-9]", "", service)     
                        #================
                        if '.ts' in str(selected_channel[4]):
                            HHHHH = self.show_more_info_Title(selected_channel)
                            self.session.open(tmdbScreen, HHHHH, 2)
                        else:
                            self.session.open(tmdbScreen, service, 2)                                


                elif os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/IMDb/plugin.pyo'):
                    from Plugins.Extensions.IMDb.plugin import IMDB
                
                    if selected_channel[2] != None:
                        text = re.compile('<[\\/\\!]*?[^<>]*?>')
                        text_clear = ''
                        text_clear = text.sub('', selected_channel[1])
                        text=text_clear
                        if '.ts' in str(selected_channel[4]):
                            HHHHH = self.show_more_info_Title(selected_channel)
                            self.session.open(IMDB, HHHHH)
                        else:
                            self.session.open(IMDB, text)
                        
                elif selected_channel[2] != None:
                    text = re.compile('<[\\/\\!]*?[^<>]*?>')
                    text_clear = ''
                    text_clear = text.sub('', selected_channel[2])
                    self.session.open(xc_Epg, text_clear)
                else:
                    message = (_('No valid list '))
                    web_info(message) 
            # else:
                # message = (_('Please enter correct parameters in Config\n no valid list '))
                # web_info(message) 
                
        except Exception as ex:
            print ex
            print 'ERROR show_more_info'
            
    def show_more_info_Title(self,truc):
        text_clear_1 = ''
        try:
            if truc[1] != None:
                self.descr = truc
                text = re.compile('<[\\/\\!]*?[^<>]*?>')
                AAA = self.descr[2].split("]")[1:][0]
                BBB = AAA.split("(")[:1][0]
                text_clear_1 = text.sub('', BBB).replace(' ',' ').replace('\n',' ').replace('\t',' ').replace('\r',' ')
                # return
            else:
                text_clear_1 = 'No Even'
        except Exception as ex:
            text_clear = 'mkach'
        return text_clear_1            
############################################         
    #
    def __playStateChanged(self, state):
        self.hideTimer.start(5000, True)
        print 'self.seekstate[3] ' + self.seekstate[3]
        text = ' ' + self.seekstate[3]
        if self.seekstate[3] == '>':
            text = ' PLAY     >'
        if self.seekstate[3] == '||':
            text = 'PAUSE   ||'
        if self.seekstate[3] == '>> 2x':
            text = '    x2     >>'
        if self.seekstate[3] == '>> 4x':
            text = '    x4     >>'
        if self.seekstate[3] == '>> 8x':
            text = '    x8     >>'
        self['state'].setText(text)

        
    #

    def play_vod(self):
        try:
            if self.vod_url != '' and self.vod_url != None and len(self.vod_url) > 5:
                print '------------------------ MOVIE ------------------'
                self.session.nav.stopService()
                if config.plugins.XCplugin.services.value == 'Gstreamer':
                    self.reference = eServiceReference(4097, 0, self.vod_url)

                else:
                    self.reference = eServiceReference(5002, 0, self.vod_url)                 

                self.reference.setName(self.title)
                self.session.nav.playService(self.reference)
            else:
                if self.error_message:
                    self.session.open(MessageBox, self.error_message.encode('utf-8'), type=MessageBox.TYPE_ERROR)
                else:
                    self.session.open(MessageBox, 'NO VIDEOSTREAM FOUND'.encode('utf-8'), type=MessageBox.TYPE_ERROR)
                self.close()

        except Exception as ex:
            print 'vod play error 2'
            print ex

    #
    def parse_url(self):
        if STREAMS.playhack != '':
            self.vod_url = STREAMS.playhack
        print '++++++++++parse_url+++++++++++'
        try:
            url = self.vod_url
        except Exception as ex:
            print 'ERROR+++++++++++++++++parse_url++++++++++++++++++++++ERROR'
            print ex
        return self.vod_url

# TASK LIST


class xc_StreamTasks(Screen):

    def __init__(self, session):
        self.session = session
        skin = SKIN_PATH + '/xc_StreamTasks.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session) 
        self['shortcuts'] = ActionMap(['OkCancelActions', 'ColorActions'], {'ok': self.keyOK,
         'esc' : self.keyClose,
         'exit' : self.keyClose,
         'green': self.message1,
         'red': self.keyClose,
         'cancel': self.keyClose}, -1)
        self['movielist'] = List([])
        self["key_green"] = Label(_("Remove"))
        self["key_red"] = Label(_("Close"))
        global srefInit
        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
        srefInit = self.initialservice
        self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
        self.Timer = eTimer()
        try:
            self.Timer_conn = self.Timer.timeout.connect(self.TimerFire)
        except:
            self.Timer.callback.append(self.TimerFire)
        self.onLayoutFinish.append(self.layoutFinished)
        self.onClose.append(self.__onClose)


    #
    def __onClose(self):
        del self.Timer


    #
    def layoutFinished(self):
        self.Timer.startLongTimer(2)


    #
    def TimerFire(self):
        self.Timer.stop()
        self.rebuildMovieList()

    #

    def rebuildMovieList(self):
        self.movielist = []
        self.getTaskList()
        self.getMovieList()
        self['movielist'].setList(self.movielist)
        self['movielist'].updateList(self.movielist)


    #

    def getTaskList(self):
        for job in JobManager.getPendingJobs():
            self.movielist.append((job,
             job.name,
             job.getStatustext(),
             int(100 * job.progress / float(job.end)),
             str(100 * job.progress / float(job.end)) + '%'))

        if len(self.movielist) >= 1:
            self.Timer.startLongTimer(10)

    #

    def getMovieList(self):
        movie = config.plugins.XCplugin.pthmovie.value #+ 'movie/'
        filelist = listdir(movie)

        if filelist is not None:
            filelist.sort()
            for filename in filelist:
                if path.isfile(movie + filename) and filename.endswith('.meta') is False:            
                    if '.m3u' in filename:
                        continue
                    self.movielist.append(('movie', filename, _('Finished'), 100, '100%'))
    #    
    def keyOK(self):
        movie = config.plugins.XCplugin.pthmovie.value #+ 'movie/'
        current = self['movielist'].getCurrent()
        if current:
            if current[0] == 'movie':
                sref = eServiceReference(4097, 0, movie + current[1])            
                sref.setName(current[1])
                self.session.open(xc_Player, sref)
            else:
                job = current[0]
                self.session.openWithCallback(self.JobViewCB, JobView, job)

    #
    def JobViewCB(self, why):
        pass

        
    def keyClose(self):
        self.session.nav.stopService()
        self.session.nav.playService(srefInit)
        self.close()
       
    #
    def message1(self):
        movie = config.plugins.XCplugin.pthmovie.value #+ 'movie/'
        current = self['movielist'].getCurrent()
        sel = movie + current[1]
        dom = sel
        self.session.openWithCallback(self.callMyMsg1,MessageBox,_("Do you want to remove %s ?") % dom, MessageBox.TYPE_YESNO, timeout = 15, default = False)       



    def callMyMsg1(self, result):
        if result:
            movie = config.plugins.XCplugin.pthmovie.value #+ 'movie/'
            current = self['movielist'].getCurrent()
            sel = movie + current[1]
            os.remove(sel)
            self.session.open(MessageBox, sel + '   has been successfully deleted\nwait time to refresh the list...', MessageBox.TYPE_INFO, timeout=5)            
            self.onShown.append(self.rebuildMovieList)         

#
class html_parser_moduls():

    def __init__(self):
        self.next_page_url = ''
        self.next_page_text = ''
        self.prev_page_url = ''
        self.prev_page_text = ''
        self.playlistname = ''
        self.error = ''


    #
    def reset_buttons(self):
        self.next_page_url = None
        self.next_page_text = ''
        self.prev_page_url = None
        self.prev_page_text = ''
        return

    #
    def get_list(self, url):
        debug(url, 'MODUL URL: ')
        self.reset_buttons()

#
def xcm3ulistEntry(download):
    res = [download]
    white = 16777215
    blue = 79488
    col = 16777215
    backcol = 1.923232
    # res.append(MultiContentEntryText(pos=(0, 0), size=(1200, 40), text=download, color=col, color_sel=white, backcolor=backcol, backcolor_sel=blue))
    res.append(MultiContentEntryText(pos=(0, 0), size=(1200, 40), text=download, color=col, color_sel=white, backcolor_sel=blue))
    return res


#
def m3ulistxc(data, list):
    icount = 0
    mlist = []
    for line in data:
        name = data[icount]
        mlist.append(xcm3ulistEntry(name))
        icount = icount + 1
    list.setList(mlist)



#

class xcM3UList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        if HD > 1280:
            self.l.setItemHeight(45)
            textfont = int(32)
            self.l.setFont(0, gFont('Regular', textfont))
        else:
            self.l.setItemHeight(22)
            textfont = int(16)
            self.l.setFont(0, gFont('Regular', textfont))


# # PLAYER

class xc_Play(Screen):
    def __init__(self, session):

        self.session = session
        skin = SKIN_PATH + '/xc_M3uLoader.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()           
        Screen.__init__(self, session)
        self.list = []
        self['list'] = xcM3UList([])

        global srefInit
        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
        srefInit = self.initialservice


        movie = config.plugins.XCplugin.pthmovie.value #+ 'movie/'
        self.name = movie
        self['path'] = Label(_('Put .m3u Files in Folder %s') % movie)
        self['version'] = Label(_(' V.%s Lite' % version))

        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Remove"))
        self["key_yellow"] = Label(_("Create") + " Bouquet")      
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'MenuActions', 'TimerEditActions'], {
         'red': self.cancel,
         'green': self.message1,
         'yellow': self.message2,
         'cancel': self.cancel,
         'ok': self.runList}, -2)

        self.onLayoutFinish.append(self.openList)

    #
    def openList(self):
        self.names = []
        self.Movies = []
        path = config.plugins.XCplugin.pthmovie.value #+ 'movie/'
        # path = self.name
        AA = ['.mkv','.mp4','.avi','.m3u']
        for root, dirs, files in os.walk(path):
            for name in files:
                for x in AA:
                    if not x in name:
                        continue
                        pass
                    self.names.append(name)
                    self.Movies.append(root +'/'+ name)
        pass
        m3ulistxc(self.names, self['list'])

        
    def runList(self):
        idx = self['list'].getSelectionIndex()
        path = self.Movies[idx]
        if idx == -1 or None:
            return
        else:
            name = path
            if '.m3u' in name : 
                self.session.open(xc_M3uPlay, name)
                return
            else:

                name = self.names[idx]            
                sref = eServiceReference(4097, 0, path)
                sref.setName(name)
                self.session.openWithCallback(self.backToIntialService,xc_Player, sref)       
                return
                
    def backToIntialService(self, ret = None):
        self.session.nav.stopService()
        self.session.nav.playService(self.initialservice)
    #
    def cancel(self):
        self.close()

        
    #
    def message1(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:


            return
        else:
            idx = self['list'].getSelectionIndex()
            dom = self.name + self.names[idx]
            self.session.openWithCallback(self.callMyMsg1,MessageBox,_("Do you want to remove: %s ?")% dom, MessageBox.TYPE_YESNO, timeout = 15, default = False)       

    #
    def callMyMsg1(self, result):
        if result:
            idx = self['list'].getSelectionIndex()
            dom = self.name + self.names[idx]
            if fileExists(dom):
                os.remove(dom)
                self.session.open(MessageBox, dom +'   has been successfully deleted\nwait time to refresh the list...', MessageBox.TYPE_INFO, timeout=5)
                del self.names[idx]
                m3ulistxc(self.names, self['list'])
            else:
                self.session.open(MessageBox, dom +'   not exist!', MessageBox.TYPE_INFO, timeout=5)
    def message2(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None :
            return

        path = self.Movies[idx]
        name = path# + self.names[idx]
        if '.m3u' in name : 

            idx = self['list'].getSelectionIndex()
            dom = self.names[idx]
            self.session.openWithCallback(self.convert,MessageBox,_("Do you want to Convert %s to favorite .tv ?")% dom, MessageBox.TYPE_YESNO, timeout = 15, default = False)  
        else:
            return
            
    #


    def convert(self, result):
        idx = self['list'].getSelectionIndex()
        if result:        
            name = self.names[idx]
            self.convert_bouquet()
            return           
        else:
            return


    #
    def convert_bouquet(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            path = config.plugins.XCplugin.pthmovie.value #+ 'movie/'
            name = path + self.names[idx]
            namel = self.names[idx]
            # pth = self.name
            xcname = 'userbouquet.%s.tv' % namel.replace('.m3u', '').replace(' ', '')
            self.iConsole = iConsole()
            desk_tmp = hls_opt = ''
            in_bouquets = 0

            if os.path.isfile('/etc/enigma2/%s' % xcname):
                os.remove('/etc/enigma2/%s' % xcname)
            with open('/etc/enigma2/%s' % xcname, 'w') as outfile:
                outfile.write('#NAME %s\r\n' % namel.replace('.m3u', '').replace(' ', '').capitalize())            

                for line in open('%s' % name.encode('utf-8')):
                    if line.startswith('http://'):
                        outfile.write('#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s' % line.replace(':', '%3a'))
                        outfile.write('#DESCRIPTION %s' % desk_tmp)
                    elif line.startswith('#EXTINF'):
                        desk_tmp = '%s' % line.split(',')[-1]
                    elif '<stream_url><![CDATA' in line:
                        outfile.write('#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s\r\n' % line.split('[')[-1].split(']')[0].replace(':', '%3a'))
                        outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
                    elif '<title>' in line:
                        if '<![CDATA[' in line:
                            desk_tmp = '%s\r\n' % line.split('[')[-1].split(']')[0]
                        else:
                            desk_tmp = '%s\r\n' % line.split('<')[1].split('>')[1]

                outfile.close()
                self.mbox = self.session.open(MessageBox, _('Check on favorites lists...'), MessageBox.TYPE_INFO, timeout=5)

            if os.path.isfile('/etc/enigma2/bouquets.tv'):
                for line in open('/etc/enigma2/bouquets.tv'):
                    if xcname in line:
                        in_bouquets = 1

                if in_bouquets is 0:
                    if os.path.isfile('/etc/enigma2/%s' % xcname) and os.path.isfile('/etc/enigma2/bouquets.tv'):
                        remove_line('/etc/enigma2/bouquets.tv', xcname)
                        with open('/etc/enigma2/bouquets.tv', 'a') as outfile:
                            outfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % xcname)
                outfile.close()
            self.mbox = self.session.open(MessageBox, _('Reload Playlists in progress...') + '\n\n\n' + _('wait please...'), MessageBox.TYPE_INFO, timeout=8)
            ReloadBouquet()



#            
class xc_M3uPlay(Screen):
    def __init__(self, session, name):

        self.session = session
        skin = SKIN_PATH + '/xc_M3uPlay.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()  
        Screen.__init__(self, session) 
        self.list = []
        self['list'] = xcM3UList([])
        self['version'] = Label(_(' V.%s Lite' % version))
        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Play"))
        self['key_yellow'] = Label(_('OK') + ': ' + _('Preview') )         
        # self['okpreview'] = Label(_('OK') + ': ' + _('Preview') )           
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'TimerEditActions'], {
         'red': self.close,
         'ok': self.runPreview,
         # 'blue': self.runChannel,  
         'yellow': self.runPreview,         
         'green': self.runChannel,
         'cancel': self.cancel}, -2)
        self['live'] = Label('')
        self['live'].setText('')
        path = config.plugins.XCplugin.pthmovie.value #+ 'movie/'
        self.name = name
        self.onLayoutFinish.append(self.playList)


    #
    def playList(self):
        self.names = []
        self.urls = []
        try:
            if fileExists(self.name):
                f1 = open(self.name, 'r+')
                fpage = f1.read()
                regexcat = 'EXTINF.*?,(.*?)\\n(.*?)\\n'
                match = re.compile(regexcat, re.DOTALL).findall(fpage)
                for name, url in match:
                    url = url.replace(' ', '')
                    url = url.replace('\\n', '')
                    self.names.append(name)
                    self.urls.append(url)
                m3ulistxc(self.names, self['list'])
                self['live'].setText(str(len(self.names)) + ' Stream')
        except Exception as ex:
            print ex
            print 'ex playList' 

            
    #
    def runChannel(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            name = self.names[idx]
            url = self.urls[idx]
            self.session.open(M3uPlay2, name, url)
            return



            
    def runPreview(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            name = self.names[idx]
            url = self.urls[idx]
            url = url.replace(':', '%3a')
            self.url = url
            self.name = name
        

            if ".ts" in self.url: 
                ref = '4097:0:1:0:0:0:0:0:0:0:' + url
                #ref = '1:0:1:0:0:0:0:0:0:0:' + url                
                print "ref ts= ", ref        
        
            else:
                if config.plugins.XCplugin.services.value == 'Gstreamer':
                    ref = '4097:0:1:0:0:0:0:0:0:0:' + url
                    print "ref 4097= ", ref
                else:
                    ref = '5002:0:1:0:0:0:0:0:0:0:' + url
                    print "ref 5002= ", ref
            sref = eServiceReference(ref)
            sref.setName(self.name)
            self.session.nav.stopService()
            self.session.nav.playService(sref)
            
    def cancel(self):
        self.session.nav.stopService()
        self.session.nav.playService(srefInit)
        self.close()

class M3uPlay2(Screen, InfoBarMenu, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarShowHide): #, InfoBarAudioSelection, InfoBarSubtitleSupport):
    # STATE_IDLE = 0
    # STATE_PLAYING = 1
    # STATE_PAUSED = 2
    # ENABLE_RESUME_SUPPORT = True
    # ALLOW_SUSPEND = True

    def __init__(self, session, name, url):
        Screen.__init__(self, session)
        self.skinName = 'MoviePlayer'
        title = 'Play Stream'
        self['list'] = MenuList([])

        # if STREAMS.disable_audioselector == False:
            # InfoBarAudioSelection.__init__(self)
        # InfoBarSubtitleSupport.__init__(self)
        InfoBarMenu.__init__(self)
        InfoBarNotifications.__init__(self)
        InfoBarBase.__init__(self)
        InfoBarShowHide.__init__(self)
        # InfoBarSubtitleSupport.__init__(self)
        # InfoBarAudioSelection.__init__(self)
        self['actions'] = ActionMap(['WizardActions',
         'MoviePlayerActions',
         'MovieSelectionActions',
         'MediaPlayerActions',
         'EPGSelectActions',
         'MediaPlayerSeekActions',
         'SetupActions',
         'ColorActions',
         'InfobarShowHideActions',
         'InfobarActions',
         'InfobarSeekActions'], {'leavePlayer': self.cancel,
         'showEventInfo': self.showVideoInfo,
         'stop': self.leavePlayer,
         'cancel': self.cancel,         
         'back': self.cancel}, -1)
        self.allowPiP = False
        InfoBarSeek.__init__(self, actionmap='InfobarSeekActions')       
        url = url.replace(':', '%3a')  
        self.url = url
        self.name = name
        # self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.openPlay)

        
    def openPlay(self):
        url = self.url
        if config.plugins.XCplugin.services.value == 'Gstreamer':
            ref = '4097:0:1:0:0:0:0:0:0:0:' + url
            print "ref1= ", ref  

        else:
            ref = '5002:0:1:0:0:0:0:0:0:0:' + url          
            print "ref2= ", ref
        sref = eServiceReference(ref)
        sref.setName(self.name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)
    def keyNumberGlobal(self, number):
        self['text'].number(number)
    def cancel(self):
        self.session.nav.stopService()
        self.session.nav.playService(srefInit)
        self.close()

    #
    def ok(self):
        if self.shown:
            self.hideInfobar()
        else:
            self.showInfobar()

    #


    def keyLeft(self):
        self['text'].left()

    #


    def keyRight(self):
        self['text'].right()


    #

    def showVideoInfo(self):
        if self.shown:
            self.hideInfobar()
        if self.infoCallback is not None:
            self.infoCallback()
        return

    #


    def leavePlayer(self):
        self.close()


# HELP  
class xc_help(Screen): 
    def __init__(self, session):

        self.session = session
        skin = SKIN_PATH + '/xc_help.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)          
        self['version'] = Label(_(' V.%s Lite' % version))
        self['key_red'] = Label(_("Back"))
        self["helpdesc"] = Label()
        self["helpdesc2"] = Label()        
        self["infocredits"] = Label()     
        self['actions'] = HelpableActionMap(self, 'xc_help', {"cancel": self.close, 'key_red': self.close}, -1) 
        self.onLayoutFinish.append(self.finishLayout)

    #
    def finishLayout(self):
        self["helpdesc"].setText(self.gethelpdesc())
        self["helpdesc2"].setText(self.gethelpdesc2())        
        self["infocredits"].setText(self.getinfocredits())

    #
    def gethelpdesc(self):
        # conthelp  = " TV               >  Reload Channels from Playlist\n"
        conthelp = " Menu / 8             >  Setup Options\n"         
        conthelp += " Info / 5              >  Show Info User Account\n"        
        conthelp += " Help                  >  This !!!\n" 
        conthelp += " Pvr/FILELIST/7   >  Open Media Folder\n"
        conthelp += " 3                       >  Open Movie Folder\n"        
        conthelp += " Rec                   >  Start Download or Record Select Channel:\n" 
        conthelp += "                              Set Live Player Active in Setting: set No for Record Live\n" 
        conthelp += " Key_Red             >  Close XC-Lite\n"
        conthelp += " Key_Green          >  Create XC Live/VOD Bouquets\n"
        conthelp += " Key_Yellow         >  Remove XC Bouquets\n"
        conthelp += " Key_Blue            >  Load M3U playlist from file\n" 
        conthelp += "                             see settings to change location\n"
        return conthelp        

    def gethelpdesc2(self):        
        conthelp = "--> MENU CONFIG\n"
        conthelp += " If you have a file /etc/enigma2/iptv.sh format:\n" 
        conthelp += ' USERNAME="xxxxxxxxxx"\n'         
        conthelp += ' PASSWORD="yyyyyyyyy"\n'
        conthelp += ' url="http://server:port/xxxxyyyyyzzzzz"\n'
        conthelp += " Import with Yellow Button this file iptv.sh\n"
        conthelp += "--> OPENSERVER (BLUE BUTTON):\n "  
        conthelp += "Put in a file /tmp/xc.txt and Import from Blue Button\n"
        conthelp += " host:port ( host without http:// )\n" 
        conthelp += " user\n"         
        conthelp += " password\n"
        conthelp += "SELECT YOUR FILE .XML AND SAVE CONFIG"        
        return conthelp

    #
    def getinfocredits(self):
        conthelp =  'XCplugin by Xtream-Codes Mod v. %s Lite\n' % version
        conthelp += 'Current Service Type: %s\n' % config.plugins.XCplugin.services.value 
        conthelp += 'LivePlayer Active %s\n' % config.plugins.XCplugin.LivePlayer.value        
        conthelp += 'Config Folder file xml %s\n' % config.plugins.XCplugin.pthxmlfile.value
        conthelp += 'Config Media Folder %smovie/\n' % config.plugins.XCplugin.pthmovie.value
        conthelp += 'Conversion type Output %s\n' % config.plugins.XCplugin.typem3utv.value
        conthelp += " *** Xc-Plugin is a original code by Dave Sully, Doug Mackay ***\n"        
        conthelp += " *** XC-Lite is a Mod by Lululla & mmark ***\n"        
        conthelp += " *** thanks aime_jeux and other friends ***\n"          
        conthelp += "*** Please report any bugs you find ***"
        return conthelp   


           
#
def debug(obj, text = ''):
    # print datetime.fromtimestamp(time()).strftime('[%H:%M:%S]')
    print '%s' % text + ' %s\n' % obj




conversion = {unicode('\xd0\xb0'): 'a',
 unicode('\xd0\x90'): 'A',
 unicode('\xd0\xb1'): 'b',
 unicode('\xd0\x91'): 'B',
 unicode('\xd0\xb2'): 'v',
 unicode('\xd0\x92'): 'V',
 unicode('\xd0\xb3'): 'g',
 unicode('\xd0\x93'): 'G',
 unicode('\xd0\xb4'): 'd',
 unicode('\xd0\x94'): 'D',
 unicode('\xd0\xb5'): 'e',
 unicode('\xd0\x95'): 'E',
 unicode('\xd1\x91'): 'jo',
 unicode('\xd0\x81'): 'jo',
 unicode('\xd0\xb6'): 'zh',
 unicode('\xd0\x96'): 'ZH',
 unicode('\xd0\xb7'): 'z',
 unicode('\xd0\x97'): 'Z',
 unicode('\xd0\xb8'): 'i',
 unicode('\xd0\x98'): 'I',
 unicode('\xd0\xb9'): 'j',
 unicode('\xd0\x99'): 'J',
 unicode('\xd0\xba'): 'k',
 unicode('\xd0\x9a'): 'K',
 unicode('\xd0\xbb'): 'l',
 unicode('\xd0\x9b'): 'L',
 unicode('\xd0\xbc'): 'm',
 unicode('\xd0\x9c'): 'M',
 unicode('\xd0\xbd'): 'n',
 unicode('\xd0\x9d'): 'N',
 unicode('\xd0\xbe'): 'o',
 unicode('\xd0\x9e'): 'O',
 unicode('\xd0\xbf'): 'p',
 unicode('\xd0\x9f'): 'P',
 unicode('\xd1\x80'): 'r',
 unicode('\xd0\xa0'): 'R',
 unicode('\xd1\x81'): 's',
 unicode('\xd0\xa1'): 'S',
 unicode('\xd1\x82'): 't',
 unicode('\xd0\xa2'): 'T',
 unicode('\xd1\x83'): 'u',
 unicode('\xd0\xa3'): 'U',
 unicode('\xd1\x84'): 'f',
 unicode('\xd0\xa4'): 'F',
 unicode('\xd1\x85'): 'h',
 unicode('\xd0\xa5'): 'H',
 unicode('\xd1\x86'): 'c',
 unicode('\xd0\xa6'): 'C',
 unicode('\xd1\x87'): 'ch',
 unicode('\xd0\xa7'): 'CH',
 unicode('\xd1\x88'): 'sh',
 unicode('\xd0\xa8'): 'SH',
 unicode('\xd1\x89'): 'sh',
 unicode('\xd0\xa9'): 'SH',
 unicode('\xd1\x8a'): '',
 unicode('\xd0\xaa'): '',
 unicode('\xd1\x8b'): 'y',
 unicode('\xd0\xab'): 'Y',
 unicode('\xd1\x8c'): 'j',
 unicode('\xd0\xac'): 'J',
 unicode('\xd1\x8d'): 'je',
 unicode('\xd0\xad'): 'JE',
 unicode('\xd1\x8e'): 'ju',
 unicode('\xd0\xae'): 'JU',
 unicode('\xd1\x8f'): 'ja',
 unicode('\xd0\xaf'): 'JA'}



#
def cyr2lat(text):
    i = 0
    text = text.strip(' \t\n\r')
    text = unicode(text)
    retval = ''
    bukva_translit = ''
    bukva_original = ''
    while i < len(text):
        bukva_original = text[i]
        try:
            bukva_translit = conversion[bukva_original]
        except:
            bukva_translit = bukva_original


        i = i + 1
        retval += bukva_translit
    return retval



class xc_Epg(Screen): 

    def __init__(self, session, text_clear):

        self.session = session
        skin = SKIN_PATH + '/xc_epg.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)       
        text_clear = text_clear        
        self['version'] = Label(_(' V.%s Lite' % version))
        self['key_red'] = Label(_("Back"))
        self["text_clear"] = Label(text_clear)        
        self['actions'] = HelpableActionMap(self, 'xc_epg', {"cancel": self.exit, 'key_red': self.exit }, -1) 


    #
    def exit(self):
            self.close()



#
class OpenServer(Screen):
    def __init__(self, session):
        global STREAMS
        self.session = session

        if fileExists(BRAND) or fileExists(BRANDP):
            skin = SKIN_PATH + '/xc_OpenServer.xml'
        else:
            skin = SKIN_PATH + '/xc_OpenServerCvs.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()   
        Screen.__init__(self, session)
        self.list = []
        self['list'] = xcM3UList([]) 
        self['version'] = Label(_(' V.%s Lite' % version))
        self['playlist'] = Label('')
        self['key_red'] = Label(_("Back"))
        self["key_green"] = Label(_("Rename"))        
        self["key_yellow"] = Label(_("Remove"))
        self['key_blu'] = Label(_("Import") + "Server")
        self['key_blu'].hide()
        if fileExists('/tmp/xc.txt'):
            self['key_blu'].show()
        self['live'] = Label('')
        self['live'].setText('')
        self.name = config.plugins.XCplugin.pthxmlfile.value #+ '/'
        self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
        self['actions'] = HelpableActionMap(self, 'OpenServer', {
         # 'iptv': self.importIptv_sh,
         'ok': self.selectlist,
         # 'selectlist': self.selectlist,
         'remove': self.message1,
         'red': self.goMain,
         'cancel': self.goMain,
         'import': self.ImportInfosServer,         
         'exit': self.goMain,
         'rename': self.rename,
         'help': self.help}, -1)   
        self.onLayoutFinish.append(self.openList)    

    # def importIptv_sh(self):
        # STREAMS.iptv_sh()
        
    def ImportInfosServer(self):
            if fileExists('/tmp/xc.txt'):
            
                f = file('/tmp/xc.txt',"r")
                chaine = f.readlines()
                f.close()
                url = chaine[0].replace('\n','').replace('\t','').replace('\r','')
                user = chaine[1].replace('\n','').replace('\t','').replace('\r','').replace(':','_')
                pswrd = chaine[2].replace('\n','').replace('\t','').replace('\r','')
                filesave = 'xc_' + user + '.xml' 
                
                filesave = filesave.replace(':','_')
                filesave = filesave.lower()
                
                pth= config.plugins.XCplugin.pthxmlfile.value 
                print 'pth:', pth                
                f5 = open(pth + filesave, "w") 
                f5.write(str('<?xml version="1.0" encoding="UTF-8" ?>\n' + '<items>\n' + '<plugin_version>' + currversion + '</plugin_version>\n' +'<xtream_e2portal_url><![CDATA[http://'+ url + '/enigma2.php]]></xtream_e2portal_url>\n' + '<username>' + user + '</username>\n' + '<password>' + pswrd + '</password>\n'+ '</items>'))
                f5.close()
                self.mbox = self.session.open(MessageBox, _('File saved to %s !' % filesave ), MessageBox.TYPE_INFO, timeout=5)
                config.plugins.XCplugin.hostaddress.setValue(url)
                config.plugins.XCplugin.user.setValue(user)
                config.plugins.XCplugin.passw.setValue(pswrd) 
                self.updateConfig()                
                #  self.close(STREAMS.get_list(STREAMS.xtream_e2portal_url))   
                # # self.onLayoutFinish.append(self.openList)
                
            else:
                self.mbox = self.session.open(MessageBox, _('File not found /tmp/xc.txt!'), MessageBox.TYPE_INFO, timeout=5)                

    #


    def openList(self):
        self.names = []
        path = self.name
        # pass

        for root, dirs, files in os.walk(path):
            files.sort()
            for name in files:
                if not ".xml" in name:
                    continue
                    pass
                self.names.append(name)
        pass
        m3ulistxc(self.names, self['list'])

        self['live'].setText(str(len(self.names)) + ' Team')        
        self.updateConfig()



    def updateConfig(self):        
        global STREAMS
        STREAMS = iptv_streamse()
        STREAMS.read_config()
        # STREAMS.get_list(STREAMS.xtream_e2portal_url)
        # self['playlist'].setText(STREAMS.playlistname) 

        if STREAMS.xtream_e2portal_url and STREAMS.xtream_e2portal_url != 'exampleserver.com:8888' :
            STREAMS.get_list(STREAMS.xtream_e2portal_url)
            self['playlist'].setText(STREAMS.playlistname)    

                


    def selectlist(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            idx = self['list'].getSelectionIndex()
            dom = self.name + '/' + self.names[idx]        
            tree = ElementTree()
            xml = tree.parse(dom)
            xtream_e2portal_url = xml.findtext('xtream_e2portal_url')
            self.xtream_e2portal_url = xtream_e2portal_url
            self.url = self.xtream_e2portal_url
            host = self.url.replace('http://','').replace('/enigma2.php','')
            username = xml.findtext('username')
            if username and username != '':
                self.username = username
            password = xml.findtext('password')
            if password and password != '':
                self.password = password
            config.plugins.XCplugin.hostaddress.setValue(host)
            config.plugins.XCplugin.user.setValue(self.username)
            config.plugins.XCplugin.passw.setValue(self.password) 

            global STREAMS
            STREAMS = iptv_streamse()
            STREAMS.read_config()
            # self.close(STREAMS.get_list(STREAMS.xtream_e2portal_url))            
            if STREAMS.xtream_e2portal_url and STREAMS.xtream_e2portal_url != 'exampleserver.com:8888' :
                self.close(STREAMS.get_list(STREAMS.xtream_e2portal_url))
            else:
                self.close()  



            
    #

    def goMain(self):
        clear_img()    
        global STREAMS
        STREAMS = iptv_streamse()
        STREAMS.read_config()
        # self.close(STREAMS.get_list(STREAMS.xtream_e2portal_url))      
        if STREAMS.xtream_e2portal_url and STREAMS.xtream_e2portal_url != 'exampleserver.com:8888' :
            self.close(STREAMS.get_list(STREAMS.xtream_e2portal_url))
        else:
            self.close() 

    #
    def message1(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return

        else:
            idx = self['list'].getSelectionIndex()
            dom = self.name + '/' + self.names[idx]
            self.session.openWithCallback(self.removeXml,MessageBox,_("Do you want to remove: %s ?")% dom, MessageBox.TYPE_YESNO, timeout = 15, default = False)       
    # #
    def removeXml(self, result):
        if result:
            idx = self['list'].getSelectionIndex()
            dom = self.name + '/' + self.names[idx]
            if fileExists(dom):
                os.remove(dom)
                self.session.open(MessageBox, dom +'   has been successfully deleted\nwait time to refresh the list...', MessageBox.TYPE_INFO, timeout=5)
                del self.names[idx]
                m3ulistxc(self.names, self['list'])
            else:
                self.session.open(MessageBox, dom +'   not exist!', MessageBox.TYPE_INFO, timeout=5)


    #
    def rename(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            dom = self.name + '/' + self.names[idx]
            dim = self.names[idx]
            if dom is None:
                return
            else:
                global NewName
                NewName = str(dim)
                self.session.openWithCallback(self.newname, VirtualKeyBoard, text=str(dim))
            return   
            
    def newname(self, word):
        if word is None:
            pass
        else:
            oldfile = self.name + '/' + NewName
            newfile = self.name + '/' + word 
            newnameConf = "mv " + "'" + oldfile + "'" + " " + "'" + newfile + "'"
            self.session.open(Console, _('XCplugin Console Rename: %s') % oldfile, ['%s' % newnameConf], closeOnSuccess=True)          
            self.onShown.append(self.openList)

    #


    def help(self):
        self.session.open(xc_help)



# XC_IPtv_player
class nIPTVplayer(Screen, InfoBarBase, IPTVInfoBarShowHide, InfoBarAudioSelection, InfoBarSubtitleSupport):

    def __init__(self, session):
        self.session = session

        if fileExists(BRAND) or fileExists(BRANDP):


            skin = SKIN_PATH + '/xc_iptv_player.xml'
        else:
            skin = SKIN_PATH + '/xc_iptv_playerTs.xml'         
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        global STREAMS        
        InfoBarBase.__init__(self, steal_current_service=True)
        IPTVInfoBarShowHide.__init__(self)
        if STREAMS.disable_audioselector == False:
            InfoBarAudioSelection.__init__(self)
        InfoBarSubtitleSupport.__init__(self)
        self['channel_name'] = Label('')
        self['picon'] = Pixmap()
        if fileExists(BRAND) or fileExists(BRANDP):
           self.picload = ePicLoad()
        #self.picload = ePicLoad()
        self.picfile = ''
        self['programm'] = Label('')
        self.InfoBar_NabDialog = Label('')
        self.session = session
        self.channel_list = STREAMS.iptv_list
        self.index = STREAMS.list_index
        STREAMS.play_vod = False
        self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onFirstExecBegin.append(self.play_channel)
        self['actions'] = HelpableActionMap(self, 'nStreamPlayerIPTV', {'toChListIPTV': self.exit,
         'help': self.help,
         'moreInfo': self.info2,
         'prevChannelIPTV': self.prevChannel,
         'nextChannelIPTV': self.nextChannel,
         'nextAR': self.nextAR,
         'prevAR': self.prevAR,
         'power': self.power_off}, -1)
        self.StateTimer = eTimer()
        try:
            self.StateTimer_conn = self.StateTimer.timeout.connect(self.trialWarning)
        except:
            self.StateTimer.callback.append(self.trialWarning)
        if STREAMS.trial != '':
            self.StateTimer.start(STREAMS.trial_time * 1000, True) 


    #
    def nextAR(self):
        message = nextAR()
        self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=3)



    #
    def prevAR(self):
        message = prevAR()
        self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=3)


    #
    def trialWarning(self):
        self.StateTimer.start(STREAMS.trial_time * 1000, True)
        self.session.open(MessageBox, STREAMS.trial, type=MessageBox.TYPE_INFO, timeout=STREAMS.timeout_time)


    #


    def exit(self):
        if STREAMS.playhack == '':
            self.session.nav.stopService()
            self.session.nav.playService(self.oldService)            
        OnclearMem()
        self.close()

    #

    def power_off(self):
        self.close(1)


    #
    def play_channel(self):
        try:

            selected_channel = STREAMS.iptv_list[self.index]
            self['channel_name'].setText(selected_channel[1])
            text = re.compile('<[\\/\\!]*?[^<>]*?>')
            text_clear = ''
            if selected_channel[2] != None:
                text_clear = text.sub('', selected_channel[2])
            self['programm'].setText(text_clear)

            try:
                #self['picon'].instance.setPixmapFromFile('%s/poster.jpg' % STREAMS.images_tmp_path)
                debug(selected_channel[3], 'selected_channel[3] IPTVLOGO')
                if selected_channel[3] != '':
                    if selected_channel[3].find('http') == -1:
                        self.picfile = selected_channel[3]
                        self.decodeImage()
                        print 'LOCAL IPTV IMG'
                    else:
                        if STREAMS.img_loader == False:
                            self.picfile = '%s/poster.jpg' % STREAMS.images_tmp_path
                        else:
                            m = hashlib.md5()
                            m.update(selected_channel[3])
                            cover_md5 = m.hexdigest()
                            self.picfile = '%s/%s.jpg' % (STREAMS.images_tmp_path, cover_md5)
                        if os.path.exists(self.picfile) == False or STREAMS.img_loader == False:
                            downloadPage(selected_channel[3], self.picfile).addCallback(self.image_downloaded).addErrback(self.downloadError)
                            
                        else:
                            self.decodeImage()
            except Exception as ex:
                print ex
                print 'update PICON'
            try:
                esr_id = 1         
                url = selected_channel[4]
                self.session.nav.stopService()
                if url != '' and url != None:

                    sref = eServiceReference(esr_id, 0, url)
                    sref.setName(selected_channel[1])
                    try:
                        self.session.nav.playService(sref)
                    except Exception as ex:
                        print 'play_channel'
                        print ex

            except Exception as ex:
                print ex
                print 'play_channel1'

        except Exception as ex:
            print ex
            print 'play_channel2'


    #           
    def nextChannel(self):
        index = self.index
        index += 1
        if index == len(self.channel_list):
            index = 0
        if self.channel_list[index][4] != None:
            self.index = index

            STREAMS.list_index = self.index
            STREAMS.list_index_tmp = self.index

            self.play_channel()



    #
    def prevChannel(self):
        index = self.index
        index -= 1
        if index == -1:
            index = len(self.channel_list) - 1
        if self.channel_list[index][4] != None:
            self.index = index

            STREAMS.list_index = self.index
            STREAMS.list_index_tmp = self.index
            self.play_channel()

    #
    def help(self):
        self.session.open(xc_help)


###################################            
    def info2(self):
        try:
            # # if config.plugins.XCplugin.configured.value or 
            # if STREAMS.xtream_e2portal_url and STREAMS.xtream_e2portal_url != '' or 'exampleserver.com:8888' :
                # selected_channel = self.channel_list[self.mlist.getSelectionIndex()] 

                if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/TMBD/plugin.pyo"):
                    from Plugins.Extensions.TMBD.plugin import TMBD         #TMDB v.8.3           
                    if selected_channel[2] != None:
                        text = re.compile('<[\\/\\!]*?[^<>]*?>')
                        text_clear = ''
                        text_clear = text.sub('', selected_channel[1])
                        text=text_clear

                        if '.ts' in str(selected_channel[4]):
                                HHHHH = self.show_more_info_Title(selected_channel)
                                self.session.open(TMBD, HHHHH, False)
                        else:
                                self.session.open(TMBD, text, False) 

                elif fileExists('/usr/lib/enigma2/python/Plugins/Extensions/tmdb/plugin.pyo'):
                    from Plugins.Extensions.tmdb.tmdb import tmdbScreen #tmdb 7.3

                    if selected_channel[2] != None:
                        text = re.compile('<[\\/\\!]*?[^<>]*?>')
                        text_clear = ''
                        text_clear = text.sub('', selected_channel[1])
                        text=text_clear
                        #================
                        global service
                        target = text
                        filtertmdb
                        robj = re.compile('|'.join(filtertmdb.keys()))
                        service = robj.sub(lambda m: filtertmdb[m.group(0)], target)
                        service = service.replace("("," ").replace(")","").replace("."," ").replace("[","").replace("]","").replace("-"," ").replace("_"," ").replace("+"," ")
                        service = re.sub("[0-9][0-9][0-9][0-9]", "", service)     
                        #================
                        if '.ts' in str(selected_channel[4]):
                            HHHHH = self.show_more_info_Title(selected_channel)
                            self.session.open(tmdbScreen, HHHHH, 2)
                        else:
                            self.session.open(tmdbScreen, service, 2)                                


                elif os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/IMDb/plugin.pyo'):
                    from Plugins.Extensions.IMDb.plugin import IMDB
                
                    if selected_channel[2] != None:
                        text = re.compile('<[\\/\\!]*?[^<>]*?>')
                        text_clear = ''
                        text_clear = text.sub('', selected_channel[1])
                        text=text_clear
                        if '.ts' in str(selected_channel[4]):
                            HHHHH = self.show_more_info_Title(selected_channel)
                            self.session.open(IMDB, HHHHH)
                        else:
                            self.session.open(IMDB, text)
                        
                elif selected_channel[2] != None:
                    text = re.compile('<[\\/\\!]*?[^<>]*?>')
                    text_clear = ''
                    text_clear = text.sub('', selected_channel[2])
                    self.session.open(xc_Epg, text_clear)
                else:
                    message = (_('No valid list '))
                    web_info(message) 
            # else:
                # message = (_('Please enter correct parameters in Config\n no valid list '))
                # web_info(message) 
                
        except Exception as ex:
            print ex
            print 'ERROR show_more_info'
            
    def show_more_info_Title(self,truc):
        text_clear_1 = ''
        try:
            if truc[1] != None:
                self.descr = truc
                text = re.compile('<[\\/\\!]*?[^<>]*?>')
                AAA = self.descr[2].split("]")[1:][0]
                BBB = AAA.split("(")[:1][0]
                text_clear_1 = text.sub('', BBB).replace(' ',' ').replace('\n',' ').replace('\t',' ').replace('\r',' ')
                # return
            else:
                text_clear_1 = 'No Even'
        except Exception as ex:
            text_clear = 'mkach'
        return text_clear_1            
############################################

        



    # Switch Param for CVS/PLI Based      
    def decodeImage(self):
        try:
            x = self['picon'].instance.size().width()
            y = self['picon'].instance.size().height()
            picture = self.picfile
            picload = self.picload
            sc = AVSwitch().getFramebufferScale()
            self.picload.setPara((x, y, sc[0], sc[1], 0, 0, '#00000000'))
            if fileExists(BRAND)or fileExists(BRANDP):
                self.picload.PictureData.get().append(boundFunction(self.showImage)) ### OPEN

            else:
                self.picload_conn = self.picload.PictureData.connect(self.showImage) ### CVS
            self.picload.startDecode(self.picfile)


        except Exception as ex:
            print ex
            print 'ERROR decodeImage'


    # Switch Param for CVS/PLI Based     
    def showImage(self, picInfo = None):
        self['picon'].show()
        try:
            ptr = self.picload.getData()
            if ptr:
                if fileExists(BRAND) or fileExists(BRANDP): 
                    self['picon'].instance.setPixmap(ptr.__deref__())  ### OPEN

                else:

                    self['picon'].instance.setPixmap(ptr)                ### CVS
        except Exception as ex:
            print ex
            print 'ERROR showImage'

    #        
    def image_downloaded(self, id):
        self.decodeImage()



    #
    def downloadError(self, raw):
        try:

            system("cd / && cp -f " + piclogo + ' %s/poster.jpg' % STREAMS.images_tmp_path)
            self.decodeImage()
        except Exception as ex:
            print ex
            print 'exe downloadError'


class ShowInfo(Screen):

    def __init__(self, session):
        # Screen.__init__(self, session)
        self.session=session
        skin = SKIN_PATH + '/ShowInfo.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()   
        Screen.__init__(self, session)
        self["info"] = Label()
        self["info"].setText(" ")
        self['check']= Label('')
        self['exp']= Label('')
        self['max_connect'] = Label('') 
        self['active_cons']= Label('') 
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"], 
        {
        "ok": self.okClicked,
        "cancel": self.cancel,
        "back": self.cancel,
        "red": self.cancel,
        "green": self.okClicked,
        }, -1)
        self["key_red"] = Label(_("Back"))
        self.icount = 0
        self.errcount = 0
        print  "In ShowInfo 1"
        self.onLayoutFinish.append(self.checkinf)
        
    # def checkinf(self):
            # url_info = urlinfo.replace('enigma2.php','player_api.php')
            # print "url_info2 = ", url_info   
            
            # try:
                # fpage = urllib2.urlopen(url_info).read()
                # print  "fpage =", fpage
                # fp = eval(fpage)
                # user_info = fp['user_info']
                # print  "user_info =", user_info
                # status = user_info['status']
                # self['check'].setText('Status: ' + status) 
                # exp_date = user_info['exp_date']
                # tconv = datetime.fromtimestamp(float(exp_date)).strftime('%c')
                # self['exp'].setText('Exp date: ' + str(tconv)) 
                # max_connections = user_info['max_connections']
                # self['max_connect'].setText('Max Connections: ' +  str(max_connections))                 
                # active_cons = user_info['max_connections']
                # self['active_cons'].setText('User Active: ' +  str(active_cons)) 
            # except Exception as ex:
                # print ex
                # print 'ERROR user_info'           
                # self['check'].setText('Status: no authorised!')
                # self['exp'].setText('Url is invalid or')
                # self['max_connect'].setText('playlist/user') 
                # self['active_cons'].setText('no authorised!') 
                
    def checkinf(self):
            line_info = urlinfo
            line_info = line_info.replace('http://', '').replace('/enigma2.php?',' | ').replace('&',' | ')
            ########            
            # serv = ""
            # port = 80
            serv = config.plugins.XCplugin.hostaddress.value
            user = ""
            passw = ""
            # if re.search('(?<=http:\/\/)[a-zA-Z0-9._\-]+', line_info) is not None:
                # serv = re.search('(?<=http:\/\/)[a-zA-Z0-9._\-]+', line_info).group()
            # if re.search('(?<=:)(\d+)(?=/)', line_info) is not None:
                # port = int(re.search('(?<=:)(\d+)(?=/)', line_info).group())
            if re.search('(?<=username=)[ :@.#a-zA-Z0-9_\-]+', line_info) is not None:
                user = re.search('(?<=username=)[ :@.#a-zA-Z0-9_\-]+', line_info).group()
            if re.search('(?<=password=)[ :@.#a-zA-Z0-9_\-]+', line_info) is not None:
                passw = re.search('(?<=password=)[ :@.#a-zA-Z0-9_\-]+', line_info).group()
            # self['info'].setText("Host: http://" + str(serv) + '\n' + 'Port: ' + str(port) + '\n' + 'Username: ' + str(user) + '\n' + 'Password: ' + str(passw) )  
            self['info'].setText("Host: http://" + str(serv) + '\n' + 'Username: ' + str(user) + '\n' + 'Password: ' + str(passw) ) 
            ########
            # self['info'].setText(line_info)
            url_info = urlinfo.replace('enigma2.php','player_api.php')
            print "url_info2 = ", url_info             
            try:
                fpage = urllib2.urlopen(url_info).read()
                # fpage = urllib2.urlopen(line_info).read()
                print  "fpage =", fpage
                fp = eval(fpage)
                user_info = fp['user_info']
                print  "user_info =", user_info
                status = user_info['status']
                self['check'].setText('Status: ' + status) 
                exp_date = user_info['exp_date']
                tconv = datetime.fromtimestamp(float(exp_date)).strftime('%c')
                self['exp'].setText('Exp date: ' + str(tconv)) 
                max_connections = user_info['max_connections']
                self['max_connect'].setText('Max Connections: ' +  str(max_connections))                 
                active_cons = user_info['max_connections']
                self['active_cons'].setText('User Active: ' +  str(active_cons))                  
                
            except Exception as ex:
                print ex
                print 'ERROR user_info'           
                self['check'].setText('Status: no authorised!')
                self['exp'].setText('Url is invalid or')
                self['max_connect'].setText('playlist/user') 
                self['active_cons'].setText('no authorised!') 
                
                
    def cancel(self):
        self.close()

    def okClicked(self):                   
        self.close()

    def keyLeft(self):
        self["text"].left()

    def keyRight(self):
        self["text"].right()

#
def menu(menuid, **kwargs):
    if menuid == 'mainmenu':

        return [('XCplugin',
          Start_iptv_player,
          'XCplugin',
          4)]
    return []


#
def Start_iptv_player(session, **kwargs):
    global STREAMS
    STREAMS = iptv_streamse()
    STREAMS.read_config()
    if STREAMS.xtream_e2portal_url and STREAMS.xtream_e2portal_url != 'exampleserver.com:8888' :
        STREAMS.get_list(STREAMS.xtream_e2portal_url)

        session.open(xc_Main)

    else: 
        session.open(xc_Main)


mainDescriptor = PluginDescriptor(name='XCplugin Lite', description= descriptionplug + version, where=PluginDescriptor.WHERE_MENU, fnc=menu)

def Plugins(**kwargs):
    result = [PluginDescriptor(name='XCplugin Lite', description= descriptionplug + version, where=PluginDescriptor.WHERE_PLUGINMENU, icon=iconpic, fnc=Start_iptv_player)]
    if config.plugins.XCplugin.strtmain.value:
        result.append(mainDescriptor)
    return result  

