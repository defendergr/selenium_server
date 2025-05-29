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
import os, platform
import socket


data = ''
# not_connected = 0
# times_has_lost_connection = 0


def progress_bar(percent=0, divide=100, width=20):
    try:
        left = width * percent // (divide - 1)
        right = width - left
        bar = '█' * int(left) + '░' * int(right)
        return bar
    except ZeroDivisionError:
        pass



@app.get('/')
def home():
    text = 'sport links, search machine API v1.0.12 By Defender'
    return RedirectResponse("https://defendersportstreams.com/")

@app.get("/agrules/")
def agrules():
    return "https://defendersportstreams.com"

@app.get("/selenium/")
async def selenium(request: Request, url='', wait=''):
    token = request.headers.get('token')
    # sys.stdout.write('header token:', token)
    # print('header token:',token)
    if token not in API_KEYS:
        return 'invalid token'
    elif token in API_KEYS:
        if 'http' or 'https' in url:
            url = url
        else:
            url = 'https://' + url
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
        if wait == 'on':
            driver.get(url=url)
            driver.implicitly_wait(10)
            data = driver.page_source
            driver.close()
            return data

        # if log == 'on':
        #     driver.get(url=url)
            # network = driver.execute_script(
            #     "var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;")
            # network = driver.get_log('performance')
            # driver.close()
            # return network

        if url != '' and 'widget' not in url:
            driver.get(url=url)
            data = driver.page_source
            driver.close()
            return data
        else:
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
        print("\nCompleted!")
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



@app.get("/system/")
def data(request: Request):
    token = request.headers.get('token')
    if token in API_KEYS:
        # ASCII logo
        logo = figlet_format('Defender', font='standard') # fonts url http://www.figlet.org/examples.html
        # console print
        cprint(logo, 'green')

        if os.name == 'posix':
            uptime = os.popen('uptime -p').read()
        else:
            uptime = None

        system_info = {
            "logo": logo, # use <pre> tag in html
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "OS": platform.platform(),
            "OS release": platform.release(),
            "OS version": platform.version(),
            "OS architecture": platform.architecture(),
            "CPU cores": psutil.cpu_count(logical=False),
            "CPU threads": psutil.cpu_count(),
            "RAM": str(round(psutil.virtual_memory().total / (1024 ** 3)))+"GB",
            "Disk": str(round(psutil.disk_usage('/').total / (1024 ** 3)))+"GB",
            "GPU VRAM": str(round(psutil.virtual_memory().total / (1024 ** 3)))+"GB",
            "CPU load": str(psutil.cpu_percent())+"%",
            "Memory load": str(psutil.virtual_memory().percent)+"%",
            # "CPU temperature": str(psutil.sensors_temperatures(fahrenheit=False))+"°C", # doesn't work in windows
            "Network received": str(round(psutil.net_io_counters().bytes_recv/(1024 ** 2)))+"MB",
            "Network sent": str(round(psutil.net_io_counters().bytes_sent/(1024 ** 2)))+"MB",
            "Uptime": uptime,
            "Disk usage": str(psutil.disk_usage('/').percent)+"% of "+str(round(psutil.disk_usage('/').total / (1024 ** 3)))+"GB",

        }
        return JSONResponse(content=system_info)
        # return 'system info under construction'
    else:
        sys.stdout.write('invalid token\n')
        return 'invalid token'



# use when you want to run the job periodically at certain time(s) of day
@scheduler.scheduled_job('cron', minute='00,10,20,30,40,50') #('interval', seconds=600) #
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
        print("\nCompleted!")
        new_data = driver.page_source
        driver.close()

        if data != new_data:
            data = new_data
            requests.get(url=WEBHOOK_URL)
            print("new data added")
        else:
            print("no new data")
    except requests.exceptions.ConnectionError:
        pass
        # global not_connected
        # not_connected += 1


#
# def is_connected(hostname):
#   try:
#     # See if we can resolve the host name - tells us if there is
#     # A DNS listening
#     host = socket.gethostbyname(hostname)
#     # Connect to the host - tells us if the host is actually reachable
#     s = socket.create_connection((host, 80), 2)
#     s.close()
#     return True
#   except Exception:
#      pass # We ignore any errors, returning False
#   return False
#
#
# @scheduler.scheduled_job('interval', seconds=60) #('cron', minute='05,15,25,35,45,55') #
# def connection_status():
#     global not_connected
#     global times_has_lost_connection
#     if not is_connected("192.168.2.1"):
#         not_connected += 1
#         times_has_lost_connection += 1
#     if not_connected > 3:
#         print('No internet connection!')
#         os.system(f'echo {SYSTEM_PASSWORD} | sudo -S reboot')
#     if is_connected("192.168.2.1"):
#         not_connected = 0
#     print(f"system connected: {is_connected('192.168.2.1')}.", f"Times not connected: {not_connected}.", f"Times has lost connection: {times_has_lost_connection}.")
