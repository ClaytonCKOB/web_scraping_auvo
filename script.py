# This document will be the script that will be executed by the system periodically
from auvo.auvo import *
from auvo.auvo_report import *
import auvo.constants as const
from datetime import date

def getLastDayMonth(month:int, year:int) -> int:
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

auvo = Auvo(f"{const.BASE_DIR}\chromedriver.exe")

collaborator = "Técnicos SP"

today = date.today()
day   = today.day
month = today.month
year  = today.year

# While the day isn't monday, decrement the day
while today.strftime("%a") != "Mon":
    if day == 1:
        day = getLastDayMonth(month - 1, year)
        today = today.replace(day = day, month=month-1)
    else:
        today = today.replace(day = day - 1)
        day -= 1

# Get the begin of the interval
begin = f"{day}/{today.month}/{year}"

# Getting the last day of the month
last_day =  getLastDayMonth(month, year)
day = day + 4 if day + 4 <= last_day else day + 4 - last_day

# Get the end of the interval
end = f"{day}/{month}/{year}"

auvo.openSite()
auvo.loginAuvo()
auvo.goToRelatorios()

df = auvo.getIntervalReport(begin, end, collaborator, False)

xlsxReport(df)
emailReport(df)
postNotion(df)

auvo.__exit__()