import socket

# ipv4        SOCK_DGRAM指定了这个Socket的类型是UDP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 绑定 客户端口和地址:
s.bind(('127.0.0.1', 9999))  # 绑定9999端口号
print('开始聊天了')
while True:
    # 接收数据 自动阻塞 等待客户端请求:
    data, addr = s.recvfrom(1024)  # 接收客户端发过来的数据和ip地址
    data = data.decode()
    # print('客户端的ip信息', addr)
    print(data)
    msg = input('你的回复：')  # 这个是咱们返回的数据
    s.sendto(msg.encode(), addr)  # 把数据发送给客户端
    # recvfrom()方法返回数据和客户端的地址与端口，这样，服务器收到数据后，直接调用sendto()就可以把数据用UDP发给客户端。
