from selenium import webdriver
import time
import requests
import cv2
from selenium.webdriver import ActionChains

driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://qzone.qq.com/")

# 切换到登陆的frame
driver.switch_to.frame(driver.find_element_by_xpath('//*[@id="login_frame"]'))

driver.find_element_by_xpath('//*[@id="switcher_plogin"]').click()

driver.find_element_by_xpath('//*[@id="u"]').send_keys("1241351234")
driver.find_element_by_xpath('//*[@id="p"]').send_keys("sdfgawedsaf")

driver.find_element_by_xpath('//*[@id="login_button"]').click()
driver.implicitly_wait(2)
driver.switch_to.frame(driver.find_element_by_xpath('//*[@id="tcaptcha_iframe"]'))

target = driver.find_element_by_xpath('//*[@id="slideBg"]')
template = driver.find_element_by_xpath('//*[@id="slideBlock"]')
response = requests.get(target.get_attribute("src"))
response2 = requests.get(template.get_attribute("src"))
with open("./lib/target.png", 'wb') as file:
    file.write(response.content)
with open("./lib/template.png", 'wb') as file:
    file.write(response2.content)


def findPic(target="./lib/target.png", template="./lib/template.png"):
    target_rgb = cv2.imread(target)
    target_gray = cv2.cvtColor(target_rgb, cv2.COLOR_RGB2GRAY)

    # 读取图片的位置
    template_rgb = cv2.imread(template, 0)

    # 匹配模块位置
    res = cv2.matchTemplate(target_gray, template_rgb, cv2.TM_CCOEFF_NORMED)

    value = cv2.minMaxLoc(res)
    return value[2][0]


x = findPic()
# 获取原图的宽度
img = cv2.imread("./lib/target.png")
w1 = img.shape[1]

# 获取网页图片的宽度
w2 = target.size["width"]
# 22*56/132
# 22 是待匹配图片的透明部分的宽度，56是网页待匹配图片的宽度，132是待匹配图片的宽度
x = x * w2 / w1
x = int(x + 9.3 - 32)

print(x)
# 获取鼠标
action = ActionChains(driver)
# 先按住模块
action.click_and_hold(template).perform()
# 拖动多少像素
action.move_by_offset(x, 0)
# 松开鼠标
action.release().perform()

time.sleep(3)
driver.close()
