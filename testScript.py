import sys
import email
from cStringIO import StringIO
from email.generator import Generator
import email.MIMEText
import email.MIMEBase
from email.MIMEMultipart import MIMEMultipart
import datetime
import re

full_email = sys.stdin.readlines()

email_obj = email.message_from_string("".join(full_email))

email_to = email_obj['to']
email_from = email_obj['from']
email_subject = email_obj['subject']
email_body = email_obj.get_payload()
email_obj.add_header('reply-to', email_to)

reg_exp = re.compile('Name: ([A-Za-z]+)')
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

reg_exp = re.compile('Date: [A-Za-z]+, ([A-Za-z0-9,]+) ([0-9]+)th, ([0-9]+)')
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

# convert date times into ics format 
appt_date = appt_month + " " + appt_day + " " + appt_year
appt_date = datetime.datetime.strptime(appt_date,'%B %d %Y')
appt_time_beg = datetime.datetime.strptime(appt_time_beg,'%I:%M%p')
appt_time_end = datetime.datetime.strptime(appt_time_end,'%I:%M%p')
appt_date = datetime.datetime.strftime(appt_date,'%Y%m%d')
appt_time_beg = datetime.datetime.strftime(appt_time_beg, '%H%M%S')
appt_time_end = datetime.datetime.strftime(appt_time_end, '%H%M%S')
appt_start_date = appt_date + "T" + appt_time_beg + "Z"
appt_end_date = appt_date + "T" + appt_time_end + "Z"

# write to file for debugging
file1 = open("testFile", "w")
file1.write(appt_start_date)
file1.write("\n\n")
file1.write(appt_end_date)
file1.write("\n\n")
file1.write(email_from)
file1.write("\n\n")
file1.write(email_to)
file1.write("\n\n")
file1.write(email_body)
file1.write("\n\n")
file1.write(email_subject)
file1.write("\n\n")



# handle different email cases 
if email_subject.startswith("Advising Signup with"):
	file1.write("We are in the signup portion\n\n")
	file1.close()
elif email_subject.startswith("Advising Signup Cancellation"):
	file1.write("We are in the cancel portion\n\n")
	file1.close()
else:
	file1.write("We are in the else portion\n\n")
	file1.close()	

# print the final email 
out_obj = StringIO()
gen = Generator(out_obj)
gen.flatten(email_obj)
print(out_obj.getvalue())
sys.stdout.flush()

# writes out full email, useful for debugging
file2 = open("testFile2", "w")
file2.write(out_obj.getvalue())
file2.close()