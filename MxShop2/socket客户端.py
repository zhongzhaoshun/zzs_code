import socket

'''
客户端使用UDP时，首先仍然创建基于UDP的Socket，然后不需要连接，直接通过sendto()给服务器发数据：
'''
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print('开始聊天了')
while True:
    data = input()
    # 发送数据:
    s.sendto(data.encode(), ('127.0.0.1', 9999))
    recv = s.recv(1024)  # 返回的数据
    print(recv.decode())
# 接收数据:
s.close()
