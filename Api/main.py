import datetime
import sys
import time
import psutil
from fastapi.responses import RedirectResponse, JSONResponse
import requests
from fastapi import Request
from termcolor import cprint
from pyfiglet import figlet_format

from Api import app, scheduler
from Api.config import *
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os, platform
import socket


data = ''
# not_connected = 0
# times_has_lost_connection = 0


def progress_bar(percent=0, divide=100, width=20):
    try:
        left = width * percent // (divide - 1)
        right = width - left
        return f"[{'#' * left}{' ' * right}] {percent / (divide - 1) * 100:.1f}%"
    except:
        return "[#] 100.0%"


@app.get("/")
def home():
    return RedirectResponse("https://defendersportstreams.com/")


# @app.get("/agrules")
# def agrules():
#     return RedirectResponse("https://defendersportstreams.com/agrules")


@app.get("/selenium")
async def selenium(request: Request, url: str = '', wait: str = ''):
    token = request.headers.get('token')
    # sys.stdout.write('header token:', token)
    # print('header token:',token)
    if token not in API_KEYS:
        return 'invalid token'
    elif token in API_KEYS:
        try:
            if not url:
                return {"message": "No URL provided"}
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
            if wait:
                time.sleep(int(wait))
            data = driver.page_source
            driver.close()
            return {"data": data}
        except Exception as e:
            return {"error": str(e)}


@app.get("/data")
async def data(request: Request):
    token = request.headers.get('token')
    if token in API_KEYS:
        sys.stdout.write('token accepted\n')
        return data
    else:
        sys.stdout.write('invalid token\n')
        return 'invalid token'


# use when you want to run the job periodically at certain time(s) of day
@scheduler.scheduled_job('cron', minute='00,10,20,30,40,50')  # ('interval', seconds=600) #
def cron_task():
    global data
    try:
        WEBHOOK_URL = 'https://defendersportstreams.com/webhook'
        url = URL
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
        try:
            driver.get(url=url)
        except Exception as e:
            print('connection error', e)

        ele = driver.find_elements(By.TAG_NAME, 'h2')
        elements = len(ele)
        percent = 0
        sys.stdout.write(f'{elements} Elements found in URL \n')
        
        for acord in range(0, elements):
            element = ele[acord]
            if element.is_displayed():
                per = progress_bar(percent=percent, divide=len(ele))
                percent += 1
                elements -= 1

                sys.stdout.write(f'\r{elements} Elements remaining... {per}')
                sys.stdout.flush()
                
                try:
                    # Scroll element into view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'})", element)

                    # Try to find and switch to iframe if it exists
                    try:
                        iframe = driver.find_element(By.CSS_SELECTOR, "iframe.container-c22f2ada4abad36c86abf7381670dc0b9365")
                        driver.switch_to.frame(iframe)
                        print("Switched to iframe")
                    except:
                        pass  # No iframe found, continue with normal flow
                    
                    # Wait for element to be clickable and click it
                    wait = WebDriverWait(driver, 10)
                    element = wait.until(EC.element_to_be_clickable((By.ID, element.get_attribute('id'))))
                    
                    # Try normal click first
                    try:
                        element.click()
                    except:
                        # If normal click fails, try JavaScript click
                        driver.execute_script("arguments[0].click();", element)
                        sys.stdout.write(" Used JavaScript click as fallback")
                    
                    # Switch back to default content after clicking
                    driver.switch_to.default_content()
                except Exception as e:
                    print(f"\nCould not click element {acord}: {str(e)}")
                    # Make sure we're back to default content if something goes wrong
                    try:
                        driver.switch_to.default_content()
                    except:
                        pass
                    continue
                    
        print("\nCompleted!")
        new_data = driver.page_source
        driver.close()

        if data != new_data:
            data = ''
            data = new_data
            requests.get(url=WEBHOOK_URL)
            print("new data added")
        else:
            print("no new data")
    except requests.exceptions.ConnectionError as e:
        print('connection error', e)


@scheduler.scheduled_job('interval', days=7)  # ('cron', minute='05,15,25,35,45,55') #
def schedule_reboot():
    os.system(f'echo {SYSTEM_PASSWORD} | sudo -S reboot')


@scheduler.scheduled_job('interval', hours=4)  # ('cron', minute='05,15,25,35,45,55') #
def schedule_firefox_kill():
    os.system(f'echo {SYSTEM_PASSWORD} | sudo pkill -f firefox-esr')
