# -*- coding: utf-8 -*-
# @Author: GXR
# @CreateTime: 2022-01-20
# @UpdateTime: 2022-01-20

import time

from apscheduler.schedulers.blocking import BlockingScheduler

import config
import cookie_api
import cookie_check
import cookie_refresh

scheduler_options = {
    "job_defaults": {
        # 积攒的任务只跑一次
        "coalesce": True,
        # 最大并发实例数
        "max_instances": 1,
        # 任务超时容错
        "misfire_grace_time": 30,
    },
    "timezone": "Asia/Shanghai",
}
scheduler = BlockingScheduler(**scheduler_options)

# 定时检查新cookie
scheduler.add_job(
    cookie_check.run_cookie_check,
    "interval",
    minutes=config.TIME_CHECK,
    id="cookie_check",
)

# 定时刷新可用cookie
scheduler.add_job(
    cookie_refresh.run_cookie_refresh,
    "interval",
    minutes=config.TIME_REFRESH,
    id="cookie_refresh",
)

# 定时重启API
scheduler.add_job(
    cookie_api.run_cookie_api,
    "cron",
    hour=time.localtime().tm_hour,
    minute=time.localtime().tm_min + 1,
    id="cookie_api",
)

scheduler.start()
