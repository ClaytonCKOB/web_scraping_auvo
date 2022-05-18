from auvo.auvo import Auvo
from auvo.auvo_report import *

   
inst = Auvo("chromedriver.exe")
inst.openSite()
inst.loginAuvo()
inst.goToRelatorios()
df = inst.getIntervalReport("9/05/2022", "13/05/2022", "thiago")
xlsxReport(df)