from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time
import json
import auvo.constants as const

class Auvo():
    def __init__(self, driver_path=""):
        global driver
        driver = webdriver.Chrome(driver_path)
        driver.maximize_window()
        
    
    def __exit__(self):
        self.quit()

    # Method to open the website of booking
    def openSite(self):
        driver.get(const.SITE)


    def loginAuvo(self):
        """
        Will insert the necessary information to execute the login.
        """
        
        # Finding the elements
        user_e = driver.find_element(By.CSS_SELECTOR, 'input[id="usuario"]')
        password_e = driver.find_element(By.CSS_SELECTOR, 'input[id="senha"]')
        btn_submit = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        # Clearing its content
        user_e.clear()
        password_e.clear()

        # Inserting the info
        user_e.send_keys(const.USER)
        password_e.send_keys(const.PASS)

        # Submit
        btn_submit.click()


    def goToRelatorios(self):
        """
        Will access the 'Relatorios' page
        """
        driver.implicitly_wait(10)
        btnRel = driver.find_element(By.ID, "controlaClique3")
        btnRel.click()

        opKmRodado = driver.find_element(By.CSS_SELECTOR, 'a[href="/kmRodado"]')
        opKmRodado.click()


    def getDailyReport(self):
        """
        Will get the info of collaborator in the specified day
        """
        pass


    def getAccessToken(self):
        """
        Method will make a request to get the access Token
        """ 

        headers = {'Content-Type': 'application/json'}
        request = requests.get(f'https://api.auvo.com.br/v2/login/?apiKey={const.APP_KEY}&apiToken={const.TOKEN}', headers=headers)
        request = request.json()
        request = json.loads(json.dumps(dict(request['result']), indent=5))
        self.accessToken = request['accessToken']

 
    def getUsers(self):
        """
        Method will request the list of collaborators
        """

        headers = {
          'Content-Type': 'application/json',
          'Authorization': self.accessToken
        }
        request = requests.get('https://api.auvo.com.br/v2/customers/', headers=headers)
        print(request.json)