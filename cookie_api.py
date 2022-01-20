# -*- coding: utf-8 -*-
# @Author: GXR
# @CreateTime: 2022-01-20
# @UpdateTime: 2022-01-20

import json

import redis
from flask import Flask

import config

app = Flask(__name__)
red = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=config.REDIS_DB,
    decode_responses=True,
)


# 功能列表
@app.route("/", methods=["GET"], strict_slashes=False)
def index():
    return {
        "/get_one": "获取一个cookie",
        "/get_all": "获取所有cookie",
        "/get_status": "cookie池状态",
    }


# 随机获取一个可用cookie
@app.route("/get_one", methods=["GET"], strict_slashes=False)
def get_one():
    try:
        cookie = json.loads(red.srandmember(config.REDIS_KEY_COOKIE))
        return {"code": 0, "cookie": cookie}
    except:
        return {"code": 1, "msg": "no cookie!"}


# 获取所有可用cookie
@app.route("/get_all", methods=["GET"], strict_slashes=False)
def get_all():
    try:
        cookie_list = []
        cookie_all = red.smembers(config.REDIS_KEY_COOKIE)
        for cookie in cookie_all:
            cookie_list.append(json.loads(cookie))
        return {"code": 0, "cookie": cookie_list}
    except:
        return {"code": 1, "msg": "no cookie!"}


# cookie池cookie数量统计
@app.route("/get_status", methods=["GET"], strict_slashes=False)
def get_status():
    try:
        status = {
            config.REDIS_KEY_COOKIE: red.scard(config.REDIS_KEY_COOKIE),
        }
        return {"code": 0, "status": status}
    except:
        return {"code": 1, "msg": "no status!"}


# 启动服务
def run_cookie_api():
    app.run(debug=False, host=config.API_HOST, port=config.API_PORT)


if __name__ == "__main__":
    run_cookie_api()
