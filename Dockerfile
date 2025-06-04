FROM python:3.8-alpine

MAINTAINER tedcy <yue.cheng.ted@gmail.com>

WORKDIR /app

COPY ./requirements.txt .

# apk repository
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories

# timezone
RUN apk add -U tzdata && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && apk del tzdata

# runtime environment
RUN apk add musl-dev gcc libxml2-dev libxslt-dev vim && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del gcc musl-dev

COPY . .

RUN echo "set mouse=" >> /root/.vimrc \
    && echo "syntax on" >> /root/.vimrc \
    && echo "set number" >> /root/.vimrc \
    && echo "set encoding=utf-8" >> /root/.vimrc

EXPOSE 5010

ENTRYPOINT [ "sh", "start.sh" ]
