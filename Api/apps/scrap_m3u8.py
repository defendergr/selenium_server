"""
    @Author: Cody Keller
    @Date: 01/01/2022
    @Description: Python web-scraping tool for downloading M3U8 files
    @Version: 1.2.0
    @Links: http://www.github.com/cody-k
"""

import json
from time import sleep
from selenium import webdriver
# from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import InvalidArgumentException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import os

# IMPORTANT VARS:
DRIVER_PATH = r"C:\Users\Defender\PycharmProjects\Sports_flask\FlaskSportsApp\chromedriver.exe"
OUTPUT_FOLDER_NAME = "downloadedFiles"
URL_TO_SCRAPE = "https://s2watch.link/player.php?id=chftkcosmote1"


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


options = Options()
options.add_argument('--headless')
options.add_argument("--disable-web-security")
options.add_argument("--allow-running-insecure-content")
options.add_argument("--enable-logging")
options.add_argument("--log-level=3")

capabilities = DesiredCapabilities.CHROME
capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
# options.add_argument(capabilities)

service = Service(DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options, )


class M3U8Scraper:
    def __init__(self, url):
        self.url = url
        self.driver = driver
        self.driver.get(self.url)

    # Scrape all .m3u8 links from the page
    def get_m3u8_links(self):
        print(f"{bcolors.OKGREEN}Getting responses from page...{bcolors.ENDC}")
        links = []
        # driver.find_element(by=By.CLASS_NAME, value="link-player-action").click()
        print(driver.get_log('performance'))
        sleep(2)  # gives time for page to load and for requests to come in
        for request in driver.get_log('performance'):
            if (request.url.find("m3u8") != -1):
                links.append(request.url)

        for link in self.driver.find_elements(by=By.TAG_NAME, value='a'):
            if link.get_attribute('href') != None:
                if link.get_attribute('href').find(".m3u8") != -1:
                    print("LINK FOUND: " + link.get_attribute('href'))
                    links.append(link.get_attribute('href'))
        if (len(links) == 0):
            print("No m3u8 links found")
        return links

    # Write all .m3u8 links to a file
    def write_to_file(self, links):
        if (len(links) == 0):
            print("Will not write to file as no links were found")
            return
        file = open("links.txt", "w")
        for link in links:
            file.write(link + "\n")
        file.close()

    def print_to_terminal(self, links):
        if (len(links) == 0):
            print(f"{bcolors.FAIL}Will not print links to terminal as no links were found{bcolors.ENDC}")
            return
        for link in links:
            print(link)

    # Use ffmpeg to download all .m3u8 files
    def download_files(self, links):
        if (len(links) == 0):
            print(f"{bcolors.FAIL}Will not download files as no links were found{bcolors.ENDC}")
            return
        for link in links:
            fileName = link.split("/")[-1].split(".")[0]
            if not os.path.exists(OUTPUT_FOLDER_NAME):
                os.makedirs(OUTPUT_FOLDER_NAME)
            os.system("cd" + OUTPUT_FOLDER_NAME)

            if not os.path.isfile(OUTPUT_FOLDER_NAME + "/" + fileName + ".mp4"):
                os.system("ffmpeg -i " + link + " -codec copy " + OUTPUT_FOLDER_NAME + "/" + fileName + ".mp4")
            else:
                print(f"{bcolors.WARNING}File already exists: {fileName}.mp4{bcolors.ENDC}")
                print(f"{bcolors.WARNING}Adding number to filename and continuing...{bcolors.ENDC}")
                count = 1
                while os.path.isfile(OUTPUT_FOLDER_NAME + "/" + fileName + "(" + str(count) + ")" + ".mp4"):
                    count += 1
                os.system("ffmpeg -i " + link + " -codec copy " + OUTPUT_FOLDER_NAME + "/" + fileName + "(" + str(
                    count) + ").mp4")
            os.system("cd ..")


if __name__ == '__main__':
    try:
        scraper = M3U8Scraper(URL_TO_SCRAPE)
        links = scraper.get_m3u8_links()
        driver.close()
        driver.quit()
        if (len(links) > 0):
            scraper.print_to_terminal(links)
            scraper.download_files(links)
        print(f"{bcolors.OKBLUE}Done...{bcolors.ENDC}")
    except InvalidArgumentException:
        print(f"{bcolors.FAIL}ERROR - Invalid URL: {URL_TO_SCRAPE}{bcolors.ENDC}")
    except TimeoutException:
        print(f"{bcolors.FAIL}ERROR - Timeout occurred{bcolors.ENDC}")
    except NoSuchElementException:
        print(f"{bcolors.FAIL}ERROR - No element found{bcolors.ENDC}")

    exit()
