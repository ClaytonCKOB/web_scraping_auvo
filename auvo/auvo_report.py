# This file will include functions that will be responsible to organize 
# the data of the website converting it to xlsx, pdf...
from pandas import DataFrame
import pandas as pd


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
    df = df.drop(columns=['Nome'])
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

def emailReport(df:DataFrame):
    pass