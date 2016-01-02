#!/usr/bin/env python

from lib.msg import message
from lib.config import config
from lib.hts import tvheadend
from datetime import datetime
import getopt
import sys
import os 
import commands
import time


def usage():
  print "TO DO"


## ----- Main Programm
def main():

  script_name = "naptime"
  output = None
  force = False
  sys_halt = True
  sys_idle = -1
  sys_mode = "off"
  sys_path_config = "/etc/" + script_name + ".conf"
  sys_path_checkfile = None

  try:
    opts, args = getopt.getopt(sys.argv[1:], "hc:f", ["help","config","force"])

  except getopt.GetoptError as err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

  for o, a in opts:
    if o in ("-h", "--help"):
      usage()
      sys.exit()
    elif o in ("-c", "--config"):
      if os.path.isfile(a):
        sys_path_config = a
    elif o in ("-f", "--force"):
      force = True
    else:
      assert False, "unhandled option"



  ## ----- Read Config and run checks
  Message = message(None)
  Message.ws("Running " + script_name + " at " + time.strftime("%c"))
  Config = config()
  if False ==  Config.read(sys_path_config): sys.exit(2)
  for s in Config.sections():


    ## ----- General Settings
    if s == "General":
      Message.ws("> General Settings")
      try: sys_service = Config.map(s)['enabled']
      except: sys_service = "False"
      if "True" != sys_service:
        Message.rt("  > " + script_name + " is disabled.")
        sys.exit(0)

      try:
        sys_path_checkfile = Config.map(s)['checkfile']
        Message.gn("  > Using CheckFile: " + sys_path_checkfile)
      except: Message.ge("  > No CheckFile defined!")

      try:
        sys_mode = Config.map(s)['mode']
        Message.gn("  > Using Mode: " + sys_mode)
      except: Message.ge("  > No Mode defined!")
        


    ## ----- Checking TVheadend
    elif s == "CheckTVheadend":
      Message.ws("> Checking TVheadend for running an upcoming recordings ...")
      try:
        tv_host = Config.map(s)['host']
        tv_port_web = int(Config.map(s)['portweb'])
        tv_port_htsp = int(Config.map(s)['porthtsp'])
        tv_pre_wake_up = int(Config.map(s)['prewakeup'])
    
        TVheadendServer = tvheadend.client([tv_host, tv_port_web, tv_port_htsp]) 
        tv_response = TVheadendServer.dvrGetGrid("upcoming", 0, 1, True)

        tv_next_recording =  int(tv_response["entries"][0]["start_real"])
        tv_idle = tv_next_recording - time.time()
  
        if tv_idle < 0:
          sys_halt = False
          Message.rt("  > TVheadend records: " + tv_response["entries"][0]["title"]["ger"] + "!")
        elif tv_idle < tv_pre_wake_up:
          sys_halt = False
          Message.rt("  > Next recording: " + tv_response["entries"][0]["title"]["ger"] + " at " + datetime.fromtimestamp(tv_next_recording).strftime('%d.%m.%Y %H:%M:%S'))
        else:
          Message.gn("  > Next recording: " + tv_response["entries"][0]["title"]["ger"] + " at " + datetime.fromtimestamp(tv_next_recording).strftime('%d.%m.%Y %H:%M:%S'))
          sys_idle = tv_idle - tv_pre_wake_up

      except:
        Message.rt("  > Broken configuration!")
        Message.rt("    Please check " + sys_path_config + ".")
        sys_halt = False


    ## ----- Checking Network
    elif s == "CheckNetwork":
      Message.ws("> Checking Network ...")
      try: servers = Config.map(s)['servers'].split()
      except: servers = {}
      for ip in servers:
        if 0 == os.system("ping -c 1 " + ip + " > /dev/null 2>&1"):
          sys_halt = False
          Message.rt("  > "+ ip + " is up!")
        else:
          Message.gn("  > " + ip + " is down!")


    ## ----- Checking for running Deamons
    elif s == "CheckDeamon":
      Message.ws("> Checking for running Deamons ...")
      try: deamons = Config.map(s)['daemons'].split()
      except: deamons = {}
      for daemon in deamons:
        resp = commands.getstatusoutput("pgrep -c " + daemon)
        name = daemon.replace("_", "")
        name = name.replace("^", "")
        name = name.replace("$", "")
    
        if int(resp[1]) > 1:
          sys_halt = False
          Message.rt("  > Daemon " + name + " is active! (" + resp[1] + ")")
        else:
          Message.gn("  > Daemon " + name + " is inactive! (" + resp[1] + ")")


    ## ----- Checking for running Applications
    elif s == "CheckApps":
      Message.ws("> Checking for running Applications ...")
      try: apps = Config.map(s)['apps'].split()
      except: apps = {}
      for app in apps:
        resp = commands.getstatusoutput("pgrep -c " + app)
        name = app.replace("_", "")
        name = name.replace("^", "")
        name = name.replace("$", "")

        if int(resp[1]) > 0:
          sys_halt = False
          Message.rt("  > Application " + name + " is running! (" + resp[1] + ")")
        else:
          Message.gn("  > Application " + name + " isn\'t running! (" + resp[1] + ")")


    ## ----- Checking for Users
    elif s == "CheckUsers":
      Message.ws("> Checking for Users ...")
      for check in Config.map(s):
        try: count = int(commands.getstatusoutput(Config.map(s)[check])[1])
        except: count = -1

        if 0 == count:
          Message.gn("  > No " + check + " users.")
        elif -1 == count:
          Message.ge("  > Check for " + check + " didn't return a number!")
        else:
          sys_halt = False
          Message.rt("  > Some " + check + " users are active (" + str(count) + ").")


    ## ----- Not defined Checks
    else:
      Message.ws("> Nothing to do for " + s + ".")


  ## ----- Check for going to sleep
  if sys_halt or force:
    
    if os.path.isfile(sys_path_checkfile) or force:
      Message.bl("> Going down for sleep now.")
      if 0 < sys_idle: 
        cmd = "rtcwake -m " + sys_mode + " -s " + str(int(sys_idle))
      else
        if sys_mode == "halt": cmd = "shutdown -h now"
        else:
          Message.rt("  > Mode " + sys_mode + " not implemented!")
          sys.exit(1)

      try:
        os.system(cmd)
        os.remove(sys_path_checkfile)
        Message.bl("  " + cmd )
      except:
        Message.rt("  > Command " + cmd + " failed!")

    else:
      Message.ge("> Going to sleep after future check.")
      try: open(sys_path_checkfile, 'a').close()
      except: Message.rt("  > Can't create " + sys_path_checkfile + ".")

  else:
    Message.ws("> Can't going to sleep while server is in use!")
    if os.path.isfile(sys_path_checkfile): os.remove(sys_path_checkfile)


if __name__ == "__main__":
  main()






# ############################################################################
# Editor Configuration
#
# vim:sts=2:ts=2:sw=2:et
# autocmd Filetype python setlocal ts=2 sts=2 sw=2 expandtab
# ############################################################################
