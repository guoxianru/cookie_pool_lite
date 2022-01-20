# -*- coding: utf-8 -*-
# @Author: GXR
# @CreateTime: 2022-01-20
# @UpdateTime: 2022-01-20

import redis
from loguru import logger

import config
import cookie_login

red = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=config.REDIS_DB,
    decode_responses=True,
)


# 刷新cookie数量
def cookie_refresh():
    logger.info("开始检查cookie数量")
    while 1:
        cookie_list = red.smembers(config.REDIS_KEY_COOKIE)
        if len(cookie_list) >= config.COOKIE_COUNT:
            break
        cookie_login.run_cookie_login(1)
    logger.info("cookie数量正常[%s]" % len(cookie_list))


def run_cookie_refresh():
    cookie_refresh()


if __name__ == "__main__":
    run_cookie_refresh()
