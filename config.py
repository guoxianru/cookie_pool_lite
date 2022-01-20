# -*- coding: utf-8 -*-
# @Author: GXR
# @CreateTime: 2022-01-20
# @UpdateTime: 2022-01-20

# Redis设置
REDIS_HOST = "redis"
REDIS_PORT = "6379"
REDIS_DB = "0"
REDIS_PASSWORD = "123456"

# 代理池API设置
API_HOST = "0.0.0.0"
API_PORT = "22001"

# cookie池Redis-key
REDIS_KEY_COOKIE = "weibo_cookie"

# 验证码位数
CODE_COUNT = 6

# 验证码等待时间(秒)
CODE_DELAY = 30

# cookie池数量
COOKIE_COUNT = 5

# 检查cookie可用性时间周期(分)
TIME_CHECK = 10

# 检查cookie数量时间周期
TIME_REFRESH = 30

# 通用请求头
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}

# 测试cookie网站
COOKIE_CHECK_URL = "https://s.weibo.com/weibo?q=小米&page=2"
