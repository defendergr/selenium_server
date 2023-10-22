import sys
from fastapi.responses import RedirectResponse
import requests
from fastapi import Request
from Api import app, scheduler
from Api.config import *
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import os



data = ''



def progress_bar(percent=0, divide=100, width=20):
    left = width * percent // (divide - 1)
    right = width - left
    bar = '█' * int(left) + '░' * int(right)
    return bar



@app.get('/')
def home():
    text = 'sport links, search machine API v1.0.12 By Defender'
    return RedirectResponse("https://defendersportstreams.com/")

@app.get("/selenium/")
async def selenium(url: str, request: Request):
    token = request.headers.get('token')
    # sys.stdout.write('header token:', token)
    # print('header token:',token)

    if token not in API_KEYS:
        return 'invalid token'
    elif token in API_KEYS:
        options = Options()
        options.add_argument('--headless')
        if os.name == 'nt':
            service = Service(GeckoDriverManager().install())
        elif os.name == 'posix':
            if os.path.isfile('/usr/bin/geckodriver'):
                service = Service(executable_path='/usr/bin/geckodriver')
            else:
                service = Service(executable_path='/data/data/com.termux/files/usr/bin/geckodriver')
        driver = webdriver.Firefox(service=service, options=options)

        driver.get(url=url)
        ele = driver.find_elements(By.TAG_NAME, 'h2')
        elements = len(ele)
        percent = 0
        sys.stdout.write(f'{elements} Elements found in URL \n')
        for acord in range(0, elements):
            if ele[acord].is_displayed():
                per = progress_bar(percent=percent, divide=len(ele))
                percent += 1
                elements -= 1

                sys.stdout.write(f'\r{elements} Elements remaining... {per}')
                sys.stdout.flush()
                ele[acord].click()
        sys.stdout.write("\rCompleted!\n")
        scraped = driver.page_source
        driver.close()
        return scraped


@app.get("/data/")
def data(request: Request):
    token = request.headers.get('token')
    if token in API_KEYS:
        sys.stdout.write('token accepted\n')
        return data
    else:
        sys.stdout.write('invalid token\n')
        return 'invalid token'


# use when you want to run the job periodically at certain time(s) of day
@scheduler.scheduled_job('cron', minute='00,10,20,30,40,50') #('interval', seconds=60)
def cron_task():
    global data
    WEBHOOK_URL = 'https://defendersportstreams.com/webhook'
    url = 'https://widget.streamsthunder.tv/?d=1&s=1&sp=1,2&fs=12px&tt=none&fc=333333&tc=333333&bc=FFFFFF&bhc=F3F3F3&thc=333333&pd=5px&brc=CCCCCC&brr=2px&mr=1px&tm=333333&tmb=FFFFFF&wb=EBEBEB&bcc=FFFFFF&bsh=0px&sm=1&rdb=EBEBEB&rdc=333333&lk=1&fk=0%22%20width=%22100%%22%20height=%22800%22%20scrolling=%22auto%22%20align=%22top%22%20frameborder=%220%22'
    options = Options()
    options.add_argument('--headless')
    if os.name == 'nt':
        service = Service(GeckoDriverManager().install())
    elif os.name == 'posix':
        if os.path.isfile('/usr/bin/geckodriver'):
            service = Service(executable_path='/usr/bin/geckodriver')
        else:
            service = Service(executable_path='/data/data/com.termux/files/usr/bin/geckodriver')
    driver = webdriver.Firefox(service=service, options=options)

    driver.get(url=url)
    ele = driver.find_elements(By.TAG_NAME, 'h2')
    elements = len(ele)
    percent = 0
    sys.stdout.write(f'{elements} Elements found in URL \n')
    for acord in range(0, elements):
        if ele[acord].is_displayed():
            per = progress_bar(percent=percent, divide=len(ele))
            percent += 1
            elements -= 1

            sys.stdout.write(f'\r{elements} Elements remaining... {per}')
            sys.stdout.flush()
            ele[acord].click()

    sys.stdout.write("\rCompleted!\n")
    new_data = driver.page_source
    driver.close()

    if data != new_data:
        data = new_data
        requests.get(url=WEBHOOK_URL)
        print("new data added")
    else:
        print("no new data")

