# This file will include functions that will be responsible to organize 
# the data of the website converting it to xlsx, pdf...
from email import header
from h11 import Data
from pandas import DataFrame
import pandas as pd
import auvo.constants as const
from email.message import EmailMessage
import requests
import json
import smtplib


def xlsxReport(df:DataFrame):
    """
    Given a dataframe, will convert it to a xlsx file 
    
    :Args
        df: Dataframe -> data from the website 
    
    :Usage
        xlsxReport(df)
    """
    
    # Variables
    name = df['Nome'].iloc[0].lower()
    name = name[:30] if len(name) >= 31 else name
    df = df.drop(columns=['Nome', 'index'])
    writer = pd.ExcelWriter(f"reports/{name}.xlsx", engine='xlsxwriter')
    workbook  = writer.book
    

    # Saving the dataframe
    df.to_excel(writer, sheet_name=name, startrow=1, header=False, index=False)

    # Creating the worksheet
    worksheet = writer.sheets[name]

    # Creating formats
    bg_white = workbook.add_format({'bg_color': '#EEEEEE','font_name': 'Montserrat'}) 
    bg_gray  = workbook.add_format({'bg_color': '#FFFFFF','font_name': 'Montserrat'})

    bg_red   = workbook.add_format({'bg_color': 'red', 
                                    'font_color': 'white',
                                    'font_name': 'Montserrat'})

    bg_green = workbook.add_format({'bg_color': '#58BB43', 
                                    'font_color': 'white',
                                    'font_name': 'Montserrat'})

    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#51515D',
        'font_color': 'white',
        'font_name': 'Montserrat',
        'font_size': 10,
        'border': 1
    })


    # Getting the column's title
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
        column_len = df[value].astype(str).str.len().max()
        column_len = max(column_len, len(value)) + 3
        worksheet.set_column(col_num, col_num, column_len)

    # Adding conditional formats
    worksheet.conditional_format('F1:F'+str(len(df)+1), {'type':     'cell',
                                        'criteria': '<=',
                                        'value':    -2,
                                        'format':   bg_red})

    worksheet.conditional_format('F2:F'+str(len(df)+1), {
                                        'type':     'cell',
                                        'criteria': '>',
                                        'value':    -2,
                                        'format':   bg_green})

     
    # Declaring that the odds rows will be gray
    for i in range(len(df)+1):  
        worksheet.set_row(i, 20, cell_format=(bg_white if i%2!=0 else bg_gray))

    writer.save()

def pdfReport(df:DataFrame):
    pass

def postNotion(df:DataFrame):
    """
    Will make the integration with the notion

    :Args
        df: Dataframe -> data from the website 
    
    """
    secret = const.SECRET
    pageId = const.DB_ID

    url = f'https://api.notion.com/v1/pages'

    headers = {
        'Authorization': f'Bearer {secret}',
        "Notion-Version": "2022-02-22",
        "Content-Type": "application/json"
    }

    for i in range(len(df)):
        name = df['Nome'][i]
        km_inicial = float(df['Km Inicial Carro'][i])
        km_final =   float(df['Km Final Carro'][i])
        km_sistema = float(df['Km Sistema'][i])
        km_total =   float(df['Km Total'][i])
        date =       df['Data'][i]
        comparativo =round(float(df['Comparativo'][i])*100)/100

        data = {
        "parent":{
            "database_id": pageId
        },
        "properties": {
          "Nome": {
            "title": [
              {
                "text": {
                  "content": name
                }   
              }
            ]
          },
          "Km Inicial Carro": {
            "number": km_inicial
               
          },
          "Km Final Carro": {
            "number": km_final
              
          },
          "Km Sistema": {
            "number": km_sistema
          },
          "Km Total": {
            "number": km_total
          },
          "Data": {
            "rich_text": [
              {
                "text": {
                  "content": date
                }   
              }
            ]
          },
          "Comparativo": {
            "number": comparativo
          },
        }}
    
        requests.post(url, json=json.loads(json.dumps(data)), headers=headers)

def emailReport(df:DataFrame):
    """
    Will send an email if there are negative values 

    :Args
        df: Dataframe -> data from the website 
    
    :Usage
        emailReport(df)
    
    """

    # Variables
    sender = const.EMAIL
    password = const.E_PASS
    msg = EmailMessage()
    css_style = ""
    divergence_records = ""

    msg['Subject'] = "Divergência de Valores"
    msg['From'] = sender
    msg['To'] = const.TO_EMAIL

    for i in range(len(df)):
        comp = df['Comparativo'][i]
        if comp < -2:
            divergence_records += f""" <tr><td>{df['Nome'][i]}</td><td>{df['Km Inicial Carro'][i]}</td><td>{df['Km Final Carro'][i]}</td><td>{df['Km Sistema'][i]}</td><td>{df['Km Total'][i]}</td><td>{df['Data'][i]}</td><td>{df['Comparativo'][i]}</td></tr> """

    # If there are negative records, send them to email
    if divergence_records != "":
        # Estilo css que será adicionado ao corpo do e-mail
        css_style = """
        body{
            background-color: #eff3f6;
            font-family: 'Arial';
            padding: 40px;
        }   
        #info-itens{
            border-collapse: collapse;
            margin-top: 50px;
            margin-bottom: 50px;
            margin-left: auto;
            margin-right: auto;
            font-size: 0.9em;
        }   
        #info-itens thead tr{
            background-color: #3c3c3c;
            color: #fff;
            text-align: left;
            font-weight: bold;
        }   
        #info-itens th,
        #info-itens td{
            padding: 12px 15px;
        }   
        #info-itens tbody tr{
            border-bottom: 1px solid #ddd;
        }   
        #info-itens tbody tr:nth-of-type(even){
            background-color: white;
        }
        """ 

        # HMTL code of the email
        msg.add_alternative(f"""
        <!DOCTYPE html>
        <html>
            <style>
                {css_style}
            </style>
            <body>
                    <div id=tabela>
                        <table id=info-itens>
                            <thead>
                                <tr>
                                    <th>Nome</th>
                                    <th>Km Inicial Carro</th>
                                    <th>Km Final Carro</th>
                                    <th>Km Sistema</th>
                                    <th>Km Total</th>
                                    <th>Data</th>
                                    <th>Comparativo</th>
                                </tr>
                            </thead>
                            <tbody>
                                {divergence_records}
                            </tbody>
                        </table>
                    </div>
            </body>
        </html>
        """, subtype='html')    
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)