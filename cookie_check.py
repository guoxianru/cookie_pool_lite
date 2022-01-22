# -*- coding: utf-8 -*-
# @Author: GXR
# @CreateTime: 2022-01-20
# @UpdateTime: 2022-01-20

import json

import redis
import requests
from retrying import retry

import config
from cookie_api import app

red = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=config.REDIS_DB,
    decode_responses=True,
)


@retry
def get_response(cookie):
    config.HEADERS.update(
        {
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            "sec-ch-ua-mobile": "?0",
            "dnt": "1",
            "upgrade-insecure-requests": "1",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "accept-language": "zh-CN,zh;q=0.9",
        }
    )
    response = requests.get(
        config.COOKIE_CHECK_URL, headers=config.HEADERS, cookies=json.loads(cookie)
    )
    if (
        "pl_common_sassfilter" in response.text
        or "login" in response.url
        or "captcha" in response.url
        or "passport" in response.url
    ):
        return 0
    elif response.status_code not in [
        300,
        301,
        305,
        400,
        401,
        402,
        403,
        404,
        405,
        406,
        407,
        408,
        429,
        450,
        500,
        501,
        502,
        503,
        504,
    ]:
        return 1
    else:
        return 0


# 检查cookie可用性
def cookie_check():
    cookie_list = red.smembers(config.REDIS_KEY_COOKIE)
    for cookie in cookie_list:
        response = get_response(cookie)
        if response == 1:
            app.logger.info("[可用cookie]-[+1]")
        else:
            red.srem(config.REDIS_KEY_COOKIE, cookie)
            app.logger.error("[删除cookie]-[+1]")


def run_cookie_check():
    cookie_check()


if __name__ == "__main__":
    run_cookie_check()
