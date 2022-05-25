
# Web Scraping Auvo

This project has the goal of automate the search of information in the Auvo plataform, organize the
data and create reports with the information. To get the data, I used the Selenium and requests libraries, with Selenium the software automate the tasks and with requests it creates the 
connection with Auvo's API. To organize the information, the project uses the Pandas library.
After the data is organized, the program create a xlsx file, send an email, when there are relevant information, and integrate the values in a Notion table.



## Requirements

Install the libraries used in the project with the command:

```bash
  pip install -r requirements.txt
```

You must have the following enviroment variables:
- USER -> Your user to do Auvo's login
- PASS -> Your password of the Auvo's account
- APP_KEY = The key the Auvo generete so You can make requests to their API
- TOKEN = Token genereted by Auvo
- EMAIL = The email that will send the emails (You must authorizate the automation in the gmail account)
- E_PASS = The password of the email
- TO_EMAIL -> The email adress that will recieve the messages
- SECRET -> the secret created by Notion
- DB_ID -> The Id of the Notion's page
    