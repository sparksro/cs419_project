#!/usr/bin/python

# Advising Schedule Interface 
# version 1.00

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

# *********   Functions  ***************************************************************************************
def make_connection():
	try:
  	   #db = mysql.connector.connect(user='advising_user', password='VLrMMJSScH6ZLHca', host='52.10.233.116', database='advising_db')
	   db = MySQLdb.connect("52.10.233.116","advising_user", "VLrMMJSScH6ZLHca",  "advising_db")
	   varConnected = True;
	except mysql.connector.Error as err:
  	   if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    	      print("Something is wrong with your user name or password %d" % (err.errno))
  	   elif err.errno == errorcode.ER_BAD_DB_ERROR:
    	      print("Database does not exist")
  	   else:
    	      print(err)
	else:
  	   db.close()
	return db

def disconnect():
	try:
  	   #db = mysql.connector.connect(user='advising_user', password='VLrMMJSScH6ZLHca', host='52.10.233.116', database='advising_db')
	   db.close()
	   varConnected = False;
	except: "Error disconnecting from database."

def get_param(prompt_string):
     stdscr.addstr(2, 2, prompt_string)
     stdscr.refresh()
     input = stdscr.getstr(10, 10, 60)
     return input

# this currently uses 9 char salting and md5 hashing -although this is probably fairly sucure there are more secure methods out there.
# this might be an alternative https://pypi.python.org/pypi/scrypt/
def operation_secure(password):
	salt = "3Km7!xc-B"
	pswd = hashlib.md5( salt + password + salt ).hexdigest()
	return pswd

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
curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)

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
stdscr.chgat(curses.LINES-1,7, 1, curses.A_BOLD | curses.color_pair(2))
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
		db = make_connection()
		cli_text_window.addstr(action_menue, curses.color_pair(2))
		#cli_text_window.chgat(curses.LINES-2,1, 1, curses.A_BOLD | curses.color_pair(2))
		#message = "                               logged out";
		stdscr.addstr(curses.LINES-1, 0, bottom_line)
		# Change the R to green, the Q to red, the Connected to green
		stdscr.chgat(curses.LINES-1,7, 1, curses.A_BOLD | curses.color_pair(2))
		stdscr.chgat(curses.LINES-1,24, 1, curses.A_BOLD | curses.color_pair(1))
		#stdscr.chgat(curses.LINES-1,69, 9, curses.A_BOLD | curses.color_pair(2))
		
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

		while addr1 != addr2:
			addr1 = get_param("Enter your email address:    " )
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
			  cli_window.clear()
			  cli_text_window.clear()
			  cli_window.box()
			  cli_text_window.refresh()
			  pswd1 = get_param("  Enter your password. - passwords must match!")# bug -- this get_param must be the same size or larger string than the last or it seems to have some left over text stuck in a buffer.  ???  
			  cli_text_window.clear()	
		 	  cli_text_window.refresh()
			  pswd2 = get_param("Re-enter your password: - passwords must match!")
			  cli_text_window.refresh()
			  cli_text_window.clear()
	 
			  if pswd1 != pswd2:  # bug -- it reffuses to enter this and print the warning.  Its just like the one above!  ????
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

		# makd the db connection
		db = MySQLdb.connect("52.10.233.116","advising_user", "VLrMMJSScH6ZLHca",  "advising_db")
		cursor = db.cursor()# prepare a cursor object using cursor() method

		# Prepare SQL query to INSERT a record into the database.
		sql = "INSERT INTO User(Email, \
		       password) \
		       VALUES ('%s', '%s')" % \
		       (addr1, tempPwd)
		try:
		   # Execute the SQL command
		   cursor.execute(sql)
		   # Commit your changes in the database-
		   db.commit()
		   db.close()
		   varConnected = False;
		   status =  "                                 logged-out";
		   stdscr.addstr(curses.LINES-1, 0, bottom_line + status )
		   stdscr.chgat(curses.LINES-1,7, 1, curses.A_BOLD | curses.color_pair(2))
		   stdscr.chgat(curses.LINES-1,24, 1, curses.A_BOLD | curses.color_pair(1))
		   stdscr.chgat(curses.LINES-1,68, 10, curses.A_BOLD | curses.color_pair(1))
		   cli_text_window.addstr("Your information was stored sucessfully.", curses.color_pair(3))
		except:
		   # Rollback in case there is any error
		   db.rollback()
		

	if c == ord('2'):
		cli_text_window.refresh()
		cli_text_window.clear()	
		#cli_text_window.addstr("numbro dose", curses.color_pair(1))
		curses.echo(1) 
		curses.curs_set(1)
		cli_text_window.refresh()

		cli_text_window.clear()
		email = get_param("Enter your email address.")
		cli_text_window.refresh()
		cli_text_window.clear()
		pswd = get_param("     Enter your password.")
		cli_text_window.clear()
		cli_text_window.refresh()
		# pull the latest email and password entered.
		db = MySQLdb.connect("52.10.233.116","advising_user", "VLrMMJSScH6ZLHca",  "advising_db")
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
		  stdscr.chgat(curses.LINES-1,68, 10, curses.A_BOLD | curses.color_pair(2))
		  cli_text_window.addstr("You have been logged in.", curses.color_pair(3))
		else:
		  cli_window.clear()
		  cli_text_window.clear()
		  cli_window.box()
		  cli_text_window.refresh()
		  cli_text_window.addstr("Your email or password did not match -try again!.", curses.color_pair(3))
		# set echo and curser back to original
		curses.echo(0) 
		curses.curs_set(0)

	if c == ord('3'):
		cli_text_window.refresh()
		cli_text_window.clear()
		db.close()	
		varConnected = False;
		status =  "                                 logged-out";
		stdscr.addstr(curses.LINES-1, 0, bottom_line + status )
		stdscr.chgat(curses.LINES-1,68, 10, curses.A_BOLD | curses.color_pair(1))
		cli_text_window.addstr("You have been logged out.", curses.color_pair(3))

	if c == ord('4'):
		cli_text_window.refresh()
		cli_text_window.clear()	
		cli_text_window.addstr("numbro quatro", curses.color_pair(1))

	if c == ord('m') or c == ord('M'):
		cli_text_window.refresh()
		cli_text_window.clear()
		make_connection()
		cli_text_window.addstr(action_menue, curses.color_pair(2))
	
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


