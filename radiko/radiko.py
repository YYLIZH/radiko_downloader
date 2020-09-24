from browsermobproxy import Server
server = Server('browsermob-proxy-2.1.4\\bin\\browsermob-proxy.bat')
server.start()
proxy= server.create_proxy()
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import datetime


filename = input("Please fill in the file name: ")
filename = filename+".mp3"
terminate_time_delta = input("Please set the recording time (min): ")



chrome_options = webdriver.ChromeOptions()
chrome_options.add_extension('0.2.5.8_0.crx')
chrome_options.add_argument('blink-settings=imagesEnabled=false')
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument('--proxy-server={0}'.format(proxy.proxy))
driver = webdriver.Chrome(options=chrome_options)
proxy.new_har("Google", options={'captureHeaders': True, 'captureContent': True})


driver.get("http://radiko.jp/#!/live/QRR")
driver.find_element_by_class_name("js-policy-accept").click()
time.sleep(5)
driver.find_element_by_class_name("play-radio").click()


def getUrl(result):
    m3u8 = None
    for entry in result['log']['entries']:
        url = entry['request']['url']
        if (url.find("medialist")!=-1):
            m3u8 = url
    return m3u8


def getm3u8(proxy):
    m3u8=None
    result = proxy.har
    if getUrl(result)!=None:
        m3u8=getUrl(result)
        return m3u8
    else:
        finish_time = datetime.datetime.now() + datetime.timedelta(minutes=2)
        while datetime.datetime.now() < finish_time:
            print("failed, try again")
            if m3u8 is None:
                driver.refresh()
                time.sleep(5)
                driver.find_element_by_class_name("play-radio").click()
                time.sleep(3)
                result = proxy.har
                m3u8 = getUrl(result)
            else:
                return m3u8

    

time.sleep(10)
m3u8 = getm3u8(proxy)
server.stop()


import subprocess
import os
path=os.getcwd()
os.chdir(path)

command="ffmpeg -i "+ "\""+ m3u8 +"\"" +" -c:a libmp3lame " + "\"" + filename + "\""
#command="ffmpeg -i "+ "\""+ m3u8 +"\"" +" -c copy -bsf:a aac_adtstoasc " + path  +"\\"+filename


now=datetime.datetime.now()
terminate_time = now + datetime.timedelta(seconds=int(terminate_time_delta))

p = subprocess.Popen(command, shell=True)

'''
while datetime.datetime.now() < terminate_time:
    pass
p.kill()
'''


