# This file contains the script that verifies if the informations were inserted by the collaborators

from datetime import date
from auvo.auvo import AuvoApi
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pandas import DataFrame
import smtplib
import auvo.constants as const

def emailAlert(today):
    """
    Will send an email if there are negative values 

    :Args
        df: Dataframe -> data from the website 
    
    :Usage
        emailReport(df)
    
    """

    # Variables
    sender = "ti.reflexapersianas@gmail.com"
    password = const.E_PASS
    msg = MIMEMultipart('related')
    text_html = ""

    msg['Subject'] = "Dados não encontrados"
    msg['From'] = sender
    msg['To'] = const.TO_EMAIL

    # HMTL code of the email
    with open(str(const.BASE_DIR) + r"\auvo\email_alert.html") as f:
        html = f.readlines()
    
    # Organizing the text
    for i in range(len(html)):
        text_html += html[i].replace("\n", '')
    

    # Adding the reports to the html
    text_html = text_html.replace("{% text %}", f"Os dados referentes à quilometragem do dia {today} da equipe 'Técnicos de SP' não foram encontrados pelo programa. Verifique se as informações estão presentes na plataforma da Auvo.")


    msgAlternative = MIMEMultipart('alternative')
    msg.attach(msgAlternative)

    msgText = MIMEText('Alternative plain text message.')
    msgAlternative.attach(msgText)

    msgText = MIMEText(text_html, 'html')
    msgAlternative.attach(msgText)

    # Adding the images of the html's body
    for i in range(1, 6):
        #Attach Image 
        fp = open(f'{const.BASE_DIR}\images\image-{i}.png', 'rb') #Read image 
        msgImage = MIMEImage(fp.read())
        fp.close()
        # Define the image's ID as referenced above
        msgImage.add_header('Content-ID', f'<image-{i}>')
        msg.attach(msgImage)

    # Send email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, const.TO_EMAIL, msg.as_string())
    


inst = AuvoApi()

today = date.today()
today = str(today.strftime("%d/%m/%y"))

data = inst.getTaskInfo( today, "Thiago Costa")
data2 = inst.getTaskInfo(today, "Rafael Rodrigues da Cunha")

if (data == [] and data2 == []):
    emailAlert(today)