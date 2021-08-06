from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager

from forex_python.converter import CurrencyRates
import math

from songline import Sendline

token = 'pIqoRxZzDneaxmfYr6oQlMYN8MoKCtNSBbSefEMs2uE' 
messenger = Sendline(token)

import hashlib
import hmac
import json
import requests
from time import time, sleep
from datetime import datetime

api_key = 'BfdjwoRufZ8xsuY8rXX0MqAWEZDzckRvUuXf3LRonjH0UrkBI9BVDhLi355T6DzU'
api_secret = 'IS64xcIututvwMoZKPvTgGIlX7SPzv1vbtzoOhDHcIRMP8LRUELCvUqt8onNJ9dp '
client = Client(api_key, api_secret)
c = CurrencyRates()
# API ของ Biannce 

# API ของ Bitkub 
API_HOST = 'https://api.bitkub.com'
API_KEY = ''
API_SECRET = b''

def json_encode(data):
    	return json.dumps(data, separators=(',', ':'), sort_keys=True)

def sign(data):
	j = json_encode(data)
	# print('Signing payload: ' + j)
	h = hmac.new(API_SECRET, msg=j.encode(), digestmod=hashlib.sha256)
	return h.hexdigest()

# check server time
response = requests.get(API_HOST + '/api/servertime')
ts = int(response.text)
# print('Server time: ' + response.text)

# check balances
header = {
	'Accept': 'application/json',
	'Content-Type': 'application/json',
	'X-BTK-APIKEY': API_KEY,
}
data = {
	'ts': ts,
}
signature = sign(data)
data['sig'] = signature

#ส่วนที่ห้ามยุ่งของ Bitkub จบที่ตรงนี้ 

prices = client.get_all_tickers()
depth = client.get_order_book(symbol='BNBUSDT')
rate_bath = c.get_rate('USD', 'THB')
# print (rate_bath) 


def ticker(coin = 'THB_BNB', variable = 'highestBid'): #หาราคาต่าง ๆ ของคู่เหรียญที่เราต้องการบอกราคาล่าสุด สูง ต่ำ เปอร์ที่เปลี่ยนแปลง 
    response = requests.get(API_HOST + '/api/market/ticker',params='sym='+coin) 
    responseJson = json.loads(response.text) #ต้องใช้ Load เพื่อให้สามารถเอาตัวแปรเข้ามาใช้งานได้จริง 
    result = ''
    if (variable == ''):
        result = responseJson[coin]
    else:
        result = responseJson[coin][variable]
   #  print (result)
    return result


mycoin = ['BNBUSDT'] #สามารถใส่ , เพื่อใส่คู่เหรียญอื่นที่ต้องการได้ 
for p in prices:
      for c in mycoin:
        sym = c
        if p['symbol'] == sym:
            print(p)
            pc = float(p['price'])
            print ("ราคา BNB ที่ Binance คือ",pc,'ดอลลาร์')
            biannce_thai_rate = pc * rate_bath
            print ("ราคา BNB ที่ Binance คือ",biannce_thai_rate,"บาท")

   
bnb_bitkub_rate = ticker()
print ("ราคา BNB ที่ Bitkub คือ",bnb_bitkub_rate,"บาท") 
result_bath = bnb_bitkub_rate - biannce_thai_rate
print ("ส่วนต่างระหว่าง 2 เว็บเทรดคือ :",result_bath,"บาท")
result_percentage = (((bnb_bitkub_rate - biannce_thai_rate)/biannce_thai_rate)*100)
print ("ส่วนต่างระหว่าง 2 เว็บเทรดคือ :",result_percentage,"%")
line_result_percentage = "ส่วนต่างระหว่าง 2 เว็บเทรดคือ :",result_percentage,"%"

if result_percentage >= 5:
    print('สามารถทำ Abritage ได้')
    # messenger.sendtext(line_result_percentage)
    messenger.sendtext("ทำได้")

elif result_percentage <= 5:
    messenger.sendtext('ทำไมได้')
    # messenger.sendtext(line_result_percentage)
    # messenger.sendtext("ทำไม่ได้")

# messenger.sendtext("Helloword")


'''
เช็คค่า API เบื้องต้นว่าทำงานได้หรือไม่ 

Bitkub = ไปเก็บราคาของฝั่ง Bitkub (BNB)
Biannce = ไปเก็บราคาของฝั่ง Biance (BNB)

สร้างฟังชั้นไว้เช็คราคาโดยเฉพาะว่า ตอนนี้กี่เปอร์เซ็นต์ 
เข้าสูตรหาส่วนต่าง (((ฺBitkub - biannce)/biannce)*100)
  if Bitkub > Biannce (เป็นบวก) +5
     print สูตรส่วนต่าง
     print สามารถทำการ Abritage ได้
  elif Bitkub < Binance (เป็นลบ) =<4.9 
     print สูตรส่วนต่าง 
     print ไม่สามารถทำได้ 

   
    
     
'''