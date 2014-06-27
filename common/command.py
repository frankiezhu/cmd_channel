#!/usr/bin/python
#-*- coding = utf-8 -*-
import os
import sys
import log

__all__ = ["Command"]

class Command:
	user = ""
	passwd = ""
	def __init__(self):
		pass
	def run_sys_cmd(self, cmd):
		return os.popen(cmd + ' 2>&1').read()

if __name__ == "__main__":
	if (sys.argv[1]!="show"):
		print "invalid"
		sys.exit(1)
	cmd = ' '.join(sys.argv[1:])
	c = Command()
	print c.run_sys_cmd(cmd)
	
