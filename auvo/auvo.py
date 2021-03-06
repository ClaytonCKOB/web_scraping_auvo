import pandas as pd
from pandas import DataFrame
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import datetime
import time
import requests
import json
import auvo.constants as const

class AuvoApi():
    def __init__(self):
        pass

    def getAccessToken(self) -> str:
        """
        Method will make a request to get the access Token
        """ 

        headers = {'Content-Type': 'application/json'}
        request = requests.get(f'https://api.auvo.com.br/v2/login/?apiKey={const.APP_KEY}&apiToken={const.TOKEN}', headers=headers)
        request = request.json()
        request = json.loads(json.dumps(dict(request['result']), indent=5))
        self.accessToken = request['accessToken']

        return self.accessToken

 
    def getUsers(self) -> dict:
        """
        Method will request the list of collaborators
        """
        users = {}

        headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer '+ self.getAccessToken()
        }
        
        request = requests.get(f'https://api.auvo.com.br/v2/users/?paramFilter={""}&page={1}&pageSize={10}&order={"asc"}&selectfields={""}', headers=headers)
        
        request = request.json()
        request = json.loads(json.dumps(dict(request['result']), indent=5))
        request = request['entityList']
        
        for user in request:
            if "Técnico de Instalação" in user['jobPosition']:
                users[user['name']] = user['userID']
        
        return users
    
    def getTeams(self) -> dict:
        """
        Method will request the list of teams
        """

        teams = {}

        headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer '+ self.getAccessToken()
        }
        
        request = requests.get(f'https://api.auvo.com.br/v2/teams/?paramFilter={""}&page={1}&pageSize={10}&order={"asc"}&selectfields={""}', headers=headers)
        
        request = request.json()
        request = json.loads(json.dumps(dict(request['result']), indent=5))
        request = request['entityList']
        
        for team in request:
            teams[team['description']] = team['teamUsers']
        
        return teams

    def getTasksId(self, date, collaborator):
        """
        Will request the list of tasks of the day and will return the ids of the ones that are 
        related to the km.

        :Args
            date: String -> represent the day that will be use in the request
            collaborator: String
        
        :Usage
            getTaskId('20/05/2022', 'clayton)

        """
        ids = []
        year = date[-4:]
        day = date[:2]
        date = year + '-' + date[3:len(date)-5] + '-' + day     # Converting the format of the date
        users = self.getUsers()
        id = users[collaborator]

        # Parameters
        headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer '+ self.getAccessToken()
        }
        

        paramFilter = {
            'startDate': date,
            'endDate': date,
            'idUserTo': id
        }

        paramFilter = json.loads(json.dumps(paramFilter))

        # Request
        request = requests.get(f'https://api.auvo.com.br/v2/tasks/?paramFilter={paramFilter}&page={1}&pageSize={10}&order={"asc"}', headers=headers)
        
        if request.status_code < 400 :
            # Converting the response to json
            request = request.json()
            request = json.loads(json.dumps(dict(request['result']), indent=5))
            request = request['entityList']

            # Searching for the ids where the word 'veiculo' is included
            for task in request:
                if 'VEÍCULO-' in task['customerDescription'] or 'VEÍCULO' in task['customerDescription']:
                    ids.append(task['taskID'])
        elif request.status_code == 404:
            return -1

        return ids
        
    def getTaskInfo(self, day, collaborator):
        """
        Will make a request to get the answers of the collaborators from the questionnaire
        
        :Args
            day: String -> represent the day that will be use in the request
            collaborator: String 
        
        :Usage
            getTaskInfo('20/05/2022', 'Clayton)

        """
        ids = self.getTasksId(day, collaborator)
        mileage = []

        headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer '+ self.getAccessToken()
        }

        if ids != -1:
            for id in ids:
                request = requests.get(f'https://api.auvo.com.br/v2/tasks/{id}', headers=headers)
                request = request.json()
                request = json.loads(json.dumps(dict(request['result']), indent=5))

                if request['questionnaires'] != []:
                    request = request['questionnaires'][0]['answers'][1]['reply']

                    mileage.append(request)
        else: return [-1]

        return mileage


class Auvo(AuvoApi):
    def __init__(self, driver_path=""):
        global driver
        self.driver_path = driver_path
        driver = webdriver.Chrome(self.driver_path)
        driver.minimize_window()

        self.site_open = False

        # Dict with the collaborators and their id
        self.collaborators = {}
    
    def __exit__(self):
        driver.quit()

    # Method to open the website of booking
    def openSite(self):
        driver.maximize_window()
        driver.get(const.SITE)
        self.site_open = True
        

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
        driver.implicitly_wait(15)
        btnRel = driver.find_element(By.ID, "controlaClique3")
        btnRel.click()

        opKmRodado = driver.find_element(By.CSS_SELECTOR, 'a[href="/kmRodado"]')
        opKmRodado.click()

    
    def getIntervalReport(self, begin, end, collaborator, is_collab) -> DataFrame:
        """
        Will collect the data in the defined interval

        :Args
            begin: String -> begin of the interval
            end: String -> end of the interval
            collaborator: String -> name of the collaborator

        :Usage
            getIntervalReport("16/05/2022", "18/05/2022", "clayton")
        """
        begin = begin.split("/")
        end = end.split("/")
        day = int(begin[0])
        month = int(begin[1])
        data = pd.DataFrame()

        # Getting the last day of the month
        next_month = datetime.date(int(begin[2]), int(begin[1]), 1).replace(day=28) + datetime.timedelta(days=4)
        last_day =  next_month - datetime.timedelta(days=next_month.day)
        last_day = last_day.strftime("%d")

        while (begin[1] == end[1] and day <= int(end[0])) or (begin[1] != end[1] and day != int(end[0]) + 1):
            self.selectDailyReport(str(day)+"/"+str(month)+"/"+end[2], collaborator, is_collab)
            time.sleep(11)
            data = pd.concat([data, self.getReportData(str(day)+"/"+str(month)+"/"+end[2], collaborator, is_collab)], axis=0)
            if day + 1 <= int(last_day):
                day += 1
            else:
                day = 1
                month += 1

        data = data.reset_index()

        return data

    def selectDailyReport(self, day, collaborator, is_collab):
        """
        Will generate the report of the collaborator in the specified day

        :Args
            day: String -> will specify the report's day
            collaborator: String -> name of the collaborator
            
        :Usage
            selectDailyReport('15/05/2022', 'clayton')

        """
        
        driver.implicitly_wait(15)
        try:
            # Select the begin of the interval
            begin_element = driver.find_element(By.ID, "dataInicio")
            begin_element.click()
            self.selectDayinTable(day)

        except:
            driver.get(driver.current_url)
            driver.refresh()
            driver.implicitly_wait(15)
            # Select the begin of the interval
            begin_element = driver.find_element(By.ID, "dataInicio")
            begin_element.click()
            self.selectDayinTable(day)

        driver.implicitly_wait(15)
        # Select the end of the interval
        end_element = driver.find_element(By.ID, "dataFim")
        end_element.click()
        self.selectDayinTable(day)


        
        # Configuring the filter 
        filter_element = driver.find_element(By.ID, "select2-filtrarPor-container")
        filter_element.click()
        filter_input = driver.find_element(By.CLASS_NAME, "select2-search__field")

        if is_collab:
            # Select the collaborator
            filter_input.send_keys("Colaborador")
            filter_input.send_keys(Keys.ENTER)
            collab_element = driver.find_element(By.ID, "select2-listaColaboradores-container")
            collab_element.click()
            
        else:
            filter_input.send_keys("Equipe")
            filter_input.send_keys(Keys.ENTER)

            user_search_element = driver.find_element(By.ID, "select2-listaEquipes-container")
            user_search_element.click()

        user_search_element = driver.find_element(By.CLASS_NAME, "select2-search__field")
        user_search_element.click()
        user_search_element.send_keys(collaborator)
        user_search_element.send_keys(Keys.ENTER)

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
                next_element = driver.find_element(By.XPATH, "/html/body/div[5]/div[1]/table/thead/tr[2]/th[3]")
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


    def getReportData(self, day, collaborator, is_collab) -> DataFrame:
        """
        Will get the atributes of the report

        :Args
            day: String -> will specify the report's day
            collaborator: String -> name of the collaborator
            
        :Usage
            getReportData('15/05/2022', 'clayton')
        """
        driver.implicitly_wait(20)

        if is_collab:
            # Finding the elements
            km_sistema = driver.find_element(By.XPATH, '//*[@id="table"]/tbody/tr/td[3]')
            km_total = driver.find_element(By.XPATH, '//*[@id="table"]/tbody/tr/td[5]')
            collab = collaborator
        else:
            # When it is a team the program needs to get the higher values
            first_km_total = driver.find_element(By.XPATH, '//*[@id="table"]/tbody/tr/td[5]')
            second_km_total = driver.find_element(By.XPATH, '//*[@id="table"]/tbody/tr[2]/td[5]')
            
            first_km_total = first_km_total.get_attribute("data-order")
            first_km_total = float(first_km_total[:len(first_km_total)-3] + "." + first_km_total[len(first_km_total)-3:])

            second_km_total = second_km_total.get_attribute("data-order")
            second_km_total = float(second_km_total[:len(second_km_total)-3] + "." + second_km_total[len(second_km_total)-3:])

            if first_km_total > second_km_total:
                km_sistema = driver.find_element(By.XPATH, '//*[@id="table"]/tbody/tr/td[3]')
                km_total = driver.find_element(By.XPATH, '//*[@id="table"]/tbody/tr/td[5]')

            else:
                km_sistema = driver.find_element(By.XPATH, '//*[@id="table"]/tbody/tr[2]/td[3]')
                km_total = driver.find_element(By.XPATH, '//*[@id="table"]/tbody/tr[2]/td[5]')

            collab = "Thiago Costa"


        # Treating each value
        km_sistema = km_sistema.get_attribute("data-order")
        km_sistema = float(km_sistema[:len(km_sistema)-3] + "." + km_sistema[len(km_sistema)-3:])       
        km_total = km_total.get_attribute("data-order")
        km_total = float(km_total[:len(km_total)-3] + "." + km_total[len(km_total)-3:])     

        # Get the data from the questionnaires 
        mileage = self.getTaskInfo(day, collab)
        beginCar = int(mileage[0]) if len(mileage) >= 1 and ('www' not in str(mileage[0]).split('.') and 'apresentou' not in str(mileage[0]).split(' ')) else 0
        endCar = int(mileage[1]) if len(mileage) >= 2 and   ('www' not in str(mileage[1]).split('.') and 'apresentou' not in str(mileage[1]).split(' ')) else 0
        
        
        # Creating the dict with the info
        data = {
            "Nome": [collaborator.upper()],
            "Km Inicial Carro": [beginCar],
            "Km Final Carro": [endCar],
            "Km Sistema": [km_sistema],
            "Km Total": [km_total],
            "Data": [day], 
            "Comp. Auvo": [round((km_sistema - km_total)*100)/100],
            "Comp. Veículo": [round((km_total - (endCar - beginCar))*100)/100]
        }

        return pd.DataFrame(data)


    

