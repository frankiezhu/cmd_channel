#!/cf_card/python2.7/bin/python
#-*- coding = utf-8 -*-
import socket
import struct
import time
import thread
import os
import sys
import fcntl
import xml.etree.ElementTree
from hashlib import md5
from common.log import Log
from common.command import Command
from common.common import SocketCommon
from common.common import Message

class Config:
	CONF_FILE = "remote.xml"
	svr_conf_dict = {}
	cli_conf_dict = {}
	cli_cmds_dict = {}
	def __init__(self):
		pass
	def __str__(self):
		return self.svr_conf_dict

	def read_config(self, file_name):
		if not os.path.exists(file_name):
			Log.logerr("CONF:%s not exists,using default." % file_name)
			return False
		tree = xml.etree.ElementTree.ElementTree(file=file_name)
		root = tree.getroot()
		self.svr_conf_dict['listen'] = int(root.findall ('server/listen')[0].text)
		self.svr_conf_dict['backlog'] = int(root.findall ('server/backlog')[0].text)
		return True
			
g_conf = Config()


class ConnHandler(SocketCommon):
	def __init__(self, sock):
		self.sock = sock
		pass

	def do_cmds(self, msg):
		if (msg.startswith("recv")):
			return self.recv_file(msg)
		elif (msg.startswith("send")):
			local_file = msg.split('#')[1]
			return self.send_file(local_file, local_file, True)
		elif (msg.startswith("cmd")):
			cmd,shell = self.parse_cmd_args(msg)
			ctl = Command()
			if (shell == 'shell'):
				ret_info = ctl.run_sys_cmd(cmd)
				return self.send_msg(self.sock, Message.MSG_CTRL, ret_info)
			elif (shell == 'update'):
				args = sys.argv[:]
				args.insert(0, sys.executable)
				os.chdir(os._startup_cwd)
				msg = 'success'
				self.send_msg(self.sock, Message.MSG_CTRL, msg)
				self.sock.close()
				Log.logmsg("Update self:%s,%s" % (args, os._startup_cwd))
				os.execv(sys.executable, args)
				#no return
			else:
				Log.logerr("Invalid cmd!%s" % msg)
				return False

	def do_work(self):
		while (True):
			header = self.readn(self.sock, 8)
			if not header:
				return True
			version, machine, type, length = Message.parse_msg_header(header)
			if (version != Message.version or machine != Message.TYPE_HYDRA):
				Log.logerr("Server check message header failed!")
				return False
			msg = self.readn(self.sock, length)
			if (type == Message.MSG_CTRL):
				Log.logmsg("Server try execute cmd :%s" % msg)
				if self.do_cmds(msg):
					Log.logmsg("Server execute cmd :%s, success" % msg)
					return True
				else:
					Log.logmsg("Server execute cmd :%s, success" % msg)
			else:
				Log.logerr("unknown cmd:%d %s" % (type, msg))
			return False

def new_conn_thread_func(conn, addr):
	print addr
	try:
		handler = ConnHandler(conn)
		handler.do_work()
	except Exception, error:
		Log.logerr('svr handler thread exception: %d(%s)' % (error.errno, error.strerror))
	finally:
		conn.close()
		thread.exit_thread()

class Server:
	def __init__(self):
		self.conf = g_conf
		pass

	def set_close_exec(self, fd):
		flags = fcntl.fcntl(fd, fcntl.F_GETFD)
		fcntl.fcntl(fd, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)

	def init_sock(self):
		try:
			port = self.conf.svr_conf_dict['listen']
			back_log = self.conf.svr_conf_dict['backlog']
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.set_close_exec(self.sock.fileno())
			self.sock.bind(('', port))
			self.sock.listen(back_log)
		except socket.error, error :
			Log.logerr('server init socket failed: %s(%s)' % (socket.error, error))
			return False
		else:
			return True
		
	def run(self):
		if not self.init_sock():
			return False
		while True:
			conn, addr = self.sock.accept()
			thread.start_new_thread(new_conn_thread_func, (conn, addr))

def createDaemon(pidfile, work_dir="/"):
	try:
		if os.fork() > 0:
			os._exit(0)
	except OSError,error:
		print 'fork #1 failed: %d(%s)' % (error.errno, error.strerror)
		return False

	os.chdir(work_dir)
	os.setsid()
	os.umask(0)

	try:
		pid = os.fork()
		if pid > 0:
			os._exit(0)
	except OSError, error:
		print 'fork #2 failed: %d(%s)' % (error.errno, error.strerror)
		return False

	import fcntl
	fd = os.open(pidfile, os.O_WRONLY | os.O_CREAT, 0666);
	try:
		fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
	except IOError:
		print "lock file:%s failed, maybe already running" % pidfile
		os.close(fd)
		return False
	os.write(fd, "%d\n" % os.getpid())

	null = file("/dev/null", 'rw+')
	os.dup2(null.fileno(), sys.stdin.fileno())
	os.dup2(null.fileno(), sys.stdout.fileno())
	os.dup2(null.fileno(), sys.stderr.fileno())
	return True


def run_svr():
	svr = Server()
	svr.run()

if __name__ == "__main__":
	PIDFILE = "/var/run/agent.pid"
	WORKPATH = "/"
	os._startup_cwd = os.getcwd()
	if not g_conf.read_config(Config.CONF_FILE):
		Log.logerr("read config failed!")
		sys.exit(1)
	import getopt,sys
	try:
		opts,args = getopt.getopt(sys.argv[1:], "d", ["daemon",])
	except getopt.GetoptError,e:
		print e
		sys.exit(1)
	for o,a in opts:
		if o in ("-d","--daemon"):
			if not createDaemon(PIDFILE, WORKPATH):
				Log.logerr("Daemon failed!")
				sys.exit(1)
	run_svr()

