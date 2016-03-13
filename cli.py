#!/usr/bin/python

# Advising Schedule Interface 
# version 1.50
# Authors:  Rob Sparks, Susan Lee

import curses
from urllib2 import urlopen
from HTMLParser import HTMLParser
#from simplejson import loads
import mysql.connector
from mysql.connector import errorcode
from os import system
import time
import MySQLdb
import hashlib
import smtplib
from email.mime.text import MIMEText
import string
import random, os
import datetime as date
from subprocess import call# for the screen resize

# make sure the terminal screen size is correct so we have room for the proper display.
call(["printf","\e[8;24;80t"])
time.sleep(.125)#have to give the system settings time to update or the new window we launch bellow will be the wrong size.

# Commonly used prompts and user indicators
LoggedIn = False;
action_menu = "Enter the number to perform the action.\n---------------------------------------\n1. Register \n2. Login \n3. Forgot Password"
logged_menu = "Enter the number to perform the action.\n---------------------------------------\n1. View Advising Schedule \n2. Change Password \n3. Logout"
bottom_line = "Press 'M' to see Menu. 'Q' to quit."
bottom_line2 = "Press UP or DOWN, No. to select an appt, X to drop out to main menu."
bottom_line3 = "Press X to drop out to appt list, C to cancel apt."

status =  "                                 logged-out";
status2 =  "logged-out";
status3 =  "                                  logged-in";#idfferent spacing versions used in different cases
status4 =  " logged-in";
status5 =  "                  logged-in";

# ****  Email Settings *****************
# These setting need to updated to instructor's email 
fromaddr = 'procmailtestscs@gmail.com'
#toaddr  = 'procmailtestscs@gmail.com'
username = 'procmailtestscs'
password = 'gobeavers!'
#***************************************
db = ''#db blank


# *********   Functions  ***************************************************************************************

def make_connection():
	try:
	   db = MySQLdb.connect("52.10.233.116","advising_user", "VLrMMJSScH6ZLHca",  "advising_db")
	except mysql.connector.Error as err:
  	   if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    	      print("Something is wrong with your user name or password %d" % (err.errno))
  	   elif err.errno == errorcode.ER_BAD_DB_ERROR:
    	      print("Database does not exist")
  	   else:
    	      print(err)
	return db

def disconnect(db):
	try:
	   db.close()
	except: 
		print "Error disconnecting or login out from database."

# insert new user info
def insertNewUsser(email, pswd):
	db = make_connection()
	cursor = db.cursor()
	sql = "INSERT INTO User (Email, Password)\
		VALUES('%s','%s')" %\
		(email, pswd)
	try:
		cursor.execute(sql)
		db.commit()
		disconnect(db)
	except:
		db.rollback()
		cli_text_window.addstr("An unknown error ocurred when attempting to store your user info!", curses.color_pair(1))		

#update user password 
def updatePassword(email, update):
    db = make_connection()
    cursor = db.cursor()
    sql = "UPDATE User SET Password = '%s' WHERE Email= '%s'" %(update, email)
    try:
            cursor.execute(sql)
            db.commit()
            cli_text_window.addstr("Your information was stored sucessfully.", curses.color_pair(3))
            disconnect(db)
    except:
            db.rollback()
            cli_text_window.addstr("An unknown error ocurred when attempting to store your user info!", curses.color_pair(1))		

#update users last modified date 
def updateDate(email, update):
    db = make_connection()
    cursor = db.cursor()
    sql = "UPDATE User SET lastModifiedDate = '%s' WHERE Email= '%s'" %(update, email)
    try:
            cursor.execute(sql)
            db.commit()
            disconnect(db)
    except:
            db.rollback()
            cli_text_window.addstr("An unknown error ocurred when attempting to store your user info!", curses.color_pair(1))		

# main function that get users input inside the curses environment windows
def get_param(prompt_string, colorPair):
    cli_text_window.addstr(2, 2, prompt_string, curses.color_pair(colorPair))
    cli_text_window.clrtoeol()
    cli_text_window.refresh()
    input = stdscr.getstr(10, 10, 60)
    return input

def reSetScreens(bottom_line, status, menu):
    stdscr.clear()
    stdscr.addstr(" Advising Schedule Interface", curses.A_REVERSE) # what becomes the top bar
    stdscr.chgat(-1, curses.A_REVERSE) #then finishes the line off with blank space.
    cli_text_window = cli_window.subwin(curses.LINES-6, curses.COLS-4,3,2)
    cli_window.clear()
    setBottomMenu(bottom_line, status, menu)
    cli_window.box()
    cli_window.refresh()
    cli_text_window.clear()
    cli_text_window.refresh()
    cli_text_window.addstr(message, curses.color_pair(2))
    stdscr.refresh()

# Change colors of letters in the bottom menue
def setBottomMenu(bottom_line, statusIn, menu):
    
    stdscr.addstr(curses.LINES-1, 0, bottom_line + statusIn )
    if menu == 1: # Normal menu
        stdscr.chgat(curses.LINES-1,6, 2, curses.A_BOLD | curses.color_pair(2))# the M
        stdscr.chgat(curses.LINES-1,24, 1, curses.A_BOLD | curses.color_pair(1))# the Q
        stdscr.refresh()
    elif menu == 2:# Appointments Summary
        stdscr.chgat(curses.LINES-1,6, 2, curses.A_BOLD | curses.color_pair(2))# the UP
        stdscr.chgat(curses.LINES-1,12, 4, curses.A_BOLD | curses.color_pair(2))# the Down
        stdscr.chgat(curses.LINES-1,18, 2, curses.A_BOLD | curses.color_pair(4))# the No
        stdscr.chgat(curses.LINES-1,41, 1, curses.A_BOLD | curses.color_pair(1))# the X
        stdscr.refresh()	
    elif menu == 3:# Advising Session
        stdscr.chgat(curses.LINES-1,6, 2, curses.A_BOLD | curses.color_pair(1))# the X
        stdscr.chgat(curses.LINES-1,34, 1, curses.A_BOLD | curses.color_pair(2))# the C
        stdscr.refresh()	
    #set the logged-in/out color
    if LoggedIn is True:
        stdscr.chgat(curses.LINES-1,68, 10, curses.A_BOLD | curses.color_pair(2))
    elif LoggedIn is False:
        stdscr.chgat(curses.LINES-1,68, 10, curses.A_BOLD | curses.color_pair(1))
    
    	#cli_text_window.clear()
        #cli_text_window.addstr("Terminal size must be set to 80 x 24\n.  Quit, resize and relaunch!\n", curses.color_pair(1))
        #cli_text_window.refresh()

# this currently uses 9 char salting and md5 hashing -although this is probably fairly sucure there are more secure methods out there.
# this might be an alternative https://pypi.python.org/pypi/scrypt/
def operation_secure(password):
    salt = "3Km7!xc-B"
    pswd = hashlib.md5( salt + password + salt ).hexdigest()
    return pswd

def changePassword():
    cli_text_window.refresh()
    cli_text_window.clear()
    cli_text_window.addstr("You must change your password\n", curses.color_pair(1))
    newPwd1=''
    newPwd2=' '
    curses.noecho()# temp turn off echo so the pwd does not appear on the screen
    while newPwd1 != newPwd2:
        newPwd1 = get_param("Enter your new password.",0)
        cli_text_window.clear()
        cli_text_window.refresh()
        newPwd2 = get_param("Re-enter your new password.",0)
        cli_text_window.refresh()
        cli_text_window.clear()

        if newPwd1 != newPwd2:
            cli_text_window.clear()
            cli_text_window.addstr("passwords must match!", curses.color_pair(1))
    
    if newPwd1 == newPwd2:
        cli_window.clear()
        cli_text_window.clear()
        cli_window.box()
        cli_text_window.refresh()

        tempPwd = operation_secure(newPwd1)
        
        updatePassword(email, tempPwd)

#RETURNS ALL APPTS for a specified faculty email
#->empty list if no references exist
def GetAllAppts(db, FacultyEmail ):
    cursor = db.cursor()
    sql = "SELECT Id, FacultyName, FacultyEmail, StudentName, StudentEmail, Date, Status, TIME_FORMAT(StartTime, '%s') as STime, TIME_FORMAT(EndTime, '%s') as ETime FROM Appointment WHERE FacultyEmail='%s' ORDER BY Date DESC LIMIT 100 " %('%h:%i%p', '%h:%i%p',FacultyEmail)
    try:
        cursor.execute(sql)
        #create empty list
        results=[]
        if cursor.rowcount != 0:
            catch = cursor.fetchall()
            for r in catch:
              results.append({"Id": str(r[0]), "FacultyName": r[1], "FacultyEmail": r[2], "StudentName":r[3],"StudentEmail":r[4], "Date": r[5].strftime('%m/%d/%y'), "Status": r[6], "StartTime": r[7], "EndTime": r[8]}) 
              #results.append('Date: '+ str(r[5]) + '  Start time: ' + STime + '  End Time: '+ ETime + '  S Name: ' + str(r[3]) + ' S. Email: ' + str(r[4]) + '  Status: '+ str(r[6] ) )
    except:
        print"Error: Unable to fetch data: "  + sql
    return results

#returns appointment for passed in appointment ID
def GetAppt(db, apptId):
    cursor = db.cursor()
    #sql = "SELECT Id, FacultyName, FacultyEmail, StudentName, StudentEmail, Date, Status, CAST(StartTime AS CHAR) as StartTime, CAST(EndTime AS CHAR) as EndTime FROM Appointment WHERE Id='%s' " %(apptId)
    sql = "SELECT Id, FacultyName, FacultyEmail, StudentName, StudentEmail, Date, Status, TIME_FORMAT(StartTime, '%s') as STime, TIME_FORMAT(EndTime, '%s') as ETime FROM Appointment WHERE Id='%s' " %('%h:%i%p', '%h:%i%p', apptId)
    try:
        cursor.execute(sql)
        #create empty list
        results=[]
        if cursor.rowcount != 0:
            catch = cursor.fetchall()
            for r in catch:
              results.append({"Id": str(r[0]), "FacultyName": r[1], "FacultyEmail": r[2], "StudentName":r[3],"StudentEmail":r[4], "Date": r[5].strftime('%m/%d/%y'), "Status": r[6], "StartTime": r[7], "EndTime": r[8]}) 
              #results.append('Date: '+ str(r[5]) + '  Start time: ' + STime + '  End Time: '+ ETime + '  S Name: ' + str(r[3]) + ' S. Email: ' + str(r[4]) + '  Status: '+ str(r[6] ) )
    except:
        print"Error: Unable to fetch data: "  + sql
    return results

#prints the currently selected appointment and returns its id
def appt_summary(appts, summaryIndex): 
    #reSetScreens(bottom_line3, status5, 3)
    #determine ending range for appointments summary
    apptLength = len(appts)
    if summaryIndex+5 > apptLength:
        rangeEnd = apptLength
    else:
        rangeEnd = summaryIndex+5

    #determine page number
    page = (summaryIndex/5)+1

    cli_text_window.addstr("***************** ")
    cli_text_window.addstr("Appointments Summary, pg " + str(page), curses.color_pair(3))
    cli_text_window.addstr(" ****************\n\n")
    cli_text_window.addstr('No.  Date      Begin    End      Status    \tStudent\n', curses.color_pair(3))
    refNo = 1 
    apptId ={} 
    
    #return only appointments in provided range
    #this splits appointments displayed into a subset of total appointments
    for index in range(summaryIndex, rangeEnd):
        appts_str = str(refNo)
        appts_str += '    '+str(appts[index].get("Date"))
        appts_str +='  '+str(appts[index].get("StartTime"))
        appts_str +='  '+str(appts[index].get("EndTime"))
        appts_str +='  '+str(appts[index].get("Status"))
        appts_str +='\t'+str(appts[index].get("StudentName"))
        cli_text_window.addstr(appts_str + '\n\n')
        apptId[str(refNo)] = appts[index].get("Id")
        refNo+=1
    return (apptId, refNo)

#prints the currently selected appointment and returns its id     
def appt_print(appt):    
    cli_text_window.refresh()
    cli_text_window.clear()
    cli_text_window.addstr("\n\n")
    cli_text_window.addstr("***************** ")
    cli_text_window.addstr("Advising Session", curses.color_pair(3))
    cli_text_window.addstr(" *****************\n")
    cli_text_window.addstr("\nDate: ")
    cli_text_window.addstr(str(appt[0].get("Date")) + '\n', curses.color_pair(3))
    cli_text_window.addstr("Time: ")
    cli_text_window.addstr(str(appt[0].get("StartTime")) + ' - ' + str(appt[0].get("EndTime")) +'\n\n', curses.color_pair(3))
    cli_text_window.addstr("Student Name: ")
    cli_text_window.addstr(str(appt[0].get("StudentName")) + '\n', curses.color_pair(3) )
    cli_text_window.addstr("Student Email: ")
    cli_text_window.addstr(str(appt[0].get("StudentEmail")) + '\n', curses.color_pair(3) )
    cli_text_window.addstr("Status: ")
    cli_text_window.addstr(str(appt[0].get("Status")) + '\n', curses.color_pair(3) )
    current_id = appt[0].get("Id")
    return current_id

#Special loop seperated out to get user input in the asvising system screen - 
 # note the x below here only works in Avising session the other one is bellow in code
def getSpecificID(appt):

    reSetScreens(bottom_line3, status5, 3)
    current_id = appt_print(appt)
    running = True
    while running:
        c2 = cli_text_window.getch()

        if c2 == ord('c') or c2 == ord('C'):
            confirmation = get_param("\nC to confirm or any other key to cancel. Followed with Enter:" ,2)
            cli_text_window.addstr("\n Processing...                                                ", curses.color_pair(2))
            cli_text_window.refresh()
            if confirmation == 'c' or confirmation == 'C':
                confirmation = ''
                message = ''
                cursor = db.cursor()
                #send cancellation email
                apptTime = appt[0].get("StartTime") + " - " + appt[0].get("EndTime")
                if appt[0].get("Status") == "Accepted":
                    cancellationEmail(appt[0].get("StudentName"), appt[0].get("StudentEmail"), appt[0].get("Date"), apptTime, appt[0].get("FacultyName"), appt[0].get("FacultyEmail"))
                else:
                    pendingCancellationEmail(appt[0].get("StudentName"), appt[0].get("StudentEmail"), appt[0].get("Date"), apptTime, appt[0].get("FacultyName"), appt[0].get("FacultyEmail"))

                try:	
                        #cursor.execute(""" Delete FROM Appointment WHERE Id=%s """,(current_id) )
                        #db.commit()
                        cli_text_window.addstr("\n Appointment Removed...Redirecting to Appointments summary", curses.color_pair(4))
                except:
                        cli_text_window.addstr("Database update error.", curses.color_pair(1))

                #show appt removed message, wait then redirect to appointment summary listing
                cli_text_window.refresh()
                cli_text_window.clear()
                time.sleep(2)
                menu = 3 
                message = ''
                running = False
                reSetScreens(bottom_line2, status4, 2)
            
            elif confirmation != 'c' or confirmation != 'C':
                cli_text_window.addstr("\n Transaction canceled.", curses.color_pair(1))
                cli_text_window.refresh()
                cli_text_window.clear()
                time.sleep(.90)
                reSetScreens(bottom_line3, status5, 3)
                appt_print(appt)	
                
        elif c2 == ord('x') or c2 == ord('X'):
            running = False
            menu = 3 
            message = ''
            cli_text_window.refresh()
            cli_text_window.clear()
            reSetScreens(bottom_line2, status4, 2)
        
        c2 = '' #prevents infinite looping in the menue
           
def sendEmail (msg, subject):
    # Create a text/plain message
    message = MIMEText(msg)
    message['Subject'] = subject
    message['From'] = fromaddr 
    message['To'] = toaddr

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toaddr, message.as_string())
    server.quit()

def forgotPwdEmail (tempPwd, toEmail):
    # Create a text/plain message
    msg = "Your temporary password is: %s.  Use this to log in to the Appointment CLI.  You will be prompted to change your password to one of your choosing.\n\nEnjoy!" %(tempPwd)
    message = MIMEText(msg)
    message['Subject'] = "Appointment CLI Password Reset"
    message['From'] = fromaddr 
    message['To'] =toEmail 

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toEmail, message.as_string())
    server.quit()

def newUserEmail (tempPwd, toEmail):
    # Create a text/plain message
    msg = "Welcome to the Appointment CLI!\n\nYour temporary password is: %s.  Use this to log in to the Appointment CLI for the first time.  You will be prompted to change your password to one of your choosing.\n\nEnjoy!" %(tempPwd)
    message = MIMEText(msg)
    message['Subject'] = "Appointment CLI New User"
    message['From'] = fromaddr 
    message['To'] = toEmail

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toEmail, message.as_string())
    server.quit()

def cancellationEmail (sName, sEmail, date, time, aName, aEmail):
    # Create a text/plain message
    msg = "Advising Signup with %s CANCELLED\nName: %s\nEmail: %s\nDate: %s\nTime: %s\n\nPlease contact support@engr.oregonstate.edu if you experience problems" %(aName, sName, sEmail, date, time)
    message = MIMEText(msg)
    recipients = [sEmail,aEmail]
    message['Subject'] = "Advising Signup Cancellation"
    message['From'] = fromaddr 
    message['To'] = ", ".join(recipients)

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, recipients, message.as_string())
    server.quit()

def pendingCancellationEmail (sName, sEmail, date, time, aName, aEmail):
    # Create a text/plain message
    msg = "Advising Signup with %s CANCELLED\nName: %s\nEmail: %s\nDate: %s\nTime: %s\n\nPlease contact support@engr.oregonstate.edu if you experience problems" %(aName, sName, sEmail, date, time)
    message = MIMEText(msg)
    recipients = [sEmail,aEmail]
    message['Subject'] = "Advising Signup Pending Appointment Cancellation"
    message['From'] = fromaddr 
    message['To'] = ", ".join(recipients)

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, recipients, message.as_string())
    server.quit()

#random temporary password generator
#sourced from stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
def randomGenerator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# *********   Set up screens  ***************************************************************************************
# Begin Program and set initial screen

try:
	stdscr = curses.initscr()
except:
	print "Problem initializing base screen."

# Propery initialize the screen
curses.noecho()  #dont echo chars as I type
curses.cbreak()  #set into char break mode
curses.curs_set(0) # hide the curser

#Check for and begin color support
if curses.has_colors():
	curses.start_color()

# Initiallizse the color combinations we're going to use
#init_color(COLOR_YELLOW, 1000, 500, 0);
curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)

# Make the top bar
stdscr.addstr(" Advising Schedule Interface", curses.A_REVERSE) # what becomes the top bar
stdscr.chgat(-1, curses.A_REVERSE) #then finishes the line off with blank space.

# Set up the base window
try:
	cli_window = curses.newwin(curses.LINES-2,curses.COLS, 1,0)
except:
	print "Problem initializing new window."

# Create a sub-window so as to clearly display the text with out overwriting the quote window borders.
try:
	cli_text_window = cli_window.subwin(curses.LINES-6, curses.COLS-4,3,2)
except:
	print "Problem initializing cli_window."

# get the size of the text window for later use
	dims = cli_text_window.getmaxyx()
	#dims2 = stdscr.getmaxyx()
	#cli_text_window.addstr("base: " + dims + "text: " + dims2 + "\n", curses.color_pair(2))

# Text to go in lower text box made by using both iner and outer window
message = "Welcome to the Curses based CLI!"
cli_text_window.addstr(message) # this is the start up screen

setBottomMenu(bottom_line, status, 1)

# Draw a boarder arround the main quote window
cli_window.box()

#Update the internal window data structures
stdscr.noutrefresh()
cli_window.noutrefresh()

# Redraw the screen
curses.doupdate()


# *********   Create the event loop  ***************************************************************************************
while True:
    c =  cli_window.getch()
    cli_text_window.clear()
    cli_text_window.refresh()
    curses.echo(0)
    # First menu if not logged in **********************************
    if not LoggedIn:
        if c == ord('m') or c == ord('M'):
            cli_text_window.refresh()
            cli_text_window.clear()
            cli_text_window.addstr(action_menu, curses.color_pair(2))
            setBottomMenu(bottom_line, status, 1)

            dims = cli_text_window.getmaxyx()
            dims2 = stdscr.getmaxyx()
            #cli_text_window.addstr("\n base: " + str(dims2) + "text: " + str(dims) + "\n", curses.color_pair(2))
                
        if c == ord('1'): #register menu item -not logged in
            curses.echo(1) 
            curses.curs_set(1)
            cli_text_window.refresh()
            cli_text_window.clear()
            
            addr1 = ''
            pswd1 = ''
            addr1 = get_param("Enter your email address:",0)
            cli_text_window.clear()
            cli_text_window.addstr("Processing..\n", curses.color_pair(2))
            cli_text_window.refresh()
            cli_text_window.clear()
            #check if email already exists in db
            db = make_connection()
            cursor = db.cursor()

            sql = "SELECT * FROM User WHERE Email = '%s' ORDER BY id DESC LIMIT 1" %(addr1)

            try:
                cursor.execute(sql)
                if cursor.rowcount != 0:
                    cli_text_window.addstr("User already exists. Try again.\n", curses.color_pair(2))
                else:
                    #send email with temp password
                    tempPwd = randomGenerator()
                    newUserEmail(tempPwd, addr1)
                    # prepare the password for secure storage in the database by hashing and salting it.
                    saltedPwd = operation_secure(tempPwd)
                    insertNewUsser(addr1, saltedPwd)

                    cli_text_window.refresh()
                    cli_text_window.clear()	
                    cli_window.box()
                    curses.curs_set(0)
                    curses.echo(0)
                    cli_text_window.refresh()
                    cli_text_window.addstr("A temporary password has been sent to your email address.\n")
                    cli_text_window.addstr("Check your email, then return to login page to sign in.")
            except:
                print"Error: Unable to fetch data."
                        

        if c == ord('2'):# login menue item -not logged in
            cli_text_window.refresh()
            cli_text_window.clear()	
            curses.echo(1) 
            curses.curs_set(1)
            cli_text_window.refresh()
            cli_text_window.clear()
            email = get_param("Enter your email address.",0)
            cli_text_window.refresh()
            cli_text_window.clear()
            curses.noecho()# temp turn off echo so the pwd does not appear on the screen
            pswd = get_param("Enter your password.",0)
            curses.echo()# temp turn echo back on
            cli_text_window.refresh()
            # pull the latest email and password entered.
            db = make_connection()
            cursor = db.cursor()

            sql = "SELECT * FROM User WHERE Email = '%s' ORDER BY id DESC LIMIT 1" %(email)

            try:
                cursor.execute(sql)
                if cursor.rowcount == 0:
                    cli_window.clear()
                    cli_text_window.clear()
                    cli_window.box()
                    cli_text_window.refresh()
                    cli_text_window.addstr("No user in database", curses.color_pair(1))
                else:
                    results = cursor.fetchall()
                    for row in results:
                        stored_email = row[1]
                        stored_password = row[2]
                        lastModified = row[3]
                        secured_pswd = operation_secure(pswd)
                    if secured_pswd == stored_password and email == stored_email:
                        LoggedIn = True
                        cli_window.clear()
                        cli_text_window.clear()
                        cli_window.box()
                        cli_text_window.refresh()
                        if lastModified is None:
                            changePassword()
                            updateDate(email, date.datetime.today())
                            setBottomMenu(bottom_line, status3, 1)
                        else:
                            setBottomMenu(bottom_line, status3, 1)
                            stdscr.chgat(curses.LINES-1,68, 10, curses.A_BOLD | curses.color_pair(2))
                            cli_text_window.addstr("You have been logged in.", curses.color_pair(3))
                    else:
                        disconnect(db)
                        cli_window.clear()
                        cli_text_window.clear()
                        cli_window.box()
                        cli_text_window.refresh()
                        cli_text_window.addstr("Your email or password did not match -try again!.", curses.color_pair(1))
                    # set echo and curser back to original

                    curses.echo(0) 
                    curses.curs_set(0)
            except:
                print"Error: Unable to fetch data."
            c = ''
            curses.echo(0) 
            #cli_text_window.refresh()
            #cli_text_window.clear()	
            #cli_window.box()

        if c == ord('3'):#forgotten password menue item -not logged in
            curses.echo(1) 
            curses.curs_set(1)
            cli_text_window.refresh()
            cli_text_window.clear()    
            addr1 = ''
            pswd1 = ''
            addr1 = get_param("Enter your email address:",0)
            
            cli_text_window.clear()
            cli_text_window.addstr("Processing..\n", curses.color_pair(2))
            cli_text_window.refresh()
            cli_text_window.clear()

            curses.curs_set(0)
            curses.echo(0)
            #send email with temp password
            tempPwd = randomGenerator()

            forgotPwdEmail(tempPwd, addr1)
            # prepare the password for secure storage in the database by hashing and salting it.
            saltedPwd = operation_secure(tempPwd)
            updatePassword(addr1, saltedPwd)
            updateDate(addr1, None)

            cli_text_window.refresh()
            cli_text_window.clear()	
            cli_window.box()
            cli_text_window.refresh()
            
            cli_text_window.addstr("A temporary password has been sent to your email address.\n", curses.color_pair(4))
            cli_text_window.addstr("Check your email, then return to login page.", curses.color_pair(4))

    # Second menu if user is logged in **********************************        
    else:
        if c == ord('m') or c == ord('M'):
            cli_text_window.refresh()
            cli_text_window.clear()
            cli_text_window.addstr(logged_menu, curses.color_pair(2))
            #setBottomMenu(bottom_line, status3, 1)

        if c == ord('1'):

            cli_text_window.keypad(1)# turns on key pad for up and down arrow detection           

            if LoggedIn is False:
                cli_text_window.addstr("You must log in first!", curses.color_pair(1))
            else:           
                #get appointments
                reSetScreens(bottom_line2, status4, 2)
                
                appts = GetAllAppts(db, email)
                num = len(appts)
                appts_number = 0# number of appointments in the summary screen 

                if num > 0:
                    running = True
                    #show first 5 appointments
                    summaryIndex = 0 
                    endSummary = False
                    
                    apptIds, appts_number = appt_summary(appts, summaryIndex)
                    #setBottomMenu(bottom_line2, status4, 2)
                    while running:
                        c2 = cli_text_window.getch()
                        
                        if c2 == curses.KEY_DOWN: 
                            cli_text_window.refresh()
                            cli_text_window.clear()
                            if summaryIndex+5 > num-1:
                                endSummary = True
                                cli_text_window.addstr("End of summary reached.", curses.color_pair(1))
                            else:
                                summaryIndex += 5
                                apptIds, appts_number = appt_summary(appts, summaryIndex)
                                #appts_number -= 1 #used to keep user entered number menu from over indexing and producing an error
                        
                        elif c2 == curses.KEY_UP:
                            #if keying up from End of summary prompt, then reset summaryIndex to view last page
                            if endSummary:
                                summaryIndex += 5
                                endSummary = False
                            if summaryIndex - 5 >= 0:
                                cli_text_window.refresh()
                                cli_text_window.clear()
                                summaryIndex -= 5
                                apptIds, appts_number = appt_summary(appts, summaryIndex)
                                #appts_number -= 1 #used to keep next menu item from over indexing and producing an error
                        
                        # Gets user appointment number input from Appointments status menu
                        elif c2 == ord('1') or c2 == ord('2') or c2 == ord('3') or c2 == ord('4') or c2 == ord('5'):
                                            
                            if( int(chr(c2)) <= (appts_number-1) ):
                                cli_text_window.refresh()
                                cli_text_window.clear()

                                user_apptId = apptIds[chr(c2)]  
                                #get info for this appt only
                                appt = GetAppt(db, user_apptId)
                                #display appt, and give cancellation options
                                getSpecificID(appt)
                                #get updated appointment info 
                                
                                appts = GetAllAppts(db, email)
                                apptIds, appts_numbers = appt_summary(appts, summaryIndex)
                                c2 =''
                            else:
                                cli_text_window.addstr("Sorry that choice is not valid on this page. \n", curses.color_pair(1))
                           
                        elif c2 == ord('x') or c2 == ord('X'):
                            running = False
                       
                            message = ''
                            cli_text_window.refresh()
                            cli_text_window.clear()
                            setBottomMenu(bottom_line, status3, 1)
                            	
                       # else:
                            #cli_text_window.addstr("Not a valid option, try again\n", curses.color_pair(1))     
                            
                else:                 
                    cli_text_window.addstr("There was an error or you have no appointments in the database!.", curses.color_pair(1))	
                    setBottomMenu(bottom_line, status3, 1)
                    

        if c == ord('2'):# change password
            secured_pswd = ''
            stored_password = ' '
            cli_text_window.refresh()
            cli_text_window.clear()	
            while secured_pswd != stored_password:
                curses.curs_set(1)
                curses.noecho()# temp turn off echo so the pwd does not appear on the screen
                pswd = get_param("Enter your current password.",0)
                curses.echo()# temp turn echo back on
                cli_text_window.refresh()
                # pull the latest email and password entered.
                db = make_connection()
                cursor = db.cursor()

                sql = "SELECT * FROM User WHERE Email = '%s' ORDER BY id DESC LIMIT 1" %(email)

                try:
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    for row in results:
                        stored_email = row[1]
                        stored_password = row[2]
                        secured_pswd = operation_secure(pswd)
                except:
                    print"Error: Unable to fetch data."

                if secured_pswd != stored_password:
                    cli_text_window.clear()
                    cli_text_window.addstr("Password did not match, try again.", curses.color_pair(3))
                    cli_text_window.refresh()
                    cli_text_window.clear()
            if secured_pswd == stored_password:
                changePassword()
                curses.echo(0)
            else:
                cli_text_window.addstr("Your password did not match.", curses.color_pair(3))

        if c == ord('3'):#logout
            cli_text_window.refresh()
            cli_text_window.clear()
            if LoggedIn:
                disconnect(db)
                #status =  "                                 logged-out";
                LoggedIn = False;
                setBottomMenu(bottom_line, status, 1)
                cli_text_window.addstr("You have been logged out.", curses.color_pair(3))
            else:
                cli_text_window.addstr("You must be logged in to log out!.", curses.color_pair(1))
            
    
    if c == ord('e') or c == ord('E'):
        q =-1
        x, y = 0, 0
        vert = 1
        hor = 1
        cli_text_window.nodelay(1)
        while q < 0:
            cli_text_window.clear()
            cli_text_window.addstr(y, x, 'Bow Ties are Cool!')
            cli_text_window.refresh()
            y += vert
            x += hor
            if y == dims[0] -1:
                vert = -1
            elif y == 0:
                vert = 1
            if x == dims[1] - len('Bow Ties are Cool!')-1:
                hor = -1
            elif x == 0:
                hor = 1
            q = cli_text_window.getch()
            time.sleep(0.1)

    elif c == ord('q') or c == ord ('Q'):
        curses.endwin()
        break
    
    # Refresh the windows from the bottom up
    stdscr.noutrefresh()
    cli_window.noutrefresh()
    cli_text_window.noutrefresh()
    curses.doupdate()

# Restore the terminal settings
curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.curs_set(1)

# Restore the terminal intself to its "former glory"
curses.endwin()


