from __future__ import with_statement
import ConfigParser
import smtplib,sys 
from email.mime.text import MIMEText

config=ConfigParser.ConfigParser()
with open('/usr/local/bin/newHA/HAconfig.cfg','rw') as cfgfile:
    config.readfp(cfgfile)
mailto_list=[config.get('info','MAIL_TO')]
mail_host=config.get('info','MAIL_HOST')
mail_user=config.get('info','MAIL_USER')
mail_pass=config.get('info','MAIL_PASS')
mail_postfix=config.get('info','MAIL_POSTFiX')
 
def send_mail(sub,content):
    me=mail_user+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content,_charset='gbk') 
    msg['Subject'] = sub 
    msg['From'] = me 
    msg['To'] = ";".join(mailto_list) 
    try: 
        s = smtplib.SMTP() 
        s.connect(mail_host) 
        s.login(mail_user,mail_pass) 
        s.sendmail(me, mailto_list, msg.as_string()) 
        s.close() 
        return True
    except Exception, e: 
        print str(e) 
        return False
if __name__ == '__main__': 
    if send_mail(u'Server dead',u'Server dead'):
        print 'yes'
    else:
        print 'no'
