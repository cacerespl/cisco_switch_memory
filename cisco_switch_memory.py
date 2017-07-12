"""

Read the memory of a switch and do the following:
If the memory is below the threshold: send an email and issue a command to switchover the supervisors
If the memory is above the threshold: send and email notifying the memory is OK 

"""

import paramiko
import time
import re
import sys
import smtplib

#IP of the switch is passed as an argument
switch_ip = sys.argv[1]

#You can set the threshold with a value between 10 to 15% of the total memory
THRESHOLD = 250000

HOST = email_server
SUBJECT = "Memory status"
TO = "receiver_account"
FROM = "sender_account"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#Read the credentials from a file
f = open('password.txt','r')
l = f.readlines()
username = l[0].split(',')[0]
password = l[0].split(',')[1].rstrip()
f.close()

#Connect to the Cisco Switch
ssh.connect(switch_IP,username=username,password=password,allow_agent=False, look_for_keys=False)
ssh_conn=ssh.invoke_shell()
output = ssh_conn.recv(1000)
ssh_conn.send("\n")
time.sleep(2)
ssh_conn.send("\n")

#Read the memory of the switch and get the numerical value
ssh_conn.send("show memory\n")
time.sleep(3)
output = ssh_conn.recv(10000)
z = output.split("\n")[3].split(",")[2].split(" ")[1]
memory = int(z.replace("K",""))

if memory < THRESHOLD:
    print 'low memory'
    text = "Memory is low\n"+"The memory is: " + str(memory)
    ssh_conn.send("\n")
    BODY = "\r\n".join(( "From: %s" % FROM,"To: %s" % TO,"Subject: %s" % SUBJECT ,"",text))								   
    ssh_conn.send("redundancy force-switchover\n")
    time.sleep(10)
    ssh_conn.send("\n")
    time.sleep(3)
    server = smtplib.SMTP(HOST)
    server.starttls()
    server.sendmail(FROM, TO, BODY)
    server.quit()
else:
    print 'Memory is healthy'
    text = "Memory is healthy\n"+"The memory is: " + str(memory)
    BODY = "\r\n".join(( "From: %s" % FROM,"To: %s" % TO,"Subject: %s" % SUBJECT ,"",text))										   
    server = smtplib.SMTP(HOST)
    server.starttls()
    server.sendmail(FROM, TO, BODY)
    server.quit()

ssh.close()
