#!/usr/bin/env python

from lib.msg import Message
from lib.config import config
from lib.hts import htsp
from datetime import datetime
from croniter import croniter
import getopt
import sys
import os
import commands
import time

scriptName = "naptime"
scriptVersion = "0.2"

def usage():
    print( scriptName + " " + scriptVersion + '''
Author: Ferdinand Zickner

Options:
-c, --config <FILE>     Specify path to config file.
-h, --help              Show this help.
-f, --force             Ignore checks an sleep until next recording.
-v, --verbose           Show hidden messages.''')

def getStart(arg):
    return arg['start']

## ----- Main Programm
def main():

    force = False
    message = Message()
    sysHalt = True
    sysIdle = -1
    sysMode = "off"
    sysPathConfig = "/etc/" + scriptName + ".conf"
    sysPathCheckfile = None
    verbose = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:fv", ["help","config","force","verbose"])

    except getopt.GetoptError as err:
        message.rt(str(err)) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-c", "--config"):
            if os.path.isfile(a):
                sysPathConfig = a
        elif o in ("-f", "--force"):
            force = True
        elif o in ("-v", "--verbose"):
            message.setVerbose()
        else:
            assert False, "unhandled option"


    ## ----- Read Config and run checks
    message.ws("Running " + scriptName + " " + scriptVersion + " at " + time.strftime("%c"))
    Config = config()
    if False ==    Config.read(sysPathConfig): sys.exit(2)
    for s in Config.sections():


        ## ----- General Settings
        if s == "General":
            message.ws("> General Settings")
            try: sysService = Config.map(s)['enabled']
            except: sysService = "False"
            if "True" != sysService:
                message.rt("  > " + scriptName + " is disabled.")
                sys.exit(0)

            try:
                sysPathCheckfile = Config.map(s)['checkfile']
                message.gn("  > Using CheckFile: " + sysPathCheckfile)
            except: message.ge("  > No CheckFile defined!")

            try:
                sysMode = Config.map(s)['mode']
                message.gn("  > Using Mode: " + sysMode)
            except: message.ge("  > No Mode defined!")

            try:
                exp = Config.map(s)['scheduledwakeup']
                iter = croniter(exp, datetime.now())
                wakeupNext = time.mktime(iter.get_next(datetime).timetuple())
                wakeupIdle = wakeupNext - time.time()
                message.gn("  > Next wake up: " + datetime.fromtimestamp(wakeupNext).strftime('%d.%m.%Y %H:%M:%S'))
                if sysIdle > wakeupIdle or sysIdle < 0:
                    sysIdle = wakeupIdle
            except: message.ge("  > No ScheduledWakeUp defined!", False)


        ## ----- Checking TVheadend
        elif s == "CheckTVheadend":
            message.ws("> Checking TVheadend for running an upcoming recordings ...")

            ## connecting
            try:
                tvHeadendServer = htsp.HTSPClient([Config.map(s)['host'], int(Config.map(s)['port'])])
                tvHeadendServer.hello()
                message.gn("  > Connection to "+ Config.map(s)['host'] + " succeed.", False)
            except:
                message.ge("  > Connection to "+ Config.map(s)['host'] + " failed!", False)

            ## authentication
            try:
                tvHeadendServer.authenticate(str(Config.map(s)['user']), str(Config.map(s)['passwd']))
                message.gn("  > Authentication with user " + Config.map(s)['user'] + " succeed.", False)
            except:
                message.ge("  > Authentication failed or not configued!", False)

            ## get upcoming recordings
            try:
                tvHeadendServer.send('api', {'path': 'dvr/entry/grid_upcoming'})
                tvResponse = sorted(tvHeadendServer.recv()['response']['entries'], key=getStart)
                tvPreWakeUp = int(Config.map(s)['prewakeup'])
                tvNextRecording = int(tvResponse[0]['start'])
                tvIdle = tvNextRecording - time.time()
                if tvIdle < 0:
                    sysHalt = False
                    message.rt("  > TVheadend records: " + tvResponse[0]["title"]["ger"] + "!")
                elif tvIdle < tvPreWakeUp:
                    sysHalt = False
                    message.rt("  > Next recording: " + tvResponse[0]["title"]["ger"] + " at " + datetime.fromtimestamp(tvNextRecording).strftime('%d.%m.%Y %H:%M:%S'))
                else:
                    message.gn("  > Next recording: " + tvResponse[0]["title"]["ger"] + " at " + datetime.fromtimestamp(tvNextRecording).strftime('%d.%m.%Y %H:%M:%S'))
                    if sysIdle > (tvIdle - tvPreWakeUp) or sysIdle < 0:
                        sysIdle = tvIdle - tvPreWakeUp
            except:
                message.rt("  > Connection to "+ Config.map(s)['host'] + " failed!")
                sysHalt = False


        ## ----- Checking Network
        elif s == "CheckNetwork":
            message.ws("> Checking Network ...")
            try: servers = Config.map(s)['servers'].split()
            except: servers = {}
            for ip in servers:
                if 0 == os.system("ping -c 1 " + ip + " > /dev/null 2>&1"):
                    sysHalt = False
                    message.rt("  > "+ ip + " is up!")
                else:
                    message.gn("  > " + ip + " is down!")


        ## ----- Checking for running Deamons
        elif s == "CheckDeamon":
            message.ws("> Checking for running Deamons ...")
            try: deamons = Config.map(s)['daemons'].split()
            except: deamons = {}
            for daemon in deamons:
                resp = commands.getstatusoutput("pgrep -c " + daemon)
                name = daemon.replace("_", "")
                name = name.replace("^", "")
                name = name.replace("$", "")

                if int(resp[1]) > 1:
                    sysHalt = False
                    message.rt("  > Daemon " + name + " is active! (" + resp[1] + ")")
                else:
                    message.gn("  > Daemon " + name + " is inactive! (" + resp[1] + ")")


        ## ----- Checking for running Applications
        elif s == "CheckApps":
            message.ws("> Checking for running Applications ...")
            try: apps = Config.map(s)['apps'].split()
            except: apps = {}
            for app in apps:
                resp = commands.getstatusoutput("pgrep -c " + app)
                name = app.replace("_", "")
                name = name.replace("^", "")
                name = name.replace("$", "")

                if int(resp[1]) > 0:
                    sysHalt = False
                    message.rt("  > Application " + name + " is running! (" + resp[1] + ")")
                else:
                    message.gn("  > Application " + name + " isn\'t running! (" + resp[1] + ")")


        ## ----- Checking for Users
        elif s == "CheckUsers":
            message.ws("> Checking for Users ...")
            for check in Config.map(s):
                try: count = int(commands.getstatusoutput(Config.map(s)[check])[1])
                except: count = -1

                if 0 == count:
                    message.gn("  > No " + check + " users.")
                elif -1 == count:
                    message.ge("  > Check for " + check + " didn't return a number!")
                else:
                    sysHalt = False
                    message.rt("  > Some " + check + " users are active (" + str(count) + ").")


        ## ----- Not defined Checks
        else:
            message.ws("> Nothing to do for " + s + ".")


    ## ----- Check for going to sleep
    if sysHalt or force:

        if os.path.isfile(sysPathCheckfile) or force:
            message.bl("> Going down for sleep now.")

            if 0 < sysIdle:
                cmd = "rtcwake -m " + sysMode + " -s " + str(int(sysIdle))
            else:
                if sysMode == "halt": cmd = "shutdown -h now"
                elif sysMode == "off": cmd = "shutdown -h now"
                else:
                    message.rt("  > Mode " + sysMode + " not implemented!")
                    sys.exit(1)

            try:
                os.system(cmd)
                os.remove(sysPathCheckfile)
                message.bl("    " + cmd )
            except:
                message.rt("  > Command " + cmd + " failed!")

        else:
            message.ge("> Going to sleep after future check.")
            try: open(sysPathCheckfile, 'a').close()
            except: message.rt("  > Can't create " + sysPathCheckfile + ".")

    else:
        message.ws("> Can't going to sleep while server is in use!")
        if os.path.isfile(sysPathCheckfile): os.remove(sysPathCheckfile)


if __name__ == "__main__":
    main()
