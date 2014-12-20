#!/usr/bin/env python

"""
Sends automatically the emails to the users.
"""
from __future__ import print_function

import os, sys, time, csv, datetime, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from daemon import Daemon


class NotificationDaemon(Daemon):

    # class variables
    msg_week = 'This week is your turn to give a seminar talk!'
    title_week = 'Your seminar talk'
    msg_reminder = """
        Could you send information about your talk around? The information should
        include: title of your talk, an abstract, and a list of references.
    """ 
    title_reminder = 'Your seminar talk - a reminder'
    token_path='/tmp/sent_token'


    @staticmethod
    def csv2list(name='seminar_list_short.csv'):
        # each entry of the list has form:
        #   [date,username,userlogin]
        row_list=[]
        with open(name,'rb') as csvfile:
            reader=csv.reader(csvfile, delimiter='	')
            # skip the header
            next(reader,None)
            for row in reader:
                seminar=datetime.datetime.strptime(row[0],'%d.%m.%Y')
                row_list.append([seminar,row[1],row[2]])
            return row_list
        return None


    @staticmethod
    def send_message(name,userlogin,title,content):
        recipient=userlogin
        sender="mmalinow@mpi-inf.mpg.de"
        cc=sender

        msg=MIMEMultipart('alternative')
        msg['Subject']=title
        msg['From']=sender
        msg['To']=recipient
        msg['CC']=cc
        full_content="Hi %s,\n%s\n\nBest,\nM.M.\n\nMessage is automatically sent. If you spot errors please let me know." % \
                (name, content)
        msg.attach(MIMEText(full_content,'plain'))
        s=smtplib.SMTP('localhost')
        to_addr=[recipient] + [cc]
        s.sendmail(sender,to_addr,msg.as_string())
        s.quit()
        time.sleep(10)  # sleep to ensure the token is created


    @staticmethod
    def not_sent():
        if os.path.isfile(NotificationDaemon.token_path):
            return False
        else:
            return True


    @staticmethod
    def send_token(msg=''):
        # Informs that the message is sent
        with open(NotificationDaemon.token_path,'w') as f:
            f.write('sent: ' + msg + '\n')


    @staticmethod
    def remove_token():
        if os.path.isfile(NotificationDaemon.token_path):
            os.remove(NotificationDaemon.token_path)


    @staticmethod
    def find_entry(slist,today,day_diff):
        # find whose turn it is
        # return format:
        #   datetime, name, login
        for el in slist:
            d=el[0]
            if d.month == today.month and d.year == today.year:
                if d.day - today.day == day_diff:
                    return el
        return None


    def run(self):
        slist=NotificationDaemon.csv2list('seminar_list.csv')
        while True:
            # check what is day today
            today=datetime.datetime.today()
            weekday=today.weekday()
           
            if weekday == 0:
                # Monday
                if NotificationDaemon.not_sent():
                    entry=NotificationDaemon.find_entry(slist,today,4)
                    if entry:
                        NotificationDaemon.send_message(
                                entry[1], entry[2],
                                NotificationDaemon.title_week, 
                                NotificationDaemon.msg_week)
                        NotificationDaemon.send_token(entry[2])
            elif weekday == 3:
                # Thursday
                if NotificationDaemon.not_sent():
                    entry=NotificationDaemon.find_entry(slist,today,1)
                    if entry:
                        NotificationDaemon.send_message(
                                entry[1], entry[2],
                                NotificationDaemon.title_reminder, 
                                NotificationDaemon.msg_reminder)
                        NotificationDaemon.send_token(entry[2])
            elif weekday == 1 or weekday == 4:
                # remove the token
                NotificationDaemon.remove_token()
            time.sleep(60*60)


if __name__ == '__main__':
    daemon=NotificationDaemon('/tmp/notification-daemon.pid',stderr='/tmp/err')

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print("Unknown command", file=sys.stderr)
            sys.exit(2)

        sys.exit(0)
    else:
        print("Usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)

