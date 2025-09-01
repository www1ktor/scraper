import os, smtplib
from email.message import EmailMessage

addrs = []
with open('emails.txt') as emails:
    for mail in emails:
        addrs.append(mail.strip())
        
# Wczytanie zmian
with open('table.html', encoding='utf-8') as fp:
    body = fp.read()

with open('keys/sentgrid.txt', encoding='utf-8') as pswd:
    passwd = str(pswd.read())

# Parametry SMTP SendGrid
SMTP_HOST = 'smtp.sendgrid.net'
SMTP_PORT = 587
USERNAME  = 'apikey'                           # literal "apikey"
PASSWORD  = passwd     # Twój klucz

for a in addrs:
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = 'zmiana tydzień do tygodnia'
    msg['To']    = a    # możesz użyć dowolnego valid-from
    msg['From'] = 'karykowskiw@gmail.com'
    msg.add_alternative(body, subtype='html')

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(USERNAME, PASSWORD)
        smtp.send_message(msg)



