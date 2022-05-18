# This file contains the graphic configurations
from auvo.auvo import Auvo
from auvo.auvo_report import *
import tkinter as tk
from PIL import ImageTk, Image

class Tracking(tk.Tk):
    def __init__(self):
        super().__init__()

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
        self.name.set('Clayton')
        self.names = ['Thiago', 'Clayton']
        self.collaborators = tk.OptionMenu(self, self.name, *self.names)
        self.collaborators.config(bg="white", fg="black",font=("Arial", 10, "bold"), borderwidth=0, width=38)
        self.collaborators.place(relx=0.175, rely=0.37)

        # Entries of interval
        self.beginInt = tk.Entry(self, width=18, background="white", borderwidth=0)
        self.endInt   = tk.Entry(self, width=18, background="white", borderwidth=0)
        self.beginInt.place(relx=0.18, rely=0.625)
        self.endInt.place(relx=0.58, rely=0.625)
        
        # Button to generate the report
        self.btn_generate = tk.Button(self, borderwidth=0, image=self.img_button)
        self.btn_generate.place(relx=0.18, rely=0.85)
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