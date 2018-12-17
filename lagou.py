# coding=utf-8
from selenium import webdriver
from lxml import etree
import re
import pymysql


class Lagou:
    def __init__(self):
        self.base_url = "https://www.lagou.com/jobs/list_python?px=default&city=%E5%85%A8%E5%9B%BD#filterBox"
        self.driver_path = "D:\Program\chromedriver.exe"
        self.driver = webdriver.Chrome(executable_path=self.driver_path)
        self.conn = pymysql.connect(host="127.0.0.1",user='root',password='root',database='lagou',port=3306)
        self.cursor = self.conn.cursor()

    # 分析页面  获取目标数据
    def parse_page(self,html):
        element = etree.HTML(html)
        lis = element.xpath("//div[@id='s_position_list']/ul[@class='item_con_list']/li")
        for li in lis:
            company_name = li.xpath(".//div[@class='company_name']/a/text()")[0]
            job_name = li.xpath(".//h3/text()")[0]
            address = li.xpath(".//em/text()")[0]
            if "·" in address:
                city = re.search(".*(?=\·)",address).group()
            else:
                city = address
            money = li.xpath(".//div[@class='li_b_l']/span[@class='money']/text()")[0]
            min_money = re.match("\d*",money).group()
            if "-" in money:
                max_money = re.search("(?<=-)\d*(?=k|K)",money).group()
            else:
                max_money = min_money
            industry = li.xpath(".//div[@class='industry']/text()")[0].strip()
            Financing = re.search("(?<=/).*(?=/)",industry).group().strip()
            data = {
                "company_name":company_name,
                "job_name":job_name,
                "city":city,
                "min_money":min_money,
                "max_money":max_money,
                "Financing":Financing
            }
            #保存数据
            self.sava_data(data)

    def sava_data(self,data):
        company_name = data["company_name"]
        job_name = data["job_name"]
        city = data["city"]
        min_money = data["min_money"]
        max_money = data["max_money"]
        Financing = data["Financing"]
        sql = """
        insert into lagou_python (id,company_name,job_name,city,min_money,max_money,Financing) values(null,%s,%s,%s,%s,%s,%s)
        """
        self.cursor.execute(sql,[company_name,job_name,city,min_money,max_money,Financing])
        self.conn.commit()

    def run(self):
        # 1.用selenium通过base_url获取第一页的html
        self.driver.get(self.base_url)
        while True:
            html = self.driver.page_source
            # 2.分析页面 获取目标数据
            self.parse_page(html)
            # 页面跳转
            next_button = self.driver.find_element_by_class_name("pager_next")
            if "pager_next_disabled" in next_button.get_attribute("class"):
                break
            next_button.click()
            page = self.driver.find_element_by_class_name("pager_is_current")
            page_num = page.get_attribute("page")
            print("跳转到第%s页。\n"%page_num,"------"*20)
        self.conn.close()


if __name__ == '__main__':
    lagou = Lagou()
    lagou.run()