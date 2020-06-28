import requests
import re
import urllib
import download_file
from bs4 import BeautifulSoup
import selenium
import math
import time
import threading
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


start_time = time.time()

class House:
    #driver = webdriver.Chrome(executable_path=r"C:\Users\731ru\Downloads\chromedriver\chromedriver.exe")
    def __init__(self, link):
        self.link = link
        self.get_atribute()

    def get_atribute(self):
        res = urllib.request.urlopen(self.link).read().decode("utf-8")
        self.check_captcha(res)
        self.soup = BeautifulSoup(res, 'html.parser')
        self.address = self.soup.find(class_="a10a3f92e9--geo--18qoo").span.get("content")#вытаскиваем адрес
        info = self.soup.find_all(class_="a10a3f92e9--info-value--18c8R")#находим информацию про этаж
        self.floor, self.max_floor = self.get_floor("(\d{1,10}) из (\d{1,10})", info)# ищем этаж
        self.square = int(float(self.checking(info[0], "text","")[:-3].replace(",", ".")))#Находим общую площадь*
        self.room = re.search("(\d{1,10})-комн.",self.soup.find(class_="a10a3f92e9--title--2Widg").text).group(1)#Кол-во комнат
        self.repairs = self.checking(self.soup.find(class_="a10a3f92e9--value--3Ftu5"),"text", "")#ремонт
        self.price = int(self.checking(self.soup.find(itemprop="price"), "", "content")[:-1].replace(" ", ""))#Стоимость*
        self.one_price = self.checking(self.soup.find(class_="a10a3f92e9--price_per_meter--hKPtN a10a3f92e9--price_per_meter--residential--1mFDW"),"text", "")[:-4]#Цена за кв. метр
        #self.ten_watches, self.data_create = self.get_watch()#за 10 дней и дата создания
        self.all_watches = re.search("(\d{1,10}) просмо", self.soup.find(class_="a10a3f92e9--link--1t8n1 a10a3f92e9--link--2mJJk").text).group(1)  # всего просмотров
        self.type = self.checking(self.soup.find(class_="a10a3f92e9--vas_item--2wQfE"), "text", "")#тип размещения
        self.first_price = self.get_first_price()#первоначальная цена*
        self.district = self.get_district()#получение р-н
        self.underground = self.get_underground()#метро
        self.type_of_house = self.checking(self.soup.find(class_="a10a3f92e9--value--3Ftu5"),"text", "")#тип дома
        self.result = [self.link, self.address, self.floor, self.max_floor, self.square, self.room, self.repairs, self.price,
                       self.one_price, self.all_watches, self.type,self.first_price, self.district, self.underground,
                       self.type_of_house] #self.ten_watches, self.data_create]
        #print(self.result)

    def check_captcha(self,res):
        if 'id="form_captcha"' in res:
            print("\nCAPTCHA\n")
            exit(0)
    def write_file(self, number, name):
        first_line = ["Ссылка","Адрес", "Этаж", "Всего этажей", "Площадь","Кол-во комнат","Ремонт","Стоимость","Цена за кв. м.","Всего Просмотров",
                      "Тип объявления","Первоначальная цена","Район","Метро","Тип дома","Просмотры за 10 дней", "Дата создания"]
        if number == 0:
            write = "w"
        else:
            write = "a"
        with open(name, write, newline="") as file:
            writer = csv.writer(file)
            if write == "w":
                writer.writerow(first_line)
            writer.writerow(self.result)

    def checking(self, result, text, get):  # Проверка что там находится не None
        if result == None:
            return "Не указано"
        elif text:
            return result.text
        elif get:
            return result.get(get)
        return "Не указано"

    def get_watch(self):
        self.driver.get(self.link)
        elem = self.driver.find_element_by_class_name("a10a3f92e9--link--1t8n1")
        elem.click()
        time.sleep(1)
        place = self.driver.find_element_by_class_name("a10a3f92e9--information--AyP9e").text
        return (re.search("(\d{1,10}) .* за последние 10 дней",place).group(1), re.search("\d{1,2}.\d{1,2}.\d{1,2}",place).group(0))#за 10 дней и дата создания
    def get_first_price(self):
        div = self.soup.find(class_="a10a3f92e9--container--3jr-Q")
        if div == None:
            return "Не указано"
        else:
            return div.find_all(class_="a10a3f92e9--event-price--BxH3c")[-1].text[:-1]
    def get_district(self):#получение района
        address = self.soup.find_all(class_="a10a3f92e9--link--1t8n1 a10a3f92e9--address-item--1clHr")
        if address == None:
            return "Не указано"
        for i in range(len(address)):
            if "р-н" in address[i].text:
                return address[i].text
    def get_underground(self):
        result = ""
        unders = self.soup.find_all(class_="a10a3f92e9--underground_link--AzxRC")
        if unders != None:
            for i in range(len(unders)):
                result += unders[i].text + ","
        return result
    def get_floor(self, pattern, info):
        for i in range(len(info)):
            result = re.search(pattern, info[i].text)
            if result != None:
                return (int(result.group(1)),int(result.group(2)))
        return "Не указано"
    def close(self):
        self.driver.close()

def read_file(name):
  with open(name, 'br') as file:
    return str(file.read(),encoding="utf-8")



def downloa(url):#Скачиваем страницы попробовать не скачивать а сразу читать
    pages_number_list = []
    i = 1
    while 1:
        if i == 1:
            download_file.download_file(url, "files/index" + str(i) + ".html")
            i = i + 1
            continue
        if i==2:
            url = url + "&p=" + str(i)
        else:
            url = url.replace("&p="+str(i-1),"&p="+str(i))

        res = urllib.request.urlopen(url).read().decode("utf-8")
        soup = BeautifulSoup(res, 'html.parser')
        pages_count = int(soup.find(class_="_93444fe79c--list-item--active--3dOSi").span.text)
        print(pages_count)
        if pages_count == 1:
            print("now we break")
            break
        pages_number_list.append(pages_count)
        download_file.download_file(url, "files/index" + str(i) + ".html")
        i += 1
    print(pages_number_list)
    return pages_number_list[-1]

url = "https://kazan.cian.ru/cat.php?deal_type=sale&engine_version=2&foot_min=45&metro%5B0%5D=319&offer_type=flat&only_foot=2&region=4777&room3=1&room4=1"
url = "https://kazan.cian.ru/cat.php?deal_type=sale&engine_version=2&foot_min=45&metro%5B0%5D=316&metro%5B1%5D=317&metro%5B2%5D=318&metro%5B3%5D=319&metro%5B4%5D=320&metro%5B5%5D=321&object_type%5B0%5D=2&offer_type=flat&only_foot=2&room1=1&room2=1"


#number = download_pages(url)


def get_link(soup):#получает список ссылок

    list_of_flat = soup.find_all(class_="c6e8ba5398--header--1fV2A")
    links = [_ for _ in range(len(list_of_flat))]
    for i in range(len(list_of_flat)):
        links[i] = list_of_flat[i].get('href')
    print(links)
    return links

def download_pages(url):
    pages_number_list = []
    i = 1
    flats = []
    while 1:
        if i==2:
            url = url + "&p=" + str(i)
        else:
            url = url.replace("&p="+str(i-1),"&p="+str(i))
        res = urllib.request.urlopen(url).read().decode("utf-8")
        soup = BeautifulSoup(res, 'html.parser')
        pages_count = int(soup.find(class_="_93444fe79c--list-item--active--3dOSi").span.text)
        if i == 1:
            flats.append(get_link(soup))
            i = i + 1
            continue

        print(pages_count)
        if pages_count == 1 or pages_count == 3:
            print("now we break i - ", pages_count)
            break
        #flats.append(get_link(soup))
        i += 1

    return flats

def get_flats():#Находим на каждой странице квартиры
    flats = [i for i in range(number)]
    k = 0
    for i in range(number):
        print("files/index"+str(i+1)+".html")
        soup = BeautifulSoup(read_file("files/index"+str(i+1)+".html"), 'html.parser')
        flats[i] = soup.find_all(class_='_93444fe79c--card--_yguQ')
        k +=1
    return flats

#flats = get_flats()
flats = download_pages(url)
print("Найдено объявлений ", (len(flats)-1)*len(flats[0])+len(flats[-1]))


objects = []
k = 0


for i in range(len(flats)):
    #if i == 1:
       # break
    for j in range(len(flats[i])):
            #if j == 10:
             #   break
        try:
            k += 1
            print(k)
            house = House(flats[i][j])
            objects.append(house)
            #if i==len(flats)-1 and j==len(flats[i])-1:
                #house.close()
        except Exception as e:
            print("\n\n It was error: " + str(e) + " \n\n")
            continue



objects = sorted(objects,key= lambda object: (object.floor, object.square, object.price))

for i in range(len(objects)):
    objects[i].write_file(i, "result_sort.csv")

print("\n", time.time() - start_time)
exit(0)