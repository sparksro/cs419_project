#!/usr/bin/python

# ************************************************************************
# Program: Email sending tool.
# Version 1.1
# Date: Jan 12 2016
# Description: Python based tool for sending text based emails.  Used for 
#              testing of filters and conversion programs for project.  Assembled from
#	       Python documentation here: https://docs.python.org/2/library/email-examples.html
#	       and Gmail examples here: 
#	       http://stackoverflow.com/questions/10147455/how-to-send-an-email-with-gmail-as-provider-using-python
#	       
#	       Replace the fromaddr, username and password with your gmail settings in the settings section bellow. 
#	       
# Author: Rob Sparks
# Note: I set this up to work with gmail as the sending server but Google has ramped 
# up the security settings.  In order to use this with your account you have to make 
# a change to your settings.  See the following: 
#
# https://support.google.com/accounts/answer/6010255

# ************************************************************************
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

# ****  Settings *****************

fromaddr = 'fromaddress@gmail.com'
toaddr  = 'toaddress7@x.com'
username = 'username'
password = 'password'

# ********************************

# Open a plain text file for reading.  For this example, assume that
# the text file contains only ASCII characters.
textfile =''
subject = ''
message = ''

def sendemail (message, subject, textfile):
	fp = open(textfile, 'rb')
	# Create a text/plain message
	msg = MIMEText(fp.read())
	fp.close()

	msg['Subject'] = subject
	msg['From'] = 'do.not.reply@engr.orst.edu'
	msg['To'] = toaddr

	server = smtplib.SMTP('smtp.gmail.com:587')
	server.ehlo()
	server.starttls()
	server.login(username,password)
	server.sendmail(fromaddr, toaddr, msg.as_string())
	server.quit()
	print message	

# Menue
ans=True
while ans:
	print("""
	1. Send Advising signup email.
	2. Send Advising cancellation email.
	3. Exit.
	""" )
	ans=raw_input("What would you like to do? ") 
    	if ans=="1": 
     		message = '\n    Register email sent.'
		subject = 'Advising Signup with McGrath, D Kevin confirmed for x'
		textfile = 'signup.txt'
		sendemail (message, subject, textfile)
    	elif ans=="2":
		message = '\n    Cancellation email sent.'
      		subject = 'Advising Signup Cancellation'
		textfile = 'cancellation.txt'
		sendemail (message, subject, textfile)
    	elif ans=="3":
		print('\n    Quiting.')
		raise SystemExit
        elif ans !="":
        	print("\n    Not Valid Choice Try again!") 


