# 安装docker

```
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
```

# docker镜像加速

```
https://www.coderjia.cn/archives/dba3f94c-a021-468a-8ac6-e840f85867ea#google_vignette
```

## 创建目录

```
sudo mkdir -p /etc/docker
```

## 写入配置文件

```
sudo tee /etc/docker/daemon.json <<-'EOF'
{
    "registry-mirrors": [
    	"https://docker.unsee.tech",
        "https://dockerpull.org",
        "docker.1panel.live",
        "https://dockerhub.icu"
    ]
}
EOF
```

## 重启docker服务

```
sudo systemctl daemon-reload && sudo systemctl restart docker# 创建目录
```

# 安装redis

```
yum install redis
```

修改/etc/redis.conf，修改绑定端口改成本地端口

# 安装proxy_pool

```
docker pull tedcy/proxy_pool
docker run -d --env DB_CONN=redis://x.x.x.x:6379/0 -p 5010:5010 tedcy/proxy_pool:latest
```

# 我的改动

改成了百度检测连接可用 

改成了动态配置生效，具体看settting.py

# 后期维护

官方项目只有12个代理，通过搜索https://github.com/search?q=%22def+freeProxy13%22+language%3APython&type=code&p=1来看看别人是怎么加代理的

或者https://github.com/jhao104/proxy_pool/forks根据star排序，看看别人怎么加代理的

或者在全部项目里面搜索“免费代理”，看看有没有最近更新过的http代理，例如https://github.com/parserpp/ip_ports

加完代理以后上传：

```
docker login
docker build -t tedcy/proxy_pool .
docker push tedcy/proxy_pool
```
