from auvo.auvo import Auvo

   
inst = Auvo("chromedriver.exe")
inst.openSite()
inst.loginAuvo()
inst.goToRelatorios()
inst.selectDailyReport('16/05/2022', 'thiago')
print(inst.getReportData('16/05/2022', 'thiago'))