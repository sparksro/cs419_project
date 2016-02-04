#!/usr/bin/python

# Advising Schedule: database modifier
# version 1.00

import MySQLdb
import mysql.connector
from  mysql.connector import errorcode
import datetime
import time

#opens a connection with advising database - returns connection object
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
    sql = "SELECT * FROM Appointment WHERE FacultyEmail='%s' ORDER BY Date DESC" %(FacultyEmail)

    try:
        cursor.execute(sql)
        #create empty list
        results=[]
        if cursor.rowcount != 0:
            catch = cursor.fetchall()
            for r in catch:
              #format time object
              STime = str(r[7])
              ':'.join(str(STime).split(':')[:1])
              ETime = str(r[8])
              ':'.join(str(ETime).split(':')[:1])
              results.append({"Id": r[0], "FacultyName": r[1], "FacultyEmail": r[2], \
                  "StudentName":r[3], "StudentEmail":r[4], "Date": r[5].strftime('%m/%d/%y'), "Status": r[6], "StartTime": STime, "EndTime": ETime}) 
    except:
        print"Error: Unable to fetch data: "  + sql

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


#TESTING
db = make_connection()
#TO DO: convert all emails to upper or lower
FacultyName = "Mr.T"
FacultyEmail= "MrT@oregonstate.edu"
StudentName = "JoeT"
StudentEmail = "JoeT@oregonstate.edu"
Date = datetime.datetime(2016, 2, 3)
print Date
Status = "Pending"
StartTime = datetime.time(10, 30)
EndTime = datetime.time(11, 15)
#InsertNewAppt(db, FacultyName, FacultyEmail, StudentName, StudentEmail, Date, Status, StartTime, EndTime)
ApptID = 7
#DeleteAppt(db,ApptID)
Status = "Accepted"
UpdateAppt(db, Status, ApptID)
appts = GetAllAppts(db, 'MrT@oregonstate.edu')
print appts



disconnect(db)

