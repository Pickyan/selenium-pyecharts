# coding=utf-8
import pymysql
from pyecharts import Geo,Page

def create_charts():
    page = Page()
    data = get_data()

    chart = Geo("python招聘分布", "data from 拉勾网")
    attr, value = chart.cast(data)
    chart.add("", attr, value, type="heatmap", is_visualmap=True,
              visual_range=[0, 180], visual_text_color='white',
              is_legend_show=False)
    page.add(chart)
    page.render()

def get_data():
    conn = pymysql.connect(host="127.0.0.1",user='root',password='root',database='lagou',port=3306)
    cursor = conn.cursor()
    sql = """select city ,count(1) from lagou_python group by city"""

    cursor.execute(sql)
    aa = cursor.fetchall()
    data = []
    for x in aa:
        if "海外" not in x[0]:
            data.append(x)
    conn.close()
    print(data)
    return data

if __name__ == '__main__':
    create_charts()