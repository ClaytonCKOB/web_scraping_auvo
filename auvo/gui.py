# This file contains the graphic configurations
from auvo.auvo import Auvo
from auvo.auvo_report import *
import auvo.constants as const
import time
import datetime
from datetime import date
import tkinter as tk
from PIL import ImageTk, Image

class Tracking(tk.Tk):
    def __init__(self):
        self.auvo = Auvo(f"{const.BASE_DIR}\chromedriver.exe")
        super().__init__()

        screen_width = self.winfo_screenwidth()
        screen_heigth = self.winfo_screenheight()

        # Configuring size of the window
        self.geometry(f"450x550+{int((screen_width - 450)/2)}+{int((screen_heigth - 550)/2)}")

        self.iconbitmap(f'{const.BASE_DIR}\images\iconTracking.ico')
        self.img_button = ImageTk.PhotoImage(Image.open(str(const.BASE_DIR)+r"\images\btn.jpg"))
        self.img_bg     = ImageTk.PhotoImage(Image.open(str(const.BASE_DIR)+r"\images\base.jpg"))

        self.mainFrame = tk.Label(self, image=self.img_bg)
        self.mainFrame.place(width=450, height=550)

        # Title
        self.title("Tracking")

        # Name of collaborator
        self.name = tk.StringVar()
        self.names = [list(self.auvo.getTeams().keys())[0]]
        self.names = self.names + list(self.auvo.getUsers().keys())
        self.name.set(self.names[0])
        self.collaborators = tk.OptionMenu(self, self.name, *self.names)
        self.collaborators['menu'].insert_separator(1)
        self.collaborators.config(bg="white", fg="black",font=("Arial", 10, "bold"), borderwidth=0, width=38)
        self.collaborators.place(relx=0.175, rely=0.37)

        # Entries of interval
        self.beginInt = tk.Entry(self, width=18, background="white", borderwidth=0)
        self.endInt   = tk.Entry(self, width=18, background="white", borderwidth=0)
        self.beginInt.place(relx=0.18, rely=0.625)
        self.endInt.place(relx=0.58, rely=0.625)
        
        # CheckButtons
        var = tk.IntVar()
        checkboxes = []
        
        checkboxes.append(tk.Checkbutton(self, onvalue=1, variable=var, text="Dia", command=self.dayInterval, background="#F6F5F5"))  
        checkboxes.append(tk.Checkbutton(self, onvalue=2, variable=var, text="Semana", command=self.weekInterval, background="#F6F5F5"))  
        checkboxes.append(tk.Checkbutton(self, onvalue=3, variable=var, text="Mês", command=self.monthInterval, background="#F6F5F5"))  
    
        checkboxes[0].place(relx=0.18, rely=0.68)
        checkboxes[1].place(relx=0.18, rely=0.73)
        checkboxes[2].place(relx=0.18, rely=0.78)

        # Warning Label
        self.warning_text = tk.StringVar()
        self.warning_label = tk.Label(self, textvariable=self.warning_text, font=('Arial', 8), fg='red', background='#F6F5F5')
        self.warning_label.place(relx=0.18, rely=0.84)

        # Button to generate the report
        self.btn_generate = tk.Button(self, borderwidth=0, image=self.img_button)
        self.btn_generate.place(relx=0.18, rely=0.9)
        self.btn_generate['command'] = lambda: self.generateReport(self.beginInt.get(), self.endInt.get(), self.name.get(), self.name.get() in list(self.auvo.getUsers().keys()))
    
    def __exit__(self):
        self.auvo.__exit__()

    def generateReport(self, begin, end, collaborator, is_collab=True):
        """
        Will generate the report with the informations of the graphic interface

        :Args
            begin: String -> begin of the interval
            end: String -> end of the interval
            collaborator: String -> name of the collaborator

        :Usage
            generateReport("16/05/2022", "18/05/2022", "clayton")
            
        """
        begin_day =   int(begin.split('/')[0])
        begin_month = int(begin.split('/')[1])
        begin_year =  int(begin.split('/')[2])
        last_day_begin = self.getLastDayMonth(int(begin_month), int(begin_year))

        end_day =   int(end.split('/')[0])
        end_month = int(end.split('/')[1])
        end_year =  int(end.split('/')[2])
        last_day_end = self.getLastDayMonth(int(end_month), int(end_year))

        # Verifing if the interval is correct
        # The year of the begin must be less or equal of the end's year
        # if the interval is in the same month, the begin's day must be less or equal of the end's day
        # if the interval is in different months, then the begin's month must be previous than the end's month
        # The day of the interval must be less or equal to the last day of the month

        if (begin_year <= end_year) and ((begin_month == end_month and begin_day <= end_day) or (begin_month < end_month)) and (begin_day <= last_day_begin and end_day <= last_day_end):
            self.warning_text.set("")
            
            if not self.auvo.site_open:
                self.auvo.openSite()
                self.auvo.loginAuvo()
                self.auvo.goToRelatorios()
                
            df = self.auvo.getIntervalReport(begin, end, collaborator, is_collab)
            xlsxReport(df)
            emailReport(df)
            postNotion(df)
            
            
        else:
            # If it is not valid, alert the user
            self.warning_text.set("Atenção: Insira valores válidos.")
            

    def dayInterval(self):
        """
        Will insert in the entries the interval that represents the current day
        """
        cur_time = time.localtime()
        day = time.strftime("%d/%m/%Y", cur_time)

        self.beginInt.delete(0,tk.END)
        self.beginInt.insert(0,day)

        self.endInt.delete(0,tk.END)
        self.endInt.insert(0,day)


    def weekInterval(self):
        """
        Will insert in the entries the interval that represents the current week
        """
        today = date.today()
        day   = today.day
        month = today.month
        year  = today.year

        # While the day isn't monday, decrement the day
        while today.strftime("%a") != "Mon":
            if day == 1:
                day = self.getLastDayMonth(month - 1, year)
                today = today.replace(day = day, month=month-1)
            else:
                today = today.replace(day = day - 1)
                day -= 1
        
        # Insert the first day in the entry
        self.beginInt.delete(0,tk.END)
        self.beginInt.insert(0,f"{day}/{today.month}/{year}")

        # Getting the last day of the month
        last_day =  self.getLastDayMonth(month, year)
        day = day + 4 if day + 4 <= last_day else day + 4 - last_day

        # Insert the last day in the entry
        self.endInt.delete(0,tk.END)
        self.endInt.insert(0,f"{day}/{month}/{year}")

    def monthInterval(self):
        """
        Will insert in the entries the interval that represents the current month
        """
        today = date.today()
        month = today.month
        year  = today.year

        # Getting the last day of the month
        last_day = self.getLastDayMonth(month, year)

        # Insert the first day in the entry
        self.beginInt.delete(0,tk.END)
        self.beginInt.insert(0,f"01/0{month}/{year}")

        # Insert the last day in the entry
        self.endInt.delete(0,tk.END)
        self.endInt.insert(0,str(last_day)+f"/{month}/{year}")

    def getLastDayMonth(self, month:int, year:int) -> int:
        """
        Will return the last day of the month

        :Args
            month: int
            year: int

        :Usage
            getLastDayMont(5, 2022)
        """

        # Getting the last day of the month
        next_month = datetime.date(year, month, 1).replace(day=28) + datetime.timedelta(days=4)
        last_day =  next_month - datetime.timedelta(days=next_month.day)
        last_day = int(last_day.strftime("%d"))

        return last_day