#!/usr/bin/python
import smtplib
import csv
import yaml
import sys
import re

'''
file: intros.py
author:  Jake Porway

Sends a batch of "Nice to meet you!" emails to the list of people in a CSV
and optionally adds them to Highrise with the tags you specify.

Column headers in the CSV define the info that you're going to email and
optionally add to Highrise.  The fields this program accepts are (* = required):

*First:  First name
*Last:  Last name
*Email:  Email address
*Subject:  Subject of the email
*Body 1...Body N:  At least one tag starting with "Body".  Multiple body columns
                   will be combined in lexographic order.  
CC:  Email addresses to CC
Tags:  Highrise tags to add
Notes:  Highrise notes to add
Title: Person's Title
Company:  Person's company name

'''
def add_to_highrise(row):
    p = Person()
    p.first_name = row["First"]
    p.last_name = row["Last"]
    p.contact_data.email_addresses.append(EmailAddress(address=row["Email"]))
    if "Tags" in row:
        for t in row["Tags"].split(","):
            p.add_tag(t.strip())
    if "Notes" in row:
        p.add_note(row["Notes"])
    if "Title" in row:
        p.title = row["Title"]
    if "Company" in row:
        p.company_name = row["Company"]



'''
send_intros(config, dictreader)

Sends intros to every row in dictreader using the config in config.
CSV's should be in the format:

| First | Last | Email | CC | Subject | Highrise Tags (optional) | Body 1 | Body 2 | ... | Body N | 

All recipients in Email (can be comma-separated list of emails) will be emailed
and Highrise tags added.  Any fields starting with "Body" will be concatenated
in lexographic order.  This allows a fragile but flexible way to specify certain 
portions of the email to be repeated across recipients or groups of recipients.  

The first row in your CSV will be used as the column names.  You can use
variables from columns for replacement using {{ }} notation, e.g.:

| First  | Last  | Email             | Subject             |
------------------------------------------------------------
|  Jane  |  Doe  |  janedoe@aol.com  |  Hey {{First}}!     |

Will send an email to janedoe@aol.com with the subject "Hey Jane!"
'''
def send_intros(config, dictreader):
    if not 'sender' in config or not config['sender']:
        print "No sender specified in config file.  Exiting."
        sys.exit(2)

    sender = config['sender']
    smtp_server = config['smtp_server']
    smtp_port = config['smtp_port']

    session = smtplib.SMTP(smtp_server, smtp_port)
         
    session.ehlo()
    session.starttls()
    session.ehlo
    session.login(sender, config['password'])

    for row in dictreader:

        if not 'Subject' in row:
            print "No subject in this row.  Exiting."
            sys.exit(2)

        if not 'Email' in row and :
            print "No recipients in this row.  Please label some column in your csv 'Email' or 'CC'."
            sys.exit(2)


        body_keys = [k for k in row.keys() if k.lower()[:4] == "body"]
        body_keys.sort()

        if not body_keys:
            print "No body columns found.  Exiting."
            sys.exit(2)

        body_list = [row[b] for b in body_keys]
        join_string = "  "
        if "join_string" in config:
            join_string = config["join_string"]
        body = join_string.join(body_list)

        ''' Do replacements in the body and subject, if needed. '''
        body = re.sub("\{\{(.+?)\}\}", lambda f: row[f.group(1)], body)
        subject = re.sub("\{\{(.+?)\}\}", lambda f: z[f.group(1)], row["Subject"])

        ''' Listify the recipients '''
        cc = ""
        if "CC" in row:
            cc = row["CC"].split(",")
        recipients = [row["Email"]]
        recipients.extend(cc)
        headers = ["From: " + sender,
                   "Subject: " + subject,
                   "To: " + ", ".join(recipients),
                   "MIME-Version: 1.0",
                   "Content-Type: text/html"]
        headers = "\r\n".join(headers)
        #session.sendmail(sender, recipients, headers + "\r\n\r\n" + body)
        print "--- SENT ---"
        print headers + "\r\n\r\n" + body
        print "---"

        if 'highrise_api_key' in config and 'highrise_server' in config:
            add_to_highrise(row)    

    session.quit()
 

def main():
    if len(sys.argv) != 3:
        print "USAGE: python intros.py <config.yaml> <list_of_names_and_info.csv>"
        sys.exit(2)

    try:
        config = yaml.load(open(sys.argv[1], "rb"))
    except Exception as e:
        print "Couldn't load config file %s: %s" % (sys.argv[1], e)
        sys.exit(2)

    if not "password" in config:
        config["password"] = raw_input("Please enter Gmail password: ")
    if not "highrise_api_key" in config or not "highrise_server" in config:
        print "--- Either highrise_api_key or highrise_server not found in config.  Won't add contacts to Highrise."
    else:
        from pyrise import *
        Highrise.set_server(config["highrise_server"])
        Highrise.auth(config["highrise_api_key"]

    try:
        dictreader = csv.DictReader(open(sys.argv[2], "rb"))
    except Exception as e:
        print "Couldn't load data file %s: %s" % (sys.argv[2], e)
        sys.exit(2)
    send_intros(config, dictreader)
    

if __name__ == "__main__":
    main()
    sys.exit(0)
