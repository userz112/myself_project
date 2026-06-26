import requests
from bs4 import BeautifulSoup
import csv

#　爬取房天下数据
def spider(url,city,target_file,cover=False):
    url = url
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    }

    data = requests.get(url, headers=header)

    bs_Data = BeautifulSoup(data.text, 'html.parser').body

    house_message = []

    city = city

    address_mes = bs_Data.find_all('p', class_='add_shop')
    address_mes_lis = [i.get_text().strip().split(' ',1) for i in address_mes]

    title = bs_Data.find_all('span', class_='tit_shop')
    title_lis = [i.get_text().replace(',', ' ') for i in title]

    mes = bs_Data.find_all('p', class_='tel_shop')
    mes_lis = [i.get_text().split('|') for i in mes]

    price = bs_Data.find_all('dd', class_='price_right')
    price_lis = [i.get_text() for i in price ]
    price_lis = [i.replace('万', ',').split(',') for i in price_lis]

    for i in range(len(title_lis)):
        house_structer = mes_lis[i][0]
        house_size = mes_lis[i][1]
        house_height = mes_lis[i][2]
        house_orientation = mes_lis[i][3]
        total_price = price_lis[i][0]
        unit_price = price_lis[i][1][:-3]
        house_message.append(f'{city},{address_mes_lis[i][0].replace(',','')},{address_mes_lis[i][1].replace(',','')},{title_lis[i].replace(',','')},{house_structer.strip().replace(',','')},{house_size.strip().replace(',','')},{house_height.strip().replace(',','')},{house_orientation.strip().replace(',','')},{total_price.strip()},{unit_price.strip()}')

    if cover:
        with open(target_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['城市','小区名称','地址','标题','户型','面积','高度','朝向','总价（万元）','单价（元/㎡）'])
            for i in house_message:
                writer.writerow(i.split(','))
        print(f'数据已覆盖到 {target_file}')
    else:
        with open(target_file, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for i in house_message:
                writer.writerow(i.split(','))
        print(f'数据已追加到 {target_file}')

beijing = ['https://esf.fang.com/','北京','house_message.csv']
shanghai = ['https://sh.esf.fang.com/','上海','house_message.csv']
guangzhou = ['https://gz.esf.fang.com/','广州','house_message.csv']
spider(guangzhou[0],guangzhou[1],guangzhou[2])
