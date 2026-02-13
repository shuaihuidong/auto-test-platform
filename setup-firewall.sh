#!/bin/bash
# 防火墙配置脚本
# 用于开放测试平台所需的端口

echo "=== 配置防火墙规则 ==="

# 开放80端口 (HTTP/前端)
if ! iptables -C INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null; then
    iptables -I INPUT -p tcp --dport 80 -j ACCEPT
    echo "✓ 已开放80端口"
else
    echo "✓ 80端口已开放"
fi

# 开放443端口 (HTTPS)
if ! iptables -C INPUT -p tcp --dport 443 -j ACCEPT 2>/dev/null; then
    iptables -I INPUT -p tcp --dport 443 -j ACCEPT
    echo "✓ 已开放443端口"
else
    echo "✓ 443端口已开放"
fi

# 开放8000端口 (后端API - 直连)
if ! iptables -C INPUT -p tcp --dport 8000 -j ACCEPT 2>/dev/null; then
    iptables -I INPUT -p tcp --dport 8000 -j ACCEPT
    echo "✓ 已开放8000端口"
else
    echo "✓ 8000端口已开放"
fi

# 开放5672端口 (RabbitMQ)
if ! iptables -C INPUT -p tcp --dport 5672 -j ACCEPT 2>/dev/null; then
    iptables -I INPUT -p tcp --dport 5672 -j ACCEPT
    echo "✓ 已开放5672端口"
else
    echo "✓ 5672端口已开放"
fi

# 保存规则
mkdir -p /etc/iptables
iptables-save > /etc/iptables/rules.v4
echo "✓ 防火墙规则已保存到 /etc/iptables/rules.v4"

echo ""
echo "=== 当前防火墙规则 ==="
iptables -L INPUT -n --line-numbers | grep -E "80|443|8000|5672"

echo ""
echo "配置完成！"
