from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.mime.text import MIMEText
import smtplib


class Notification():
    
    def __init__(self):
        # self.email_account = "konticrea@gmail.com"
        # self.email_password = "57UkqE5*$QL8"
        self.email_account = 'minisite.kontiki.dev@gmail.com'
        self.email_password = 'hgfgrnowgwtepgpj'
    
    
    
    def send_notification_paused_campagn(self, emails, database, sid, domain, errorcode):
        try:
            if emails is not None and len(emails) > 0:
                subject = f'CAMPAGN STOP AT {database} - Id {sid}'
                body = f"""Hello all,

We regret to inform you that the campaign on database {database} has been stopped due to blocking error codes encountered during a cron execution.

This was generated on the campagn at Id {sid} with {domain}.

The error code is {errorcode}

This campagn was beeing "Paused" due to this issue.You can reactivate it if needed.

Thank you for your understanding and cooperation.

Best regards,
                
                """
                msg = MIMEMultipart()
                msg['From'] = formataddr(('KONTICREA', self.email_account))
                msg['To'] = ','.join(emails)
                msg['Subject'] = subject
                body_container = MIMEMultipart('alternative')
                body_container.attach(MIMEText(	body.encode('utf-8'), 'plain', 'UTF-8'))
                msg.attach(body_container)
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.ehlo()
                server.login(self.email_account,self.email_password)
                # with open(self.path+'/log_minisite/log_unsub.txt','a') as fic:
                #     fic.write(str(self.data['receive_date'])+ ' => ' + self.basename + ' => ' + str(self.data) + '\n')
                server.sendmail(self.email_account,','.join(emails), msg.as_string())
                server.close()
            else:
                pass
        except Exception as e:
            print('error sending notification for paused campagn ',e)
            pass
        





