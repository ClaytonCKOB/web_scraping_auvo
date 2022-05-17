from auvo.auvo import Auvo

   
inst = Auvo("chromedriver.exe")
inst.openSite()
inst.loginAuvo()
inst.goToRelatorios()
inst.selectDailyReport('15/08/2022', 'thiago')