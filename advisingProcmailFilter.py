import sys
import email
import MySQLdb
from cStringIO import StringIO
from email.generator import Generator
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from datetime import datetime, timedelta
import re
from random import randint
import smtplib
from email import Encoders
import base64

#opens a connection with advising database - returns connection object
#if connection error - returns 1
def make_connection():
    try:
        db = MySQLdb.connect("52.10.233.116","advising_user", "VLrMMJSScH6ZLHca",  "advising_db")
        varConnected = True;
    except MySQLdb.Error as e:
        return 1
    return db

#disconnects connection to database - pass in connection object
def disconnect(db):
    try:
        db.close()
        varConnected = False;
    except: "Error disconnecting from database."

#INSERT NEW APPT
def InsertNewAppt(db, FacultyName, FacultyEmail, StudentName, StudentEmail, Date, Status, StartTime, EndTime, Uid):
    cursor = db.cursor()
    sql = "INSERT INTO Appointment (\
           FacultyName, FacultyEmail, StudentName, StudentEmail, Date, Status, StartTime, EndTime, UID)\
           VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s')" %\
           (FacultyName, FacultyEmail, StudentName, StudentEmail, Date, Status, StartTime, EndTime, Uid)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()

#DELETE APPT
def DeleteAppt(db, ApptID):
    cursor = db.cursor()
    sql = "DELETE FROM Appointment WHERE UID = '%s'" %(ApptID)

    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
#UPDATE APPT STATUS
def UpdateAppt(db, Status, ApptID):
    cursor = db.cursor()
    sql = "UPDATE Appointment SET Status = '%s' WHERE UID = '%s'" %(Status, ApptID)

    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()

db= make_connection()
if db == 1:
    sys.exit(1)

# read email from std in 
full_email = sys.stdin.readlines()

# create email object and parse it adapted from http://stackoverflow.com/questions/14676375/pipe-email-from-procmail-to-python-script-that-parses-body-and-saves-as-text-fil
email_obj = email.message_from_string("".join(full_email))

# handle if the email is multipart 
for body in email_obj.walk():
	if body.get_content_type() == 'text/plain': 
		email_body = body.get_payload()
email_to = email_obj['to']
email_from = email_obj['from']
email_subject = email_obj['subject']
email_obj.add_header('reply-to', email_to)

# check email subject to see if we should continue 
if((not email_subject.startswith("Advising Signup") and not email_subject.startswith("Accepted: Advising Signup with") and not email_subject.startswith("Declined: Advising Signup with")) or "Pending" in email_subject ): 
	sys.exit(1)


# check if email is from the user's email address if so check if it is accepted or declined
# if this is the case then this is the email with the attachment added
# this means we need to get the uid out of the encoded response 
if "procmailtestscs@gmail.com" not in email_from and "do.not.reply@engr.orst.edu" not in email_from: 
	if email_subject.startswith("Accepted") or email_subject.startswith("Declined"):
		# get the email into a string adapted from http://stackoverflow.com/questions/389398/trouble-with-encoding-in-emails
		out_obj = StringIO()
		gen = Generator(out_obj)
		gen.flatten(email_obj)
		# get the email string
		email_string = out_obj.getvalue()
		# find the base 64 encoded ics file 
		reg_exp = re.compile('base64\s*([^\-]*)')
		match = reg_exp.search(email_string)
		if match:
			# decode the vevent to get it in readable format 
			base64_encoded_vevent = match.group(1)
			decoded_vevent = base64.b64decode(base64_encoded_vevent)
			# get the uid from decoded portion 
			reg_exp = re.compile('UID:([^\s]+)')
			match = reg_exp.search(decoded_vevent)
			if match:
				uid = match.group(1)
			else:
				sys.exit(12)
		else:
			sys.exit(11)
		# either delete or update our appointment 
		if email_subject.startswith("Accepted"):
			UpdateAppt(db, "Accepted", uid)
		else:
			DeleteAppt(db, uid)
		# exit without printing anything so that this email ends up being deleted before getting to the user 
		sys.exit(0)
	else:
		sys.exit(13)
		
# regex portion to get necessary fields from email body 
reg_exp = re.compile('Name: ([A-Za-z]+ *[A-Za-z]*)')
match = reg_exp.search(email_body)
if match:
    name = match.group(1)
else:
    sys.exit(1)

reg_exp = re.compile('Email: ([A-Za-z@\.]+)')
match = reg_exp.search(email_body)
if match:
    student_email = match.group(1)
else:
    sys.exit(2)

reg_exp = re.compile('Date: [A-Za-z]+, ([A-Za-z0-9,]+) ([0-9]+)[rst][dth], ([0-9]+)')
match = reg_exp.search(email_body)
if match:
    appt_month = match.group(1)
    appt_day = match.group(2)
    appt_year = match.group(3)
else:
    sys.exit(3)

reg_exp = re.compile('Time: ([0-9:apmAPM]+) - ([0-9:apmAPM]+)')
match = reg_exp.search(email_body)
if match:
    appt_time_beg = match.group(1)
    appt_time_end = match.group(2)
else:
    sys.exit(4)

# remove student email from the to section so they don't get the calendar request
new_email_to = re.sub(student_email, '', email_to)

# get instructor email address from the email to section 
reg_exp = re.compile('([A-Za-z0-9.]+@[A-Za-z0-9.]+)')
match = reg_exp.search(new_email_to)
if match:
    new_email_to = match.group(1)
else:
	sys.exit(5)

# get instructor's name 
reg_exp = re.compile('Advising Signup with (.*) c', re.I)
match = reg_exp.search(email_body)
if match: 
	instructor_name = match.group(1)
else: 
	sys.exit(6)

# convert date times into ics format
appt_date = appt_month + " " + appt_day + " " + appt_year
appt_date = datetime.strptime(appt_date,'%B %d %Y')
appt_time_beg = datetime.strptime(appt_time_beg,'%I:%M%p')
ics_created_on_dt = datetime.now()  + timedelta(hours=7)
ics_created_on = ics_created_on_dt.strftime('%Y%m%dT%H%M%SZ')
appt_time_end = datetime.strptime(appt_time_end,'%I:%M%p')
appt_date_str = datetime.strftime(appt_date,'%Y-%m-%d')
appt_date = datetime.strftime(appt_date,'%Y%m%d')
appt_time_beg_str = datetime.strftime(appt_time_beg, '%H:%M:%S')
appt_time_beg += timedelta(hours=7)
appt_time_beg = datetime.strftime(appt_time_beg, '%H%M%S')
appt_time_end_str = datetime.strftime(appt_time_end, '%H:%M:%S')
appt_time_end += timedelta(hours=7)
appt_time_end = datetime.strftime(appt_time_end, '%H%M%S')
appt_start_date = appt_date + "T" + appt_time_beg + "Z"
appt_end_date = appt_date + "T" + appt_time_end + "Z"

# handle different email cases
if email_subject.startswith("Advising Signup with"):
    # create unique id
    uid = appt_start_date + student_email
    # change if you want email reply to go somewhere different
    reply_to = new_email_to
    #ics message attachment portion adapted from http://stackoverflow.com/questions/4823574/sending-meeting-invitations-with-python
    #this ics message handles sign ups
    ics_message = "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:Advising-t\r\nMETHOD:REQUEST\r\nBEGIN:VEVENT\r\nUID:" + uid + "\r\nDTSTAMP:" + ics_created_on + "\r\nDTSTART:" + appt_start_date + "\r\nDTEND:"+ appt_end_date + "\r\nSUMMARY:" + email_subject + "\r\nORGANIZER;CN=" + reply_to + ":MAILTO:" + reply_to + "\r\nATTENDEE;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE;CN" + new_email_to + ";X-NUM-GUESTS=0:MAILTO:" + new_email_to + "DESCRIPTION:" + email_body + "\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n"
    ics_sect = MIMEText(ics_message,'calendar;method=REQUEST')
    InsertNewAppt(db, instructor_name, new_email_to, name, student_email, appt_date_str, "Pending", appt_time_beg_str, appt_time_end_str, uid)
elif email_subject.startswith("Advising Signup Cancellation"):
    uid = appt_start_date + student_email
    reply_to = new_email_to
    #ics message attachment portion adapted from http://stackoverflow.com/questions/4823574/sending-meeting-invitations-with-python
    ics_message = "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:Advising-t\r\nMETHOD:CANCEL\r\nBEGIN:VEVENT\r\nUID:" + uid + "\r\nDTSTAMP:" + ics_created_on + "\r\nDTSTART:" + appt_start_date + "\r\nDTEND:"+ appt_end_date + "\r\nSUMMARY:" + email_subject + "\r\nORGANIZER;CN=" + reply_to + ":mailto:" + reply_to + "\r\nDESCRIPTION:" + email_body + "\r\nATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE;CN" + new_email_to + ";X-NUM-GUESTS=1:MAILTO:" + new_email_to + "\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n"
    ics_sect = MIMEText(ics_message,'calendar;method=CANCEL')
    # if not from procmailtests (the cli) then delete it from the database
    if "procmailtestscs" not in email_from: 
    	DeleteAppt(db, uid)


# the header and attachment portion of code adapted from http://stackoverflow.com/questions/4823574/sending-meeting-invitations-with-python
new_email_obj = MIMEMultipart("mixed")
new_email_obj["reply-to"] = reply_to
new_email_obj["date"] = email_obj["date"]
new_email_obj["to"] = new_email_to
new_email_obj["from"] = reply_to
new_email_obj["subject"] = email_subject

email_sect = MIMEText(email_body,"plain")

new_email_alternative = MIMEMultipart('alternative')

new_email_alternative.attach(email_sect)
new_email_alternative.attach(ics_sect)

new_email_obj.attach(new_email_alternative)

# print the final email adapted from http://stackoverflow.com/questions/389398/trouble-with-encoding-in-emails
out_obj = StringIO()
gen = Generator(out_obj)
gen.flatten(new_email_obj)
print(out_obj.getvalue())
sys.stdout.flush()