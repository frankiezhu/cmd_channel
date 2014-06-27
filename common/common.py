#!/usr/bin/python
#-*- coding = utf-8 -*-
import struct
import socket,os,sys,time
import hashlib
import log

__all__ = ["Message", "SocketCommon"]

class Message:
	version = 2
	header_format = "!BBHi"
	(TYPE_BOBCAT, TYPE_HYDRA, TYPE_SWITCH_1G, TYPE_SWITCH_10G) = range(0, 4)
	MSG_HEART_BEAT = 0
	MSG_CTRL = 255
	
	@staticmethod
	def get_msg_header(type, length):
		version = Message.version
		macthine = Message.TYPE_HYDRA
		header = struct.pack(Message.header_format, version, macthine, type, length)
		return header

	@staticmethod
	def parse_msg_header(header):
		return struct.unpack(Message.header_format, header)
	
	def __init__(self):
		pass

class SocketCommon:
	MSG_LEN = 4096
	def sendn(self, sock, msg, msg_length):
		totalsent = 0
		while totalsent < msg_length:
			sent = sock.send(msg[totalsent: totalsent + msg_length])
			if sent == 0:
				raise socket.error
			totalsent = totalsent + sent
		return totalsent

	def readn(self, sock, msg_length):
		msg = ''
		while len(msg) < msg_length:
			chunk = sock.recv(msg_length-len(msg))
			if chunk == '':
				raise socket.error
			msg = msg + chunk
		return msg
		
	def send_msg(self, sock, type, msg):
		msg_length = len(msg)
		header = Message.get_msg_header(type, msg_length)
		self.sendn(sock, header, len(header))
		self.sendn(sock, msg[:], msg_length)

	def parse_file_args(self, msg):
		words = msg.split('#')
		file = words[1]
		len = words[3]
		md5_sum = words[5]
		return (file, len, md5_sum)

	def parse_cmd_args(self, msg):
		words = msg.split('#')
		cmd = words[1]
		shell = words[3]
		return (cmd, shell)

	def recv_file(self, msg, local_name = ''):
		if (not msg.startswith("recv")):
			Log.logerr("Recv Failed, Reason:%s" % msg);
			return False
		remote_name,expect_len,expect_md5 = self.parse_file_args(msg)
		content = self.readn(self.sock, int(expect_len))
		cur_md5 = hashlib.new("md5", content).hexdigest()
		if (expect_md5 != cur_md5):
			Log.logerr("file md5 check failed!expect %s:%s" % (expect_md5, cur_md5))
			return False
		file_name = remote_name
		if local_name:
			file_name = local_name
		open(file_name, 'wb').write(content)	 
		return True

	def send_file(self, local_file, remote_file, send_err_msg = False):
		try:
			file_len = os.path.getsize(local_file)
			content = open(local_file, 'rb').read()
			cur_md5 = hashlib.md5(content).hexdigest()
		except Exception, error:
			err_msg = 'file exception: %d(%s)' % (error.errno, error.strerror)
			Log.logerr(err_msg)
			if send_err_msg:
				self.send_msg(self.sock, Message.MSG_CTRL, err_msg)
			return False
		msg = "recv#%s#len#%d#md5#%s" % (remote_file, file_len, cur_md5)
		self.send_msg(self.sock, Message.MSG_CTRL, msg)
		self.sendn(self.sock, content, file_len)
		return True

		
