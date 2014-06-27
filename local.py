#!/usr/bin/python
#-*- coding = utf-8 -*-
import struct
import socket,os,sys,time
from hashlib import md5
from common.log import Log
from common.common import SocketCommon
from common.common import Message

class Client(SocketCommon):
	PORT = 6666

	def __init__(self):
		pass

	def connect_server(self, host):
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect((host, self.PORT))
		except socket.error, error :
			Log.logerr('socket failed: %d(%s)' % (error.errno, error.strerror))
			return False
		else:
			return True

	def disconnect(self):
		self.sock.close()


	def cli_put_file(self, local_file, remote_file):
		if self.send_file(local_file, remote_file):
			print "send %s success" % local_file
			return True
		return False

	def cli_get_file(self, local_file, remote_file):
		msg = "send#%s" % (remote_file)
		self.send_msg(self.sock, Message.MSG_CTRL, msg)
		header = self.readn(self.sock, 8)
		(version, macthine, type, length) = Message.parse_msg_header(header)
		msg = self.readn(self.sock, length)
		if self.recv_file(msg, local_file):
			print "recv %s success" % local_file
			return True
		return False
		
	def cli_cmd(self, cmd, shell):
		msg = "cmd#%s#shell#%s" % (cmd, shell)
		self.send_msg(self.sock, Message.MSG_CTRL, msg)
		header = self.readn(self.sock, 8)
		if not header:
			return False
		(version, macthine, type, length) = Message.parse_msg_header(header)
		msg = self.readn(self.sock, length)
		print msg
		return True

if __name__ == "__main__":
	host = sys.argv[1]
	method = sys.argv[2]
	client = Client()
	if not client.connect_server(host):
		print "connect to host:%s failed!" % (host)
		sys.exit(1)

	rc = False
	try:
		if (method == "get"):
			local_file = sys.argv[4]
			remote_file = sys.argv[3]
			rc = client.cli_get_file(local_file, remote_file)
		elif (method == "put"):
			local_file = sys.argv[3]
			remote_file = sys.argv[4]
			rc = client.cli_put_file(local_file, remote_file)
		elif (method == "cmd"):
			shell = sys.argv[3]
			if shell == "shell":
				cmd = ' '.join(sys.argv[4:])
				rc = client.cli_cmd(cmd, shell)
			elif shell == "update":
				cmd = ''
				rc = client.cli_cmd(cmd, shell)
			else:
				print "invalid args", ' '.join(sys.argv[:])
		else:
			print "invalid args:%s" % (' '.join(sys.argv[:]))
	except Exception, error:
			err_msg = 'exception: %d(%s)' % (error.errno, error.strerror)
			Log.logerr(err_msg)
	if not rc:
		sys.exit(1)
	else:
		sys.exit(0)
