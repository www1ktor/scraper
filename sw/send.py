import os, smtplib
from email.message import EmailMessage

addrs = ['sebastian.karykowski@dmm-logistics.com', 'w.karykowski@icloud.com']

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
    msg['Subject'] = 'Zmiany w ogłoszeniach [wczoraj dzisiaj] tera robie testy kminisz bryłe? wszystko się zaciąga i porównuje tak jak prawie powinno. musimy jeszcze tylko zrobić śledzenie ceny i wrzucić to na mikrusa'
    msg['To']    = a    # możesz użyć dowolnego valid-from
    msg['From'] = 'karykowskiw@gmail.com'
    msg.add_alternative(body, subtype='html')

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(USERNAME, PASSWORD)
        smtp.send_message(msg)



