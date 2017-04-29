# encoding: utf-8
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))

def send_mail(receiver,text):
    sender = '1805662481@qq.com'
    subject = 'python email test'
    smtpserver = 'smtp.qq.com'
    username = '1805662481@qq.com'
    password = 'wydhxf#1124'

    msg = MIMEText(text, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = _format_addr(u'管理员 <%s>' % sender)
    msg['To'] = _format_addr(receiver)

    smtp = smtplib.SMTP(smtpserver,25)
    # smtp.connect(smtpserver)
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msg.as_string())
    smtp.quit()