####################################################################################################
#    Copyright (C) 2016 by Ingo Keller                                                             #
#    <brutusthetschiepel@gmail.com>                                                                #
#                                                                                                  #
#    This file is part of yarpTab (OS X Menu Tab for YARP).                                        #
#                                                                                                  #
#    yarpTab is free software: you can redistribute it and/or modify it under the terms of the     #
#    GNU Affero General Public License as published by the Free Software Foundation, either        #
#    version 3 of the License, or (at your option) any later version.                              #
#                                                                                                  #
#    yarpTab is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;          #
#    without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.     #
#    See the GNU General Public License for more details.                                          #
#                                                                                                  #
#    You should have received a copy of the GNU Affero General Public License                      #
#    along with yarpTab.  If not, see <http://www.gnu.org/licenses/>.                              #
####################################################################################################
from subprocess import Popen, call, PIPE
from urllib2    import urlopen

import time

import rumps

@rumps.timer(1)
def timerCallback_checkAlive(_):
    YarpTab.getInstance().updateUi()

def getBasePath():
    return '/usr/local/bin/'


class YarpController(object):

    Y_BASE         = getBasePath()
    Y_YARP         = Y_BASE + 'yarp'
    Y_YARPSRV      = Y_BASE + 'yarpserver3'
    Y_YARPVIEW     = Y_BASE + 'yarpview'

    URL_BASE       = 'http://{0}:{1}/'
    URL_DATALIST   = URL_BASE + 'data=list'

    CMD_YARP_START = [Y_YARPSRV, '--write']
    CMD_YARP_SHOW  = '/usr/bin/open ' + URL_BASE


    def __init__(self, ip = '127.0.0.1', port = 10000):
        self.ip             = ip
        self.port           = port

        self.allPorts       = {}
        self.nestedNames    = {}
        self.prev_html      = ''

        self.updatePortList()
    
    
    def clearPortList(self):
        self.allPorts       = []
        self.nestedNames    = {}
        self.prev_html      = ''
        self.updatePortList()


    def updatePortList(self):

        try:
            html = urlopen(YarpController.URL_DATALIST.format(self.ip, self.port)).read()
        except:
            return

        # no changes - no need to update
        if self.prev_html == html:
            return False
        
        self.prev_html   = html
        ports            = self.parsePortList(html)
        self.allPorts    = dict([(port[1], port[0]) for port in ports])
        self.nestedNames = {}

        # create nested names
        for port in self.allPorts.keys():
            
            namespace = self.nestedNames
            for name in port.split('/')[1:]:
                
                if not name in namespace:
                    namespace[name] = {}
                namespace = namespace[name]
        
        return True


    def parsePortList(self, html):
        """ This method returns a list of port descriptions [<PORT_DESCRIPTION>]"""
        
        # remove line breaks and other non-visual characters
        html    = html.replace('\n', '').replace('\r', '')
        lines   = html.split('<pre>')[1].split('</pre>')[0].split('<a href="')
        return [ self.parseLink(link) for link in lines if len(link.strip()) > 0 ]
    
    
    def parseLink(self, link_line):
        """ This method returns a list for a port link [<URL>, <NAME>, <DESCRIPTION>]"""
        return  [ link_line.split('"')[0],
                  link_line.split('>')[1].split('<')[0],
                  link_line.split('(')[1].split(')')[0] ]
        

    def openImageOutput(self, port):
        """ This method opens a yarp view and connects it to the given port."""
        Popen([YarpController.Y_YARPVIEW, "--name", "/yarpTab%s" % port])
        time.sleep(0.5)
        call([YarpController.Y_YARP, "connect", port, "/yarpTab%s" % port])

    
    def openTextOutput(self, port):
        """ This method opens a Terminal window and runs yarp read which is connected to the given 
            port.
        """
        yarp_cmd   = 'yarp read /yarpTab{0} {0}'.format(port)
        osa_script = 'tell application "Terminal" to do script "{0}"'.format(yarp_cmd)
        Popen(["/usr/bin/osascript", '-e', osa_script])


    def openTextInput(self, port):
        """ This method opens a Terminal window and runs yarp write which is connected to the given 
            port.
        """
        yarp_cmd   = 'yarp write /yarpTab{0} {0}'.format(port)
        osa_script = 'tell application "Terminal" to do script "{0}"'.format(yarp_cmd)
        Popen(["/usr/bin/osascript", '-e', osa_script])


    def openYarpInBrowser(self):
        """ This methods opens a browser with the yarp web interface URL."""
        cmd = YarpController.CMD_YARP_SHOW.format(self.ip, self.port)
        print cmd
        call(cmd.split())


    def cleanYarp(self):
        """ This method runs the yarp clean command."""
        call([YarpController.Y_YARP, 'clean', '--timeout', '1'])
        time.sleep(1)
        self.clearPortList()


    def killYarp(self):
        """ This method kills all yarpservers. """
        call(['killall', 'yarpserver'])
        self.clearPortList()



class YarpTab(rumps.App):
    

    MI_YS_START = ' Run'
    MI_YS_STOP  = ' Stop'
    MI_YS_SHOW  = ' Show'
    MI_YS_PORTS = ' Ports'
    MI_YS_CLEAN = ' Clean'
    MI_YS_KILL  = ' Kill'
    MI_QUIT     = ' Quit'
    
    _instance   = None
    

    @staticmethod
    def getInstance():
        if not YarpTab._instance:
            YarpTab._instance = YarpTab()
        return YarpTab._instance


    def __init__(self):
        super(YarpTab, self).__init__('yarpTab', 'Yarp')

        self.yarpserver     = None
        self.quit_button    = None
        self.prev_state     = None
        self.yarpController = YarpController()        
        self._delayedSetup  = True
        
        global_timer.start()


    def delayedSetup(self):
        self._delayedSetup = False


    @rumps.clicked(MI_YS_START)
    def start(self, sender):

        if not self.isAlive():
            self.yarpserver = Popen(YarpController.CMD_YARP_START)
            ip      = self.yarpController.ip
            port    = self.yarpController.port
            msg     = 'Yarp Server started'
            msg    += '\nIP: {0}\nPort: {1}'.format(ip, port)
            rumps.notification('YarpTab', '', msg)

        else:
            self.yarpserver.kill()
            self.yarpserver = None
            rumps.notification('YarpTab', '', 'Yarp Server stopped')

        self.updateUi()


    @rumps.clicked(MI_YS_SHOW)
    def show(self, _):
        self.yarpController.openYarpInBrowser()

    
    @rumps.clicked(MI_YS_PORTS)
    def nothing(self, _):
        pass


    @rumps.clicked(MI_YS_CLEAN)
    def clean(self, _):
        self.yarpController.cleanYarp()
        time.sleep(1)
        self.updateUi()
        
    
    @rumps.clicked(MI_YS_KILL)
    def killYarpServer(self, _):
        self.yarpController.killYarp()
        rumps.notification('YarpServer', '', 'Servers killed')
        self.updateUi()

    
    @rumps.clicked(MI_QUIT)
    def clean_up_before_quit(self, _):
        if self.isAlive():
            self.yarpserver.kill()
        rumps.quit_application()


    def isAlive(self):
        return (self.yarpserver is not None) and (self.yarpserver.poll() == None)


    def updateUi(self):

        if self._delayedSetup:
            self.delayedSetup()

        isAlive = self.isAlive()

        # only update UI if there is a reason 
        if (self.prev_state != isAlive) or self.prev_state is None :
            self.prev_state = isAlive

            startStopMenuItem = self.menu.get(YarpTab.MI_YS_START)
            if isAlive:
                startStopMenuItem.title  = YarpTab.MI_YS_STOP
                
            else:
                startStopMenuItem.title  = YarpTab.MI_YS_START


        if self.yarpController.updatePortList():
            
            # clear menu items
            rootItem = self.menu.get(YarpTab.MI_YS_PORTS)
            if rootItem:
                rootItem.clear()
            
            # add menu items
            self.addPortItem(rootItem, self.yarpController.nestedNames, '/')


    def addPortItem(self, parent, item_dict, namespace):
        
        names = item_dict.keys()
        names.sort()
        
        for name in names:
            rmi      = rumps.MenuItem('/%s' % name)
            rmi.port = namespace + name
            parent.add(rmi)
            
            # add children
            if item_dict[name]:
                self.addPortItem(rmi, item_dict[name], namespace + name + '/')

            # or add a callback function
            else:
                if 'yarpTab' not in namespace:
                    rmi.set_callback(self.callPort)

                    # create sub menus
                    rmiIO      = rumps.MenuItem('Image Output', self.callIO)
                    rmiIO.port = namespace + name
                    rmi.add(rmiIO)

                    rmiTO      = rumps.MenuItem('Text Output', self.callTO)
                    rmiTO.port = namespace + name
                    rmi.add(rmiTO)

                    rmiTI      = rumps.MenuItem('Text Input', self.callTI)
                    rmiTI.port = namespace + name
                    rmi.add(rmiTI)


    def callIO(self, sender):
        self.yarpController.openImageOutput(sender.port)

    def callTO(self, sender):
        self.yarpController.openTextOutput(sender.port)
    
    def callTI(self, sender):
        self.yarpController.openTextInput(sender.port)


    def callPort(self, sender):

        portType = self.guessPortType(sender.port)
        msgType  = self.guessMessageType(sender.port)
        port     = sender.port

        # output ports
        if portType  == 'o':

            # images
            if msgType == 'image':
                self.yarpController.openImageOutput(port)
            
            # text
            else:
                self.yarpController.openTextOutput(port)

        # input port
        elif portType == 'i':

            # text
            if msgType == 'text':
                self.yarpController.openTextInput(port)

            # images
            else:
                pass
        
        # unknown - assume text output
        else:
            self.yarpController.openTextOutput(port)
    


    def guessPortType(self, portname):

        # see if we got a input/output prefix
        suffix = portname.split(':')[1] if ':' in portname else portname.split('/')[-1]
        
        # check input suffixes
        if suffix in ['i', 'rpc']:
            return 'i'

        # check output suffixes
        elif suffix in ['o', 'grabber']:
            return 'o'

        # unkown
        return 'u'
        

    def guessMessageType(self, portname):
        
        name = portname.split('/')[-1]
        for t in ['image', 'img', 'grabber']:
            if t in name.lower():
                return 'image'

        return 'text'


if __name__ == '__main__':
    global_timer = rumps.Timer(timerCallback_checkAlive, 1)
    YarpTab.getInstance().run()