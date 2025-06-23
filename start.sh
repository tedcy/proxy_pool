#!/usr/bin/env bash
echo "192.155.89.77 www.proxynova.com" >> /etc/hosts
echo "85.214.115.35 proxydb.net" >> /etc/hosts
echo "172.67.147.11 free-proxy-list.net" >> /etc/hosts
python proxyPool.py server &
python proxyPool.py schedule