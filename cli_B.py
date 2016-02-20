#!/usr/bin/python

# Advising Schedule Interface 
# version 1.25
# Authors:  Rob Sparks, Susan Lee

import curses
from urllib2 import urlopen
from HTMLParser import HTMLParser
from simplejson import loads
import mysql.connector
from mysql.connector import errorcode
from os import system
import time
import MySQLdb
import hashlib
import smtplib
from email.mime.text import MIMEText

LoggedIn = False;
action_menu = "Enter the number to perform the action.\n---------------------------------------\n1. Store your email account info in the database \n2. Login\n"
logged_menu = "Enter the number to perform the action.\n---------------------------------------\n1. Logout\n2. View Advising Schedule"
bottom_line = "Press 'M' to see Menu. 'Q' to quit."
bottom_line2 = "Press UP or DOWN arrow, X to drop out to appt list, C to cancel apt."
bottom_line3 = "Press UP or DOWN, No. to select an appt, X to drop out to main menu."
#varConnected = False;
status =  "                                 logged-out";
status2 =  "logged-out";

# ****  Email Settings *****************
# These setting need to updated to instructor's email 
fromaddr = 'procmailtestscs@gmail.com'
toaddr  = 'procmailtestscs@gmail.com'
username = 'procmailtestscs'
password = 'gobeavers!'
#***************************************


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
		cli_text_window.addstr("Your information was stored sucessfully.", curses.color_pair(3))
		disconnect(db)
	except:
		db.rollback()
		cli_text_window.addstr("An unknown error ocurred when attempting to store your user info!", curses.color_pair(1))		

def get_param(prompt_string, colorPair):
    stdscr.addstr(2, 2, prompt_string, curses.color_pair(colorPair))
    stdscr.clrtoeol()
    stdscr.refresh()
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

def setBottomMenu(bottom_line, status, menu):# Change color of certain letters in the bottom menue
    stdscr.addstr(curses.LINES-1, 0, bottom_line + status )
    if menu == 1:
        stdscr.chgat(curses.LINES-1,6, 2, curses.A_BOLD | curses.color_pair(2))# the M
        stdscr.chgat(curses.LINES-1,24, 1, curses.A_BOLD | curses.color_pair(1))# the Q
        stdscr.refresh()
    elif menu == 2:
        stdscr.chgat(curses.LINES-1,6, 2, curses.A_BOLD | curses.color_pair(2))# the UP
        stdscr.chgat(curses.LINES-1,12, 4, curses.A_BOLD | curses.color_pair(2))# the Down
        stdscr.chgat(curses.LINES-1,24, 1, curses.A_BOLD | curses.color_pair(1))# the X
        stdscr.chgat(curses.LINES-1,52, 1, curses.A_BOLD | curses.color_pair(4))# the X
        stdscr.refresh()	
    elif menu == 3:
        stdscr.chgat(curses.LINES-1,6, 2, curses.A_BOLD | curses.color_pair(2))# the UP
        stdscr.chgat(curses.LINES-1,12, 4, curses.A_BOLD | curses.color_pair(2))# the Down
        stdscr.chgat(curses.LINES-1,18, 3, curses.A_BOLD | curses.color_pair(4))# apt number
        stdscr.chgat(curses.LINES-1,41, 1, curses.A_BOLD | curses.color_pair(1))# the X
        stdscr.refresh()	
    #set the logged-in/out color
    if LoggedIn is True:
        stdscr.chgat(curses.LINES-1,68, 10, curses.A_BOLD | curses.color_pair(2))
    elif LoggedIn is False:
        stdscr.chgat(curses.LINES-1,68, 10, curses.A_BOLD | curses.color_pair(1))

# this currently uses 9 char salting and md5 hashing -although this is probably fairly sucure there are more secure methods out there.
# this might be an alternative https://pypi.python.org/pypi/scrypt/
def operation_secure(password):
    salt = "3Km7!xc-B"
    pswd = hashlib.md5( salt + password + salt ).hexdigest()
    return pswd

#RETURNS ALL APPTS for a specified faculty email
#->empty list if no references exist
def GetAllAppts(db, FacultyEmail ):
    cursor = db.cursor()
    sql = "SELECT Id, FacultyName, FacultyEmail, StudentName, StudentEmail, Date, Status, CAST(StartTime AS CHAR) as StartTime, CAST(EndTime AS CHAR) as EndTime FROM Appointment WHERE FacultyEmail='%s' ORDER BY Date DESC LIMIT 75 " %(FacultyEmail)

    try:
        cursor.execute(sql)
        #create empty list
        results=[]
        if cursor.rowcount != 0:
            catch = cursor.fetchall()
            for r in catch:
              #format time object
              #source: stackoverflow.com/questions/904746/how-to-remove-all-characters-after-a-specific-character-in-python
              STime = ':'.join(str(r[7]).split(':')[:-1])
              ETime = ':'.join(str(r[8]).split(':')[:-1])

              results.append({"Id": str(r[0]), "FacultyName": r[1], "FacultyEmail": r[2], "StudentName":r[3],"StudentEmail":r[4], "Date": r[5].strftime('%m/%d/%y'), "Status": r[6], "StartTime": STime, "EndTime": ETime}) 
              #results.append('Date: '+ str(r[5]) + '  Start time: ' + STime + '  End Time: '+ ETime + '  S Name: ' + str(r[3]) + ' S. Email: ' + str(r[4]) + '  Status: '+ str(r[6] ) )
    except:
        print"Error: Unable to fetch data: "  + sql
    return results

#returns appointment for passed in appointment ID
def GetAppt(db, apptId):
    cursor = db.cursor()
    sql = "SELECT Id, FacultyName, FacultyEmail, StudentName, StudentEmail, Date, Status, CAST(StartTime AS CHAR) as StartTime, CAST(EndTime AS CHAR) as EndTime FROM Appointment WHERE Id='%s' " %(apptId)

    try:
        cursor.execute(sql)
        #create empty list
        results=[]
        if cursor.rowcount != 0:
            catch = cursor.fetchall()
            for r in catch:
              #format time object
              #source: stackoverflow.com/questions/904746/how-to-remove-all-characters-after-a-specific-character-in-python
              STime = ':'.join(str(r[7]).split(':')[:-1])
              ETime = ':'.join(str(r[8]).split(':')[:-1])

              results.append({"Id": str(r[0]), "FacultyName": r[1], "FacultyEmail": r[2], "StudentName":r[3],"StudentEmail":r[4], "Date": r[5].strftime('%m/%d/%y'), "Status": r[6], "StartTime": STime, "EndTime": ETime}) 
              #results.append('Date: '+ str(r[5]) + '  Start time: ' + STime + '  End Time: '+ ETime + '  S Name: ' + str(r[3]) + ' S. Email: ' + str(r[4]) + '  Status: '+ str(r[6] ) )
    except:
        print"Error: Unable to fetch data: "  + sql
    return results

def appt_summary(appts, summaryIndex): #prints the currently selected appointment and returns its id
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
    cli_text_window.addstr('No.  Date \tBegin   End  Student  Status\t\t\n', curses.color_pair(3))
    refNo = 1 
    apptId ={} 
    
    #return only appointments in provided range
    #this splits appointments displayed into a subset of total appointments
    for index in range(summaryIndex, rangeEnd):
        appts_str = str(refNo)
        appts_str += '    '+str(appts[index].get("Date"))
        appts_str +='  '+str(appts[index].get("StartTime"))
        appts_str +='  '+str(appts[index].get("EndTime"))
        appts_str +='  '+str(appts[index].get("StudentName"))
        appts_str +='\t'+str(appts[index].get("Status"))
        cli_text_window.addstr(appts_str + '\n\n')
        apptId[str(refNo)] = appts[index].get("Id")
        refNo+=1

    return apptId

def appt_print(appt): #prints the currently selected appointment and returns its id
        
    cli_text_window.refresh()
    cli_text_window.clear()
    cli_text_window.addstr("\n")
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

def getSpecificID(appt):
    menu = 2
    status2 = "logged-in"

    reSetScreens(bottom_line2, status2, menu)
    current_id = appt_print(appt)
    running = True
    while running:
        c2 = cli_text_window.getch()

        if c2 == ord('c') or c2 == ord('C'):
            confirmation = get_param("C to confirm or any other key to cancel. Followed with Enter:" ,2)
            if confirmation == 'c' or confirmation == 'C':
                confirmation = ''
                message = ''
                #status = 'Pending' # just for testingx
                status = 'Pending Cancellation'
                cursor = db.cursor()

                try:	
                        cursor.execute(""" UPDATE Appointment SET Status=%s WHERE Id=%s """,(status, current_id) )
                        db.commit()
                        cli_text_window.addstr("\n Status Changed.", curses.color_pair(1))
                except:
                        cli_text_window.addstr("Database update error.", curses.color_pair(1))

                #send cancellation email
                sendemail(current_id)
                #get udpated appt info
                appt = GetAppt(db, current_id)
                cli_text_window.refresh()
                cli_text_window.clear()
                time.sleep(1.25)
                reSetScreens(bottom_line2, status2, menu)
                appt_print(appt)
            
            elif confirmation != 'c' or confirmation != 'C':
                cli_text_window.addstr("\n Canceled.", curses.color_pair(1))
                cli_text_window.refresh()
                cli_text_window.clear()
                time.sleep(.90)
                reSetScreens(bottom_line2, status2, menu)
                appt_print(appt)	
                
        elif c2 == ord('x') or c2 == ord('X'):
            running = False
            menu = 3 
            message = ''
            cli_text_window.refresh()
            cli_text_window.clear()
            reSetScreens(bottom_line3, status2, menu)
        
        c2 = '' #prevents infinite looping in the menue
           
def sendemail (apptId):
    # Create a text/plain message
    message = MIMEText(apptId)
    message['Subject'] = "Advising Signup Cancellation"
    message['From'] = fromaddr 
    message['To'] = toaddr

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toaddr, message.as_string())
    server.quit()

# *********   Set up screens  ***************************************************************************************
# Begin Program and set initial screen
stdscr = curses.initscr()

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
cli_window = curses.newwin(curses.LINES-2,curses.COLS, 1,0)

# Create a sub-window so as to clearly display the text with out overwriting the quote window borders.
cli_text_window = cli_window.subwin(curses.LINES-6, curses.COLS-4,3,2)

# Text to go in lower text box made by using both iner and outer window
message = "Welcome to the Curses based CLI!"
cli_text_window.addstr(message) # this is the start up screen

menu = 1
setBottomMenu(bottom_line, status, menu)

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
    if not LoggedIn:
        if c == ord('m') or c == ord('M'):
            cli_text_window.refresh()
            cli_text_window.clear()
            cli_text_window.addstr(action_menu, curses.color_pair(2))
            setBottomMenu(bottom_line, status, menu)
                
        if c == ord('1'):
            curses.echo(1) 
            curses.curs_set(1)
            cli_text_window.refresh()
            cli_text_window.clear()
            
            addr1 = ''
            addr2 = ' '
            message = ''
            pswd1 = ''
            pswd2 = ' '
            counter = 0
            adminPswd = "f739a6fb430139341721e5d011cfa671"
            curses.noecho()# temp turn off echo so the pwd does not appear on the screen
            adminPwsdEntered = get_param("Enter the admin password to continue:" ,0)
            curses.echo()
            tempPwd = operation_secure(adminPwsdEntered)
            cli_text_window.refresh()
            cli_text_window.clear()

            if tempPwd == adminPswd:
                cli_text_window.refresh()
                cli_text_window.clear()
                while addr1 != addr2:
                    addr1 = get_param("Enter your email address:" ,0)
                    cli_text_window.refresh()
                    cli_text_window.clear()	
                    addr2 =  get_param("Re-enter your email address: " ,0)
                    cli_text_window.refresh()
                    cli_text_window.clear()	

                    if addr1 != addr2:
                        cli_text_window.clear()
                        cli_text_window.addstr("Email addresses must match!", curses.color_pair(1))
                        cli_text_window.refresh()
                        cli_text_window.clear()

                if addr1 == addr2:
                    cli_text_window.refresh()
                    cli_window.box()
                    cli_text_window.clear()
                    cli_window.clear()

                while pswd1 != pswd2:
                    pswd1 = get_param("Enter your password:",0) 
                    cli_text_window.clear()	
                    cli_text_window.refresh()
                    pswd2 = get_param("Re-enter your password:",0)
                    cli_text_window.refresh()
                    cli_text_window.clear()
                    
                    if pswd1 != pswd2: 
                        cli_text_window.clear()
                        cli_text_window.addstr("passwords must match!", curses.color_pair(1))
                        cli_text_window.refresh()
                        cli_text_window.clear()

                if pswd1 == pswd2:
                    cli_window.clear()
                    cli_text_window.clear()
                    cli_window.box()
                    cli_text_window.refresh()
                    # set echo and curser back to original
                    curses.echo(0) 
                    curses.curs_set(0)

                # prepare the password for secure storage in the database by hashing and salting it.
                tempPwd = operation_secure(pswd1)
                insertNewUsser(addr1, tempPwd)

            elif tempPwd != adminPswd:
                cli_window.box()
                cli_text_window.refresh()
                cli_text_window.clear()
                cli_text_window.addstr("The password was not correct!", curses.color_pair(1))
                curses.echo(0) 
                curses.curs_set(0)
                        

        if c == ord('2'):# login
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

            # TO DO: change the querry to allow mult users with addition of where email...
            # But this may open up some security concerns. -We need to think about a sollution.

            sql = "SELECT * FROM User ORDER BY id DESC LIMIT 1"

            try:
                cursor.execute(sql)
                results = cursor.fetchall()
                for row in results:
                    stored_email = row[1]
                    stored_password = row[2]
                    secured_pswd = operation_secure(pswd)
            except:
                print"Error: Unable to fetch data."
            
            if secured_pswd == stored_password and email == stored_email:
                LoggedIn = True;
                status =  "                                  logged-in";#idfferent spacing versions used in different cases
                status2 =  " logged-in";
                cli_window.clear()
                cli_text_window.clear()
                cli_window.box()
                cli_text_window.refresh()
                stdscr.addstr(curses.LINES-1, 0, bottom_line + status )
                setBottomMenu(bottom_line, status, menu)
                stdscr.chgat(curses.LINES-1,68, 10, curses.A_BOLD | curses.color_pair(2))
                cli_text_window.addstr("You have been logged in.", curses.color_pair(3))
                time.sleep(.03)
                c = ord('M')
            else:
                disconnect(db)
                cli_window.clear()
                cli_text_window.clear()
                cli_window.box()
                cli_text_window.refresh()
                cli_text_window.addstr("Your email or password did not match -try again!.", curses.color_pair(1))
                time.sleep(.03)
                c = ord('M')
            # set echo and curser back to original
            curses.echo(0) 
            curses.curs_set(0)
    else:
        if c == ord('m') or c == ord('M'):
            cli_text_window.refresh()
            cli_text_window.clear()
            cli_text_window.addstr(logged_menu, curses.color_pair(2))
            setBottomMenu(bottom_line, status, menu)
        if c == ord('1'):#logout
            cli_text_window.refresh()
            cli_text_window.clear()
            try:
                disconnect(db)
                status =  "                                 logged-out";
                LoggedIn = False;
                setBottomMenu(bottom_line, status, menu)
                cli_text_window.addstr("You have been logged out.", curses.color_pair(3))
            except:
                cli_text_window.addstr("You must be logged in to log out!.", curses.color_pair(1))
            

        if c == ord('2'):
            cli_text_window.refresh()
            cli_text_window.clear()
            cli_text_window.keypad(1)
            menu = 3 
            message = ''

            if LoggedIn is False:
                cli_text_window.addstr("You must log in first!", curses.color_pair(1))
            else:           
                #get appointments
                appts = GetAllAppts(db, email)
                num = len(appts)
                
                if num > 0:
                    running = True
                    reSetScreens(bottom_line3, status2, menu)
                    #show first 5 appointments
                    summaryIndex = 0 
                    endSummary = False
                    apptIds = appt_summary(appts, summaryIndex)
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
                                apptIds = appt_summary(appts, summaryIndex)
                        
                        elif c2 == curses.KEY_UP:
                            #if keying up from End of summary prompt, then reset summaryIndex to view last page
                            if endSummary:
                                summaryIndex += 5
                                endSummary = False
                            if summaryIndex - 5 >= 0:
                                cli_text_window.refresh()
                                cli_text_window.clear()
                                summaryIndex -= 5
                                apptIds = appt_summary(appts, summaryIndex)
                        
                        elif c2 == ord('1') or c2 == ord('2') or c2 == ord('3') or c2 == ord('4') or c2 == ord('5'):
                            cli_text_window.refresh()
                            cli_text_window.clear()
                            apptId = apptIds[chr(c2)]                   
                            #get info for this appt only
                            appt = GetAppt(db, apptId)
                            #display appt, and give cancellation options
                            getSpecificID(appt)
                            #get updated appointment info 
                            appts = GetAllAppts(db, email)
                            apptIds = appt_summary(appts, summaryIndex)
                        
                        elif c2 == ord('x') or c2 == ord('X'):
                            running = False
                            menu = 1 
                            message = ''
                            cli_text_window.refresh()
                            cli_text_window.clear()
                            reSetScreens(bottom_line, status2, menu)
                            
                else:
                    cli_text_window.addstr("There was an error or you have no appointments in the database!.", curses.color_pair(1))	                        
    
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


