"""12306抢票功能初步实现"""
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class Grab_Votes(object):

    def __init__(self):
        self.login_url = "https://kyfw.12306.cn/otn/login/init"
        self.initmy_url = "https://kyfw.12306.cn/otn/index/initMy12306"
        self.search_url = "https://kyfw.12306.cn/otn/leftTicket/init"
        self.passengers_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        self.driver = webdriver.Chrome(executable_path="E:\Program Files\chromedriver.exe")

    def wait_input(self):
        # 所有文本和时间必须和12306保持一致
        self.from_station = input("出发地：")
        self.to_station = input("目的地：")
        self.depart_time = input("出发时间：")
        self.passengers = input("乘客姓名(如有多个乘客，用英文逗号隔开)：").split(",")
        self.trains = input("车次(如果有多个车次，用英文逗号隔开):").split(",")

    def _login(self):
        self.driver.get(self.login_url)
        # 检测是否登录
        WebDriverWait(self.driver, 1000).until(
            # 是否等于我的登录地址
            EC.url_to_be(self.initmy_url)
        )
        print("登录成功!")

    def _order_ticket(self):
        # 跳转到查询余票的页面
        self.driver.get(self.search_url)
        # 等待输入出发地
        WebDriverWait(self.driver, 1000).until(
            EC.text_to_be_present_in_element_value((By.ID, "fromStationText"), self.from_station)
        )
        # 等待输入目的地
        WebDriverWait(self.driver, 1000).until(
            EC.text_to_be_present_in_element_value((By.ID, "toStationText"), self.to_station)
        )
        # 等待出发日期是否输入正确
        WebDriverWait(self.driver, 1000).until(
            EC.text_to_be_present_in_element_value((By.ID, "train_date"), self.depart_time)
        )

    def loop_detection(self):
        # 等待查询按钮是否可用
        WebDriverWait(self.driver, 1000).until(
            EC.element_to_be_clickable((By.ID, "query_ticket"))
        )
        # 如果能够点击了，那么就找到这个按钮，执行点击事件
        searchBtn = self.driver.find_element_by_id("query_ticket")
        searchBtn.click()
        # 等待点击查询按钮以后，车次信息是否显示出来
        WebDriverWait(self.driver, 1000).until(
            EC.presence_of_element_located((By.XPATH, ".//tbody[@id='queryLeftTable']/tr"))
        )
        # 找到所有没有datatran属性的标签，这些标签存储了车次信息
        tr_list = self.driver.find_elements_by_xpath(".//tbody[@id='queryLeftTable']/tr[not(@datatran)]")
        # 遍历所有满足条件的tr标签
        for tr in tr_list:
            train_number = tr.find_element_by_class_name("number").text
            if train_number in self.trains:
                left_ticket_td = tr.find_element_by_xpath(".//td[4]").text
                if left_ticket_td == "有" or left_ticket_td.isdigit:
                    orderBtn = tr.find_element_by_class_name("btn72")
                    orderBtn.click()
                    # 等待是否来到了确认乘客的页面
                    WebDriverWait(self.driver, 1000).until(
                        EC.url_to_be(self.passengers_url)
                    )
                    print("确认来到乘客页面")
                    # 等待checkbox是否显示出来
                    WebDriverWait(self.driver, 1000).until(
                        EC.presence_of_element_located((By.XPATH, ".//ul[@id='normal_passenger_id']//input"))
                    )
                    # 获取当前买票人信息
                    username = self.driver.find_element_by_xpath(".//ul[@id='normal_passenger_id']").text
                    # 如果核对正确就选择打钩
                    if username in self.passengers:
                        checkbox_Btn = self.driver.find_element_by_id("normalPassenger_0")
                        checkbox_Btn.click()
                        # 等待提交按钮显示
                        WebDriverWait(self.driver, 1000).until(
                            EC.element_to_be_clickable((By.ID, "submitOrder_id"))
                        )
                        submitBtn = self.driver.find_element_by_id("submitOrder_id")
                        submitBtn.click()
                        time.sleep(1)
                        # 等待再次确认显示
                        WebDriverWait(self.driver, 1000).until(
                            EC.element_to_be_clickable((By.ID, "qr_submit_id"))
                        )
                        time.sleep(1)
                        qr_submitBtn = self.driver.find_element_by_id("qr_submit_id")
                        qr_submitBtn.click()
                else:
                    self.loop_detection()

    def run(self):
        self.wait_input()
        self._login()
        self._order_ticket()
        self.loop_detection()


if __name__ == '__main__':
    spider = Grab_Votes()
    spider.run()