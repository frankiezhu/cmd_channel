cmd_channel
===========

exec cmd, get file, put file, update using tcp channel with remote agent; python based


example1 cmd:
~/cmd_channel]$ ./local.py 16.3.2.4 cmd shell ls /
bin
boot

example2 get:
~/cmd_channel]$ ./local.py 16.3.2.4 get remote.xml a.xml
recv a.xml success

example3 put:
~/cmd_channel]$ ./local.py 16.3.2.4 put a.xml  /cf_card/b.xml
send a.xml success

example4 update:
~/cmd_channel]$ ./local.py 16.3.2.4 cmd update
success
