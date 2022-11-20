from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
import os
from dotenv import load_dotenv
import smtplib

#setting up the environment
load_dotenv()
#driver = webdriver.Chrome('chromedriver.exe')
WINDOW_SIZE = "1920,1080"
#chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
#global variables
no_of_subjects = 0
examMarks = {}


#function to send emails when new marks are received
def sendMail(newMarks):

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.getenv('EMAIL_SENDER'), os.getenv('EMAIL_PASSWORD'))
    message = "Subject: New Marks Available\n\n"
    for key in newMarks:
        message += newMarks[key][0] + " " + newMarks[key][1] + " " + newMarks[key][2] + "/" + newMarks[key][3] + "\n"
    server.sendmail(os.getenv('EMAIL_SENDER'), os.getenv('EMAIL_RECEIVER'), message)


#function to fetch marks from the webkiosk page
def fetchMarks():

    html = driver.page_source
    with open("test.html", "w") as f:
        f.write(html)
    soup = BeautifulSoup(open('test.html'), 'html.parser')
    table = soup.find('table', class_='sort-table')
    newMarks = {}
    for row in table.tbody.find_all('tr'):
        columns = row.find_all('td')
        if(columns != []):
            sno = columns[0].text.strip()
            subject = columns[2].text.strip()
            examType = columns[3].text.strip()
            fullMarks = columns[4].text.strip()
            obtainedMarks = columns[5].text.strip()
            if ((subject + examType) not in examMarks):
                examMarks[subject + examType] = subject, examType, obtainedMarks, fullMarks
                newMarks[subject + examType] = subject, examType, obtainedMarks, fullMarks
    print(newMarks)        
    if(newMarks):
        try:
            sendMail(newMarks)
        except:
            writeLogs("sendMail()")
        newMarks={}
        time.sleep(3600)
        fetchMarks()
    else:
        time.sleep(3600)
        fetchMarks()


#function to log which function broke the function, which will be helpful when debugging the script
def writeLogs(errorFunction):

    with open("logs.txt", "a") as f:
        f.write(errorFunction + time.ctime() + "\n")

def setup(user, passw, sem):

    global no_of_subjects
    #open('marks.txt', 'w').close()
    driver.get("https://webkiosk.thapar.edu/")
    username = driver.find_element("name", "MemberCode")
    username.send_keys(user)
    password = driver.find_element("name","Password") 
    password.send_keys(passw)
    driver.find_element("name","BTNSubmit").click()
    driver.get("https://webkiosk.thapar.edu/StudentFiles/Exam/StudentEventMarksView.jsp")
    driver.find_element("name","exam").send_keys(sem)    
    driver.find_element(By.XPATH,'//input[@type="submit"]').click()

    try:
        fetchMarks()
    except:
        writeLogs("fetchMarks()")
    driver.close()


if __name__ == "__main__":
    rollNumber = os.getenv('ROLL_NUMBER')
    passw = os.getenv('WEBKIOSK_PASSWORD')
    semester = os.getenv('SEMESTER')
    try:
        setup(rollNumber, passw, semester)
    except:
        writeLogs("setup()")
