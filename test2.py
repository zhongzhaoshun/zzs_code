import os
import time
import time

# def get_files():
now_time = time.strftime("%m%d")
print(now_time)
file_path = r'C:\Users\Administrator\Desktop\广东电信的成员使用记录{}.xlsx'.format(now_time)
print(file_path)
wait_time = 5
for i in range(30):
    file_exists = os.path.exists(file_path)
    if file_exists:
        print('文件已存在')
        # return True
        break
    else:
        print("文件不存在，等待{}秒".format(wait_time))
        time.sleep(wait_time)
        # return False
        continue
