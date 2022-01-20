FROM python:3.8
ENV DEBIAN_FRONTEND noninteractive
ENV TZ Asia/Shanghai
ADD . /srv/proxy_pool_lite
WORKDIR /srv/proxy_pool_lite
EXPOSE 11013

RUN mkdir /root/.pip
COPY ./pip.conf /root/.pip/pip.conf
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD [ "python", "cookie_engine.py" ]
