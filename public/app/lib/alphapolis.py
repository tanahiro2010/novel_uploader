import time
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

class AlphaplisData:
    def __init__(self):
        self.url = 'https://ncode.syosetu.com/{}/{}'
        self.api_url = 'https://api.syosetu.com/novelapi/api/'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0"
        })

        return