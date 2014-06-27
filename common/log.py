#!/usr/bin/python
#-*- coding = utf-8 -*-

import time
from os.path import exists
import os
import sys
import inspect
import syslog

__all__ = ["Log"]
class Log:
    str_level = ["emerg", "alert", "critical", "err", "warn", "notice", "info", "dbg"]
    file_thresh = syslog.LOG_INFO
    def __init__(self):
        pass

    @staticmethod 
    def init_log(self):
        syslog.openlog(ident="AgentPy",logoption=syslog.LOG_PID, facility=syslog.LOG_LOCAL0)
    
    @staticmethod 
    def getLogMessage(level, message):
        frame,filename,lineNo,functionName,code,unknowField = inspect.stack()[3]
        filename=os.path.basename(filename)
        return "[%s][%s:%s-%s] %s" % (Log.str_level[level],filename,lineNo,functionName,message)
        
    @staticmethod
    def __raw_log(level, line):
        message = Log.getLogMessage(level, line)
        print message
        if level <= Log.file_thresh:
            syslog.syslog(message)
    
    @staticmethod   
    def logdbg(line):
        Log.__raw_log(syslog.LOG_DEBUG, line)
        
    @staticmethod   
    def logmsg(line):
        Log.__raw_log(syslog.LOG_INFO, line)
        
    @staticmethod
    def logerr(line):
        Log.__raw_log(syslog.LOG_ERR, line)
        
if __name__ == "__main__":
    Log.logerr("I'am in error!")
    Log.logmsg("I'am in msg!")
    Log.logdbg("I'am in dbg!")
    err = "logmsg"
    Log.logmsg("%s" % err)
 
    
        
            
