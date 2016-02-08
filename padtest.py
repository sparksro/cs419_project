#!/usr/bin/env python2

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

bottom_line = "Press 'M' to see Menu. 'Q' to quit."

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

def setQMbottomMenu():# Change the R to green, the Q to red, the Connected to green
	stdscr.chgat(curses.LINES-1,7, 1, curses.A_BOLD | curses.color_pair(2))# the M
	stdscr.chgat(curses.LINES-1,24, 1, curses.A_BOLD | curses.color_pair(1))# the Q

def GetAllAppts(db, FacultyEmail):
    cursor = db.cursor()
    sql = "SELECT * FROM Appointment WHERE FacultyEmail='%s' ORDER BY Date ASC" %(FacultyEmail)
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
              #results.append({"Id": str(r[0]), "FacultyName": r[1], "FacultyEmail": r[2], "StudentName":r[3],
                  #"StudentEmail":r[4], "Date": r[5].strftime('%m/%d/%y'), "Status": r[6], "StartTime": STime, "EndTime": ETime}) 
              results.append('Date: '+ str(r[5]) + '  Start time: ' + STime + '  End Time: '+ ETime + '  S Name: ' + str(r[3]) + ' S. Email: ' + str(r[4]) + '  Status: '+ str(r[6] ) )
    except:
        print"Error: Unable to fetch data: "  + sql
        return
    return results

def get_apt_param(prompt_string, print_loc):
     cli_text_window.addstr(print_loc, 4, prompt_string)
     curses.echo()
     curses.cbreak()  #set into char break mode
     curses.curs_set(1)
     cli_text_window.clrtoeol()
     cli_text_window.refresh()
     input = cli_text_window.getstr(10, 10, 60)
     return input

# Create curses screen
stdscr = curses.initscr()
stdscr.addstr(" Advising Schedule Interface", curses.A_REVERSE) # what becomes the top bar
stdscr.chgat(-1, curses.A_REVERSE) #then finishes the line off with blank space.

cli_window = curses.newwin(curses.LINES-2,curses.COLS, 1,0)#base window
cli_text_window = cli_window.subwin(curses.LINES-5, curses.COLS-6,1,1)#the text window
#cli_text_window = cli_window.subwin(curses.LINES-6, curses.COLS-4,3,2)#the text window

cli_text_window.keypad(True)
cli_text_window.refresh()
curses.noecho()
curses.curs_set(0)
cli_window.box()
stdscr.noutrefresh()
cli_window.noutrefresh()

# Get screen width/height
height,width = cli_text_window.getmaxyx()

# Create a curses pad (pad size is height + 10)
mypad_height = height +17
mypad = curses.newpad(height, width);
mypad.scrollok(True)
mypad_pos = 1
mypad_refresh = lambda: mypad.refresh(mypad_pos, -2, 2, 3, mypad_height, width)
mypad_refresh()
db = make_connection()
FacultyEmail = 'rob@test.com'
appts = GetAllAppts(db, FacultyEmail)
num = len(appts)
#mypad.addstr(str(num)+"- appointments\n")
# Fill the window with text (note that 5 lines are lost forever)
i = 1;
for index in range(0, num):#adjust the - so it keeps the 0 line when scrolling
    #if index == num:break #keeps it from over indexing
    appts_str = str(appts[index])
    i_str  = str(i)
    mypad.addstr(i_str + ": "+ appts_str +'\n\n')
    i += 1;
    mypad_refresh()

# ****** User input to allow manipulation **********************************8
#print_loc = index * 3 + 6 
#appt_num = get_apt_param("Enter the number of the appointment you would like to change:",print_loc) 

# Wait for user to scroll or quit
running = True
while running:
    ch = cli_text_window.getch()
    if ch == curses.KEY_DOWN and mypad_pos < mypad_height - height:
        mypad_pos += 1
        mypad_refresh()
    elif ch == curses.KEY_UP and mypad_pos > 0:
        mypad_pos -= 1
        mypad_refresh()
    elif ch < 256 and chr(ch) == 'q':
        running = False


# End curses
curses.endwin()

# Write the old contents of pad to console
print '\n'.join(mypad_contents)
