# cookie_pool_lite

## 一、下载安装

```shell
git clone https://gitee.com/guoxianru/cookie_pool_lite.git
```

## 二、项目配置

config.py 为配置文件，根据注释自行修改

## 三、启动项目

- 源码版

```shell
# 安装依赖
pip install -r requirements.txt
# 启动项目
nohup python cookie_pool_lite/cookie_engine.py >> cookie_pool_lite/cookie_pool_lite_`date +%Y-%m-%d_%H:%M:%S`.log 2>&1 &
```

- Docker版

```shell
docker-compose -f docker-compose.yml up -d --build
```
