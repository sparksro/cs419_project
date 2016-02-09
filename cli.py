#!/usr/bin/python

# Advising Schedule Interface 
# version 1.10

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

LoggedIn = False;
action_menue = "Enter the number to perform the action.\n---------------------------------------\n1. Store your email account info in the database \n2. Login\n3. Logout\n4. View Advising Schedule"
bottom_line = "Press 'M' to see Menu. 'Q' to quit."

varConnected = False;
status =  "                                 logged-out";
db = '';

# *********   Functions  ***************************************************************************************
def make_connection():
	try:
	   db = MySQLdb.connect("52.10.233.116","advising_user", "VLrMMJSScH6ZLHca",  "advising_db")
	   varConnected = True;
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
	   varConnected = False;
	except: 
		print "Error disconnecting or login out from database."
		varConnected = False;

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
		varConnected = False
		status = "                                 logged-out";
		stdscr.addstr(curses.LINES-1, 0, bottom_line + status )
		setQMbottomMenu()
		stdscr.chgat(curses.LINES-1,68, 10, curses.A_BOLD | curses.color_pair(1))
	except:
		db.rollback()
		print"Error: Unable to insert data: "  + sql		

def get_param(prompt_string):
     stdscr.addstr(2, 2, prompt_string)
     stdscr.clrtoeol()
     stdscr.refresh()
     input = stdscr.getstr(10, 10, 60)
     return input

def setQMbottomMenu():# Change the R to green, the Q to red, the Connected to green
	stdscr.chgat(curses.LINES-1,7, 1, curses.A_BOLD | curses.color_pair(2))# the M
	stdscr.chgat(curses.LINES-1,24, 1, curses.A_BOLD | curses.color_pair(1))# the Q

# this currently uses 9 char salting and md5 hashing -although this is probably fairly sucure there are more secure methods out there.
# this might be an alternative https://pypi.python.org/pypi/scrypt/
def operation_secure(password):
	salt = "3Km7!xc-B"
	pswd = hashlib.md5( salt + password + salt ).hexdigest()
	return pswd

#RETURNS ALL APPTS for a specified faculty email
#->empty list if no references exist
def GetAllAppts(db, FacultyEmail):
    cursor = db.cursor()
    sql = "SELECT Id, FacultyName, FacultyEmail, StudentName, StudentEmail, Date, Status, CAST(StartTime AS CHAR) as StartTime, CAST(EndTime AS CHAR) as EndTime FROM Appointment WHERE FacultyEmail='%s' ORDER BY Date ASC" %(FacultyEmail)

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
        return

    return results	

# *********   Set up screens  ***************************************************************************************
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

# Begin Program 
stdscr.addstr(" Advising Schedule Interface", curses.A_REVERSE) # what becomes the top bar
stdscr.chgat(-1, curses.A_REVERSE) #then finishes the line off with blank space.

# Set up the base window
cli_window = curses.newwin(curses.LINES-2,curses.COLS, 1,0)

# Create a sub-window so as to clearly display the text with out overwriting the quote window borders.
cli_text_window = cli_window.subwin(curses.LINES-6, curses.COLS-4,3,2)

# get teh size of the text window for later use
dims = cli_text_window.getmaxyx()

# text to go in lower text box made by using both iner and outer window
cli_text_window.addstr("Welcome to the Curses based CLI!") # this is the start up screen
stdscr.addstr(curses.LINES-1, 0, bottom_line + status )
setQMbottomMenu()

if status:
  stdscr.chgat(curses.LINES-1,68, 10, curses.A_BOLD | curses.color_pair(1))
else:
  stdscr.chgat(curses.LINES-1,68, 10, curses.A_BOLD | curses.color_pair(2))

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
	if c == ord('m') or c == ord('M'):
		cli_text_window.refresh()
		cli_text_window.clear()
		cli_text_window.addstr(action_menue, curses.color_pair(2))
		stdscr.addstr(curses.LINES-1, 0, bottom_line)
		setQMbottomMenu()
		
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
		curses.noecho()# temp turn off echo
		adminPwsdEntered = get_param("Enter the admin password to continue:" )
		curses.echo()
		tempPwd = operation_secure(adminPwsdEntered)
		cli_text_window.refresh()
		cli_text_window.clear()

		if tempPwd == adminPswd:
			cli_text_window.refresh()
			cli_text_window.clear()
			while addr1 != addr2:
				addr1 = get_param("Enter your email address:" )
				cli_text_window.refresh()
				cli_text_window.clear()	
				addr2 =  get_param("Re-enter your email address: " )
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
	                        
	                        pswd1 = get_param("Enter your password:") 
	                        cli_text_window.clear()	
	                        cli_text_window.refresh()
	                        pswd2 = get_param("Re-enter your password:")
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
			try:
			   insertNewUsser(addr1, tempPwd)
			   cli_text_window.addstr("Your information was stored sucessfully.", curses.color_pair(3))
			except:
			   cli_text_window.addstr("An unknown error ocurred when attempting to store your user info!", curses.color_pair(1))

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
		email = get_param("Enter your email address.")
		cli_text_window.refresh()
		cli_text_window.clear()
		pswd = get_param("Enter your password.")
		cli_text_window.clear()
		cli_text_window.refresh()
		# pull the latest email and password entered.
		db = make_connection()
		cursor = db.cursor()
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
		  status =  "                                  logged-in";
		  cli_window.clear()
		  cli_text_window.clear()
		  cli_window.box()
		  cli_text_window.refresh()
		  stdscr.addstr(curses.LINES-1, 0, bottom_line + status )
		  setQMbottomMenu()
		  stdscr.chgat(curses.LINES-1,68, 10, curses.A_BOLD | curses.color_pair(2))
		  cli_text_window.addstr("You have been logged in.", curses.color_pair(3))
		else:
		  disconnect(db)
		  cli_window.clear()
		  cli_text_window.clear()
		  cli_window.box()
		  cli_text_window.refresh()
		  cli_text_window.addstr("Your email or password did not match -try again!.", curses.color_pair(3))
		# set echo and curser back to original
		curses.echo(0) 
		curses.curs_set(0)

	if c == ord('3'):#logout
		cli_text_window.refresh()
		cli_text_window.clear()
		disconnect(db)
		status =  "                                 logged-out";
		stdscr.addstr(curses.LINES-1, 0, bottom_line + status )
		stdscr.chgat(curses.LINES-1,68, 10, curses.A_BOLD | curses.color_pair(1))
		setQMbottomMenu()
		cli_text_window.addstr("You have been logged out.", curses.color_pair(3))

	if c == ord('4'):
		cli_text_window.refresh()
		cli_text_window.clear()	
		if LoggedIn is False:
			cli_text_window.addstr("You must log in first!", curses.color_pair(1))
		else:
                        #get appointments
			appts = GetAllAppts(db, email)
			num = len(appts)

                        #set parameters for pad window and instantiate new pad
			cli_text_window_pos = 1
			height,width = cli_text_window.getmaxyx()
			cli_text_window_height = height + 10
                        pad = curses.newpad(cli_text_window_height, width)
                        pad_pos=0
                        pad.keypad(True)

                        #format appointment output
                        pad.addstr('No.  Date \tBegin   End  Student\t\t Email\t\t Status\t\t\n')
                        refNo = 1
			for index in range(num):
                                appts_str = str(refNo)
                        	appts_str += '    '+str(appts[index].get("Date"))
                                appts_str +='  '+str(appts[index].get("StartTime"))
                                appts_str +='  '+str(appts[index].get("EndTime"))
                                appts_str +='  '+str(appts[index].get("StudentName"))
                                appts_str +='\t'+str(appts[index].get("StudentEmail"))
                                appts_str +='\t'+str(appts[index].get("Status"))
				pad.addstr(appts_str + '\n\n', curses.color_pair(3))
                                refNo+=1
			running = True
		while running:
                        #get window size to readjust as needed
			height,width = cli_text_window.getmaxyx()
			cli_text_window_height = height + 10
                        pad.refresh(pad_pos,0,5,5,cli_text_window_height-10, width-5)
			ch = pad.getch()
			if ch == curses.KEY_DOWN and cli_text_window_pos < cli_text_window_height - height:
				pad_pos += 1
                                pad.refresh(pad_pos,0,5,5,cli_text_window_height-15, width-5)
			elif ch == curses.KEY_UP and cli_text_window_pos > 0:
				pad_pos -= 1
                                pad.refresh(pad_pos,0,5,5,cli_text_window_height-15, width-5)
			elif ch < 256 and chr(ch) == 'q':
				running = False
		        
                        
				
	if c == ord('m') or c == ord('M'):
		cli_text_window.refresh()
		cli_text_window.clear()
		make_connection()
		cli_text_window.addstr(action_menue, curses.color_pair(2) )
	
	if c == ord('E'):
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
#stdscr.keypad(0)
curses.echo()
curses.curs_set(1)

# Restore the terminal intself to its "former glory"
curses.endwin()


