# -*- coding: utf-8 -*-
# @Author: GXR
# @CreateTime: 2021-08-01
# @UpdateTime: 2021-08-01

import json
import re
import time
import traceback

import redis
import requests
from loguru import logger
from retrying import retry
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

import config

red = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=config.REDIS_DB,
    decode_responses=True,
)


class CookieLogin:
    def __init__(self):
        # 接码平台账号密码
        self.dama_username = "clovy00"
        self.dama_password = "superkingc"
        # 接码平台验证码项目ID
        self.dama_project = "10767"
        # webdriver
        self.options = Options()
        self.options.add_experimental_option("useAutomationExtension", False)
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_argument(
            "User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
        )
        try:
            self.chromedriver_path = (
                r"/Users/dev123/.envs/python37_spider/bin/chromedriver"
            )
            self.browser = webdriver.Chrome(
                options=self.options, executable_path=self.chromedriver_path
            )
        except:
            self.browser = webdriver.Chrome(options=self.options)
        js_code = open("stealth.min.js", "r", encoding="utf-8").read()
        self.browser.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument", {"source": js_code}
        )
        self.browser.maximize_window()

    @retry
    def get_login(self):
        """登陆接码平台"""
        time.sleep(3)
        headers = {
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)",
            "Host": "103.219.36.30:8088",
        }
        data = {"uName": self.dama_username, "uPass": self.dama_password}
        res_apiid = requests.post(
            "http://103.219.36.30:8088/do.php?action=Login", headers=headers, data=data,
        )
        if res_apiid.status_code == 400:
            logger.error("接码平台登陆失败：400")
            return 400
        if res_apiid.status_code == 504:
            logger.error("接码平台登陆失败：504")
            return 504
        try:
            if res_apiid.json()["ret"] == 1:
                dama_apiid = res_apiid.json()["Data"]["pt_apiID"]
                logger.info(
                    "接码平台登陆成功：[%s]-[%s]" % (self.dama_username, self.dama_password)
                )
                return dama_apiid
            elif res_apiid.json()["msg"] == "账号或密码错误!":
                logger.error("接码平台登陆失败：账号密码错误")
                return 1
            else:
                logger.error("接码平台登陆失败：%s" % res_apiid.json()["msg"])
                return 0
        except:
            logger.error("接码平台登陆失败：%s" % traceback.format_exc())
            return 0

    @retry
    def get_money(self, dama_apiid):
        """接码平台余额"""
        time.sleep(3)
        res_money = requests.get(
            "http://www.cmddaaicheng.com:8088/api.php?action=getInfo&apiid=%s&pwd=%s"
            % (dama_apiid, self.dama_password),
        )
        if res_money.status_code == 400:
            logger.error("接码平台余额失败：400")
            return 400
        if res_money.status_code == 504:
            logger.error("接码平台余额失败：504")
            return 504
        try:
            dama_status = res_money.text.split("|")[0]
            if dama_status == "1":
                dama_money = res_money.text.split("|")[1].strip()
                logger.info("接码平台余额成功：%s" % dama_money)
                return dama_money
            else:
                logger.error("接码平台余额失败：%s" % res_money.text.split("|")[-1])
                return 0
        except:
            logger.error("接码平台余额失败：%s" % traceback.format_exc())
            return 0

    @retry
    def get_phone(self, dama_apiid):
        """获取接码平台手机号"""
        time.sleep(3)
        res_phone = requests.get(
            "http://www.cmddaaicheng.com:8088/api.php?action=getPhone&apiid=%s&pwd=%s&xmid=%s"
            % (dama_apiid, self.dama_password, self.dama_project),
        )
        if res_phone.status_code == 400:
            logger.error("获取接码平台手机号失败：400")
            return 400
        if res_phone.status_code == 504:
            logger.error("获取接码平台手机号失败：504")
            return 504
        try:
            dama_status = res_phone.text.split("|")[0]
            if dama_status == "1":
                dama_phone = res_phone.text.split("|")[1].strip()
                logger.info("获取接码平台手机号成功：%s" % dama_phone)
                return dama_phone
            else:
                logger.error("获取接码平台手机号失败：%s" % res_phone.text.split("|")[-1])
                return 0
        except:
            logger.error("获取接码平台手机号失败：%s" % traceback.format_exc())
            return 0

    @retry
    def get_code(self, dama_apiid, dama_phone):
        """接收接码平台验证码"""
        time.sleep(3)
        res_code = requests.get(
            "http://www.cmddaaicheng.com:8088/api.php?action=getCode&apiid=%s&pwd=%s&xmid=%s&hm=%s"
            % (dama_apiid, self.dama_password, self.dama_project, dama_phone),
        )
        if res_code.status_code == 400:
            logger.error("接收接码平台验证码失败：400")
            return 400
        if res_code.status_code == 504:
            logger.error("接收接码平台验证码失败：504")
            return 504
        try:
            dama_status = res_code.text.split("|")[0]
            if str(dama_status) == str(dama_phone):
                dama_code = re.findall(
                    "[0-9]{%s}" % config.CODE_COUNT, res_code.text.split("|")[-1]
                )[0].strip()
                logger.info("接收接码平台验证码成功：%s" % dama_code)
                return dama_code
            else:
                logger.error("接收接码平台验证码失败：%s" % res_code.text.split("|")[-1])
                return 0
        except:
            logger.error("接收接码平台验证码失败：%s" % traceback.format_exc())
            return 0

    @retry
    def lahei_phone(self, dama_apiid, dama_phone):
        """拉黑接码平台手机号"""
        time.sleep(3)
        res_lahei = requests.get(
            "http://www.cmddaaicheng.com:8088/api.php?action=addBlack&apiid=%s&pwd=%s&xmid=%s&hm=%s"
            % (dama_apiid, self.dama_password, self.dama_project, dama_phone),
        )
        if res_lahei.status_code == 400:
            logger.error("拉黑接码平台手机号失败：400")
            return 400
        if res_lahei.status_code == 504:
            logger.error("拉黑接码平台手机号失败：504")
            return 504
        try:
            dama_status = res_lahei.text.split("|")[0]
            if dama_status == "1":
                logger.info("拉黑接码平台手机号成功")
            else:
                logger.error("拉黑接码平台手机号失败：%s" % res_lahei.text.split("|")[-1])
        except:
            logger.error("拉黑接码平台手机号失败：%s" % traceback.format_exc())

    def cookie_login(self):
        while 1:
            try:
                # 登陆接码平台
                dama_apiid = self.get_login()
                if dama_apiid == 504:
                    raise
                if dama_apiid == 1:
                    raise
                if dama_apiid == 400:
                    continue
                if dama_apiid == 0:
                    continue
                # 获取账号余额
                dama_money = self.get_money(dama_apiid)
                if dama_money == 504:
                    continue
                if dama_money == 400:
                    continue
                if dama_money == 0:
                    continue
                # 获取接码平台手机号
                dama_phone = self.get_phone(dama_apiid)
                if dama_phone == 504:
                    continue
                if dama_phone == 400:
                    continue
                if dama_phone == 0:
                    continue
                # 打开登录页面
                self.browser.get("https://weibo.com/login.php")
                time.sleep(3)
                try:
                    # 点击短信登陆
                    WebDriverWait(self.browser, 10).until(
                        expected_conditions.presence_of_element_located(
                            (By.XPATH, '//*[@id="pl_login_form"]/div/div[1]/a')
                        )
                    ).click()
                    time.sleep(3)
                    # 输入接码平台手机号
                    WebDriverWait(self.browser, 10).until(
                        expected_conditions.presence_of_element_located(
                            (
                                By.XPATH,
                                '//*[@id="pl_login_form"]/div/div[4]/div[1]/div/input',
                            )
                        )
                    ).send_keys(dama_phone)
                    time.sleep(3)
                    # 点击获取验证码
                    WebDriverWait(self.browser, 10).until(
                        expected_conditions.presence_of_element_located(
                            (
                                By.XPATH,
                                '//*[@id="pl_login_form"]/div/div[4]/div[2]/a[1]',
                            )
                        )
                    ).click()
                    time.sleep(3)
                except:
                    logger.error("页面元素未找到")
                    self.browser.delete_all_cookies()
                    continue
                try:
                    # 验证码发送失败，手机号异常
                    WebDriverWait(self.browser, 5).until(
                        expected_conditions.presence_of_element_located(
                            (By.XPATH, "/html/body/div[3]/div/p/span[2]/a")
                        )
                    )
                    logger.error("验证码发送失败，手机号异常")
                    self.lahei_phone(dama_apiid, dama_phone)
                    self.browser.delete_all_cookies()
                    continue
                except:
                    # 接收接码平台验证码
                    code_time = int(time.time())
                    while 1:
                        dama_code = self.get_code(dama_apiid, dama_phone)
                        if dama_code != 504 and dama_code != 400 and dama_code != 0:
                            break
                        elif int(time.time()) - code_time > config.CODE_DELAY:
                            break
                        else:
                            time.sleep(3)
                            continue
                    if dama_code == 504:
                        self.lahei_phone(dama_apiid, dama_phone)
                        self.browser.delete_all_cookies()
                        continue
                    if dama_code == 400:
                        self.lahei_phone(dama_apiid, dama_phone)
                        self.browser.delete_all_cookies()
                        continue
                    if dama_code == 0:
                        self.lahei_phone(dama_apiid, dama_phone)
                        self.browser.delete_all_cookies()
                        continue
                    # 输入接码平台验证码
                    WebDriverWait(self.browser, 5).until(
                        expected_conditions.presence_of_element_located(
                            (
                                By.XPATH,
                                '//*[@id="pl_login_form"]/div/div[4]/div[2]/div/input',
                            )
                        )
                    ).send_keys(dama_code)
                    time.sleep(3)
                    # 点击登陆按钮
                    WebDriverWait(self.browser, 5).until(
                        expected_conditions.presence_of_element_located(
                            (By.XPATH, '//*[@id="pl_login_form"]/div/div[4]/div[4]/a')
                        )
                    ).click()
                    time.sleep(3)
                    try:
                        # 登陆失败，出现身份验证
                        WebDriverWait(self.browser, 5).until(
                            expected_conditions.presence_of_element_located(
                                (By.XPATH, "/html/body/div[2]/div/h1")
                            )
                        )
                        logger.error("登陆失败，出现身份验证")
                        self.lahei_phone(dama_apiid, dama_phone)
                        self.browser.delete_all_cookies()
                        continue
                    except:
                        try:
                            # 登陆失败，出现账号异常
                            WebDriverWait(self.browser, 5).until(
                                expected_conditions.presence_of_element_located(
                                    (
                                        By.XPATH,
                                        "/html/body/div[1]/div/div[2]/div/div/div[1]/em",
                                    )
                                )
                            )
                            logger.error("登陆失败，出现账号异常")
                            self.lahei_phone(dama_apiid, dama_phone)
                            self.browser.delete_all_cookies()
                            continue
                        except:
                            # 登陆成功，获取浏览器cookie
                            cookie = self.browser.get_cookies()
                            cookie = {i["name"]: i["value"] for i in cookie}
                            logger.info("获取cookie +1")
                            self.browser.close()
                            self.browser.quit()
                            return cookie
            except:
                logger.error("模拟登陆异常：%s" % traceback.format_exc())
                time.sleep(600)
                self.browser.delete_all_cookies()
                continue


def run_cookie_login(count):
    cl = CookieLogin()
    for i in range(count):
        cookie = cl.cookie_login()
        red.sadd(
            config.REDIS_KEY_COOKIE, json.dumps(cookie, ensure_ascii=False),
        )


if __name__ == "__main__":
    run_cookie_login(1)
