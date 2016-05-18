cs419_project
Simplified Advising Scheduling Application
 
EXECUTIVE SUMMARY
Currently, OSU EECS students schedule advising appointments via an online web form. This generates an email that
is sent to the advisor. The system generated email is in plain text format and requires the advisor to manually input
an appointment to their Outlook Calendar. This application automates the calendar insertion process, and provides
the instructor with a Command Line Interface to manage their advising appointments through a python based Command Line
Interface (CLI) coded with the curses library to produce a GUi.

Addtitionally a python script serves as a procmail filter to capture system generated OSU EECS student emails and
convert them to an email with a MIME type attachment that’ll allow the advisor to easily add the advising
appointment to their Outlook calendar. The script adds the appointment to a relational SQL database maintained
internally through Amazon Web Services. The database duplicates the status of the advisor’s appointments, and
works in conjunction with the CLI to provide a central location for appointment management. The advisor is able to
use the CLI to view all current and pending appointments, as well as to cancel any appointment. The client provided 
clarification on how the application was to operate within the existing structure, as well as the expected functionality
of the application.
