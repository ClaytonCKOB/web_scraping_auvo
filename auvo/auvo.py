from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
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


    def selectDailyReport(self, day, collaborator):
        """
        Will generate the report of the collaborator in the specified day

        :Args
            day: String -> will specify the report's day
            collaborator: String -> name of the collaborator
            
        :Usage
            selectDailyReport('15/05/2022', 'clayton')

        """
        
        driver.implicitly_wait(10)

        # Select the begin of the interval
        begin_element = driver.find_element(By.ID, "dataInicio")
        begin_element.click()
        self.selectDayinTable(day)

        # Select the end of the interval
        end_element = driver.find_element(By.ID, "dataFim")
        end_element.click()
        self.selectDayinTable(day)


        # Select the collaborator
        collab_element = driver.find_element(By.ID, "select2-listaColaboradores-container")
        collab_element.click()
        collab_search_element = driver.find_element(By.CLASS_NAME, "select2-search__field")
        collab_search_element.click()
        collab_search_element.send_keys(collaborator)
        collab_search_element.send_keys(Keys.ENTER)

        # Click the submit button
        btn_get_report = driver.find_element(By.ID, "gerarConsulta")
        btn_get_report.click()


    def selectDayinTable(self, day):
        """
        Will select the day in the opened table

        :Args
            day: String -> the day that will be selected
        
        :Usage
            selectDayinTable('15/05/2022')

        """

        # Variables
        months = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        date = day.split('/')
        td_y = 1 if int(date[0]) < 15 else 3
        td_x = 1
        found = False

        # Select the month
        month_element = driver.find_element(By.CLASS_NAME, "datepicker-switch")
        month_in_num = months.index(month_element.text.split(' ')[0])

        while int(month_in_num) != int(date[1]):
            if int(month_in_num) < int(date[1]):
                next_element = driver.find_element(By.CLASS_NAME, "next")
                next_element.click()
            else:
                prev_element = driver.find_element(By.CLASS_NAME, "prev")
                prev_element.click()
            
            month_element = driver.find_element(By.CLASS_NAME, "datepicker-switch")
            month_in_num = months.index(month_element.text.split(' ')[0])

        # Select the day
        while not found:
            end = driver.find_element(By.XPATH, f"/html/body/div[5]/div[1]/table/tbody/tr[{td_y}]/td[{td_x}]")
            
            if end.text == date[0]:
                end.click()
                found = True
            else:
                td_x += 1
                if td_x == 8:
                    td_x = 1
                    td_y += 1
                    

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