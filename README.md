cmd_channel
===========

exec cmd, get file, put file, update using tcp channel with remote agent; python based


1. example cmd:   
  ~/cmd_channel]$ ./local.py 16.3.2.4 cmd shell ls /    
  bin   
  boot    

2. example get:   
  ~/cmd_channel]$ ./local.py 16.3.2.4 get remote.xml a.xml    
  recv a.xml success    

3. example put:   
  ~/cmd_channel]$ ./local.py 16.3.2.4 put a.xml  /cf_card/b.xml   
  send a.xml success    

4. example4 update:   
  ~/cmd_channel]$ ./local.py 16.3.2.4 cmd update    
  success   
