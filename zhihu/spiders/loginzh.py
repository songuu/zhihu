# -*- coding: utf-8 -*-
import json
from PIL import Image
import scrapy
import time
from scrapy import Request, FormRequest
from bs4 import BeautifulSoup
import re
class LoginzhSpider(scrapy.Spider):
    name = 'loginzh'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://zhihu.com/']
    captcha_path = '1.gif'
    xsrf=''
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
    }
    EMAIL = 'your email'
    PASSWORD = 'your password'

    def start_requests(self):
        timestamp = str(int(time.time()))
        type = 'login'
        lang = 'en'
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=%s&type=%s&lang=%s' % (timestamp, type, lang)
        print(captcha_url)
        yield Request(url = captcha_url, headers = self.headers, callback = self.parse_captcha)

    #验证码解析
    def parse_captcha(self, response):
        yield Request(url = 'http://www.zhihu.com/explore',callback=self.get_xsrf)
        with open(self.captcha_path, 'wb') as f:
            f.write(response.body)
            f.close()

        im = Image.open(self.captcha_path)
        im.show()
        im.close()
        captcha = input("input the captcha with quotation mark\n>")
        yield Request(url = 'https://www.zhihu.com/', callback = self.login, meta = {'captcha':captcha})
    #解析xsrf
    def get_xsrf(self,response):
        html = response.text
        BS = BeautifulSoup(html, 'html.parser')
        xsrf_input = BS.find(attrs={'name': '_xsrf'})
        pattern = r'value=\"(.*?)\"'
        self.xsrf = re.findall(pattern, str(xsrf_input))[0]
        print("获取到xsrf:" + str(self.xsrf))
    #只模拟了邮箱登录
    def login(self, response):
        login_url = 'https://www.zhihu.com/login/email'#重点重定向地址
        yield FormRequest(url = login_url,
                          method = 'POST',
                          formdata = {
                              'captcha_type': 'en',
                              'email': self.EMAIL,
                              'password':self.PASSWORD,
                              '_xsrf': self.xsrf,
                              'captcha_type': 'en',
                              'captcha': response.meta['captcha'],
                            },
                            callback = self.after_login,
                            )

    def after_login(self,response):
        json_data = json.loads(response.text)
        print(json_data)
        yield Request(url='https://www.zhihu.com/settings/account', callback=self.login_test)

    def login_test(self, response):
        print(response.text)
