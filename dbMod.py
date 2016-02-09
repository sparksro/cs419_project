#!/usr/bin/python

# Advising Schedule: database modifier
# version 1.00

import MySQLdb
#import mysql.connector
#from  mysql.connector import errorcode
import datetime
import time
import sys

#opens a connection with advising database - returns connection object
#if connection error - returns 1
def make_connection():
    try:
        db = MySQLdb.connect("52.10.233.116","advising_user", "VLrMMJSScH6ZLHca",  "advising_db")
        varConnected = True;
    except MySQLdb.Error as e:
        print(e)
        return 1
    return db

#disconnects connection to database - pass in connection object
def disconnect(db):
    try:
        db.close()
        varConnected = False;
    except: "Error disconnecting from database."
	
#RETURNS ALL APPTS for a specified faculty email
#->empty list if no references exist
def GetAllAppts(db, FacultyEmail):
    cursor = db.cursor()
    sql = "SELECT Id, FacultyName, FacultyEmail, StudentName, StudentEmail, Date, Status, CAST(StartTime AS CHAR) as StartTime, CAST(EndTime AS CHAR) as EndTime FROM Appointment WHERE FacultyEmail='%s' ORDER BY Date DESC" %(FacultyEmail)

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

              results.append({"Id": str(r[0]), "FacultyName": r[1], "FacultyEmail": r[2], "StudentName":r[3],
                  "StudentEmail":r[4], "Date": r[5].strftime('%m/%d/%y'), "Status": r[6], "StartTime": STime, "EndTime": ETime}) 
    except:
        print"Error: Unable to fetch data: "  + sql
        return

    return results


#INSERT NEW APPT
def InsertNewAppt(db, FacultyName, FacultyEmail, StudentName, StudentEmail, Date, Status, StartTime, EndTime):
    cursor = db.cursor()
    sql = "INSERT INTO Appointment (\
           FacultyName, FacultyEmail, StudentName, StudentEmail, Date, Status, StartTime, EndTime)\
           VALUES('%s','%s','%s','%s','%s','%s','%s','%s')" %\
           (FacultyName, FacultyEmail, StudentName, StudentEmail, Date, Status, StartTime, EndTime)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        print"Error: Unable to insert data: "  + sql

#DELETE APPT
def DeleteAppt(db, ApptID):
    cursor = db.cursor()
    sql = "DELETE FROM Appointment WHERE Id = '%s'" %(ApptID)

    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        print"Error: Unable to delete appointment: " +sql
    
#UPDATE APPT STATUS
def UpdateAppt(db, Status, ApptID):
    cursor = db.cursor()
    sql = "UPDATE Appointment SET Status = '%s' WHERE Id = '%s'" %(Status, ApptID)

    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        print"Error: Unable to update appointment: " +sql

#-------------------------------
#TESTING - remove in production
#--------------------------------

db = make_connection()
if db == 1:
    print "Error with connection.  Goodbye"
    sys.exit()

#Values to insert to DB
#Must convert all emails to upper to bypass case-sensitive requests
FacultyName = "Mr.T"
FacultyEmail= "rob@test.com"
StudentName = "JoeT"
StudentEmail = "JoeT@oregonstate.edu"
Date = "February 4, 2016"
Date = datetime.datetime.strptime(Date, "%B %d, %Y")
Status = "Pending"
StartTime = datetime.time(10, 30)
EndTime = datetime.time(11, 15)
#InsertNewAppt(db, FacultyName, FacultyEmail, StudentName, StudentEmail, Date, Status, StartTime, EndTime)

#set ID for appointment to modify
ApptID = 6 
Status = "Accepted"

#DeleteAppt(db,ApptID)
#UpdateAppt(db, Status, ApptID)

appts = GetAllAppts(db, FacultyEmail)
print appts

disconnect(db)

