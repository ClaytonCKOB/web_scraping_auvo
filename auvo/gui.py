# This file contains the graphic configurations
from calendar import day_abbr
from auvo.auvo import Auvo
from auvo.auvo_report import *
import time
import datetime
from datetime import date
import tkinter as tk
from PIL import ImageTk, Image

class Tracking(tk.Tk):
    def __init__(self):
        inst = Auvo("chromedriver.exe")
        super().__init__()

        self.iconbitmap(f'images\iconTracking.ico')
        self.img_button = ImageTk.PhotoImage(Image.open(r"images\btn.jpg"))
        self.img_bg     = ImageTk.PhotoImage(Image.open(r"images\base.jpg"))

        self.mainFrame = tk.Label(self, image=self.img_bg)
        self.mainFrame.place(width=450, height=550)

        # Title
        self.title("Tracking")

        # Configuring size of the window
        self.geometry("450x550")

        # Name of collaborator
        self.name = tk.StringVar()
        self.names = list(inst.getUsers().keys())
        self.name.set(self.names[0])
        self.collaborators = tk.OptionMenu(self, self.name, *self.names)
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

        # Button to generate the report
        self.btn_generate = tk.Button(self, borderwidth=0, image=self.img_button)
        self.btn_generate.place(relx=0.18, rely=0.9)
        self.btn_generate['command'] = lambda: self.generateReport(self.beginInt.get(), self.endInt.get(), self.name.get())
    
    def generateReport(self, begin, end, collaborator):
        """
        Will generate the report with the informations of the graphic interface

        :Args
            begin: String -> begin of the interval
            end: String -> end of the interval
            collaborator: String -> name of the collaborator

        :Usage
            generateReport("16/05/2022", "18/05/2022", "clayton")
            
        """

        inst = Auvo("chromedriver.exe")
        inst.openSite()
        inst.loginAuvo()
        inst.goToRelatorios()
        df = inst.getIntervalReport(begin, end, collaborator)
        xlsxReport(df)
        emailReport(df)
        postNotion(df)
    

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
            today = today.replace(day = day - 1)
            day -= 1
        
        # Insert the first day in the entry
        self.beginInt.delete(0,tk.END)
        self.beginInt.insert(0,f"{day}/{month}/{year}")

        # Getting the last day of the month
        next_month = datetime.date(year, month, 1).replace(day=28) + datetime.timedelta(days=4)
        last_day =  next_month - datetime.timedelta(days=next_month.day)
        day = day + 4 if day + 4 <= int(last_day.strftime("%d")) else day + 4 - int(last_day.strftime("%d"))

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
        next_month = datetime.date(year, month, 1).replace(day=28) + datetime.timedelta(days=4)
        last_day =  next_month - datetime.timedelta(days=next_month.day)

        # Insert the first day in the entry
        self.beginInt.delete(0,tk.END)
        self.beginInt.insert(0,f"01/{month}/{year}")

        # Insert the last day in the entry
        self.endInt.delete(0,tk.END)
        self.endInt.insert(0,last_day.strftime("%d")+f"/{month}/{year}")