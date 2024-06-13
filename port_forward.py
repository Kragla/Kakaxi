from sshtunnel import SSHTunnelForwarder
import time
from client.settings import PORT_FORWARD
import logging

# 启用调试日志
logging.basicConfig(level=logging.DEBUG)

jump_server_host = PORT_FORWARD['jumpServer']['host']
jump_server_port = PORT_FORWARD['jumpServer']['port']
jump_server_username = PORT_FORWARD['jumpServer']['username']
jump_server_password = PORT_FORWARD['jumpServer']['password']
rules = PORT_FORWARD['rules']

# 暂时只转发第一个规则
forwardings = []
for rule in rules:
    addrs = rule.split('->')
    local_addr = addrs[0].strip()
    local_addr_arr = local_addr.split(':')
    local_bind_ip = local_addr_arr[0].strip()
    local_bind_port = int(local_addr_arr[1].strip())

    dest_addr = addrs[1].strip()
    dest_addr_arr = dest_addr.split(':')
    dest_bind_ip = dest_addr_arr[0].strip()
    dest_bind_port = int(dest_addr_arr[1].strip())

    forwardings.append((local_bind_ip, local_bind_port, dest_bind_ip, dest_bind_port))

dest_address_list = [(dest_bind_ip, dest_bind_port) for (_, _, dest_bind_ip, dest_bind_port) in forwardings]
local_address_list = [(local_bind_ip, local_bind_port) for (local_bind_ip, local_bind_port, _, _) in forwardings]

with SSHTunnelForwarder(
        (jump_server_host, jump_server_port),  # 跳板机（堡垒机）B配置
        ssh_password=jump_server_password,
        ssh_username=jump_server_username,
        remote_bind_addresses=dest_address_list,
        local_bind_addresses=local_address_list) as tunnel:  # 数据库存放服务器C配置
            print(f"SSH隧道建立成功: ")
            print(rules)

            # 开启隧道
            tunnel.start()

            # 阻塞程序
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("隧道关闭中...")
