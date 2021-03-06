#โปรแกรม Bot BNB Checker Binance - Bikub (Tanatorn Vaskul)
# หลักการทำงาน : Bot จะเข้าไปเช็คราคาที่เว็บ Biancne นำมาเทียบกับของ Bitkub ทุก ๆ 30 นาทีและส่งรายงาน
# หากเกิน 3 เปอร์เซ็นต์จะแปลว่าใกล้ทำได้ แต่ถ้า 5 เปอร์เซ็นต์คือสามารถทำกำไรจากส่วนต่างได้ ให้เราทำการเทรด

# วิธีการใช้งาน :
# 1 ให้เรากรอก Line Token ที่เราต้องการส่งข้อมูลนี้ไป 
# 2 ใส่ API และ API Key ของเราลงไป (เฉพาะของฝั่ง Biannce) 
# 3 รันโปรแกรมแล้วรับแจ้งเตือนได้เลย 

from binance import Client
from forex_python.converter import CurrencyRates
from songline import Sendline
import hashlib
import hmac
import json
import requests
from time import time, sleep
from datetime import datetime
import configparser
c = CurrencyRates() 

#ส่วนของ Line Token
# token = ''  #ที่ต้อง Config
# token = 'PWCzRFGjpkxtUJ9JUzjq5wHIWsJ8sRkywCCkDA0suCd'  #ที่ต้อง Config

# API ของ Biannce 
# api_key = ''  #ที่ต้อง Config
# api_secret = ''  #ที่ต้อง Config ตั้งให้เป็น Read เท่านั้น 
# api_key = '9PkHxLgQ3lGyHIeUi6tw1HsQrC6nBnHigw99WY7gfZAf597jaMxKMXPI58col6FC'  #ที่ต้อง Config
# api_secret = 'QxKdJLR1GIRRisjEb9Wn2j7McCZ8zgMCLz4rwbMAkPM2UqsOFKiEnijtxvKeGPXt'  #ที่ต้อง Config ตั้งให้เป็น Read เท่านั้น 
# client = Client(api_key, api_secret)

# API ของ Bitkub 
API_HOST = 'https://api.bitkub.com'
API_KEY = '' #ไม่จำเป็นต้องใส่ก็ Get ค่าออกมาได้ 
API_SECRET = b'' #ไม่จำเป็นต้องใส่ก็ Get ค่าออกมาได้ 

def read_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    for section in config.sections():
        for key in config[section]:
            global messenger, client, TIME
            messenger = Sendline(config[section]['token_line'])
            client = Client(config[section]['api_key_binance'], config[section]['api_secret_binance'])
            TIME = int(config[section]['time_check'])

#ส่วนที่ห้ามยุ่งของ Bitkub  
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

#เช็คเรทค่าเงินไทย
rate_bath = c.get_rate('USD', 'THB') 
  #print (rate_bath) 


def timer(seconds): #ตัวนับเวลาถอยหลัง 
    total = 0
    while True:
        total = total + seconds
        sleep(seconds - time() % seconds)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        calculate()

def ticker(coin = 'THB_BNB', variable = 'highestBid'): #หาราคาต่าง ๆ ของคู่เหรียญที่เราต้องการบอกราคาล่าสุด สูง ต่ำ เปอร์ที่เปลี่ยนแปลง 
    response = requests.get(API_HOST + '/api/market/ticker',params='sym='+coin) 
    responseJson = json.loads(response.text) #ต้องใช้ Load เพื่อให้สามารถเอาตัวแปรเข้ามาใช้งานได้จริง 
    result = ''
    if (variable == ''):
        result = responseJson[coin]
    else:
        result = responseJson[coin][variable]
        #print (result)
    return result

def roundDec(number):
    return round(number,2)

def calculate():
   print ("-----------------")
   prices = client.get_all_tickers()
   mycoin = ['BNBUSDT'] #สามารถใส่ , เพื่อใส่คู่เหรียญอื่นที่ต้องการได้ 
   for loop_price in prices:
      for loop_mycoin in mycoin:
        sym = loop_mycoin
        if loop_price['symbol'] == sym:
            # print(loop_price)
            price_bnb = float(loop_price['price'])
            # print ("Rate BNB :",price_bnb,'USD')
            biannce_thai_rate = price_bnb * rate_bath
            # print ("Rate BNB (Binance) :",biannce_thai_rate,"Bath")
   
   bnb_bitkub_rate = ticker() #ได้ค่ามาไว้ในตัวแปร 
   result_bath = bnb_bitkub_rate - biannce_thai_rate #ได้ค่ามาไว้ในตัวแปร 
   result_percentage = (((bnb_bitkub_rate - biannce_thai_rate)/biannce_thai_rate)*100) #ได้ค่ามาไว้ในตัวแปร 

#  print ('Rate BNB :',price_bnb,'USD\nRate BNB (Binance) :',biannce_thai_rate,'Bath\nRate BNB (Bitkub) :',bnb_bitkub_rate,'Bath\nDiff (Bath):',result_bath,'\nDiff (%):',result_percentage)
   print ('Rate BNB : %.2f USD\nRate BNB (Binance) : %.2f Baht\nRate BNB (Bitkub) : %.2f Baht\nDiff (Baht): %.2f Baht\nDiff (per.): %.2f %s'%(roundDec(price_bnb),roundDec(biannce_thai_rate),roundDec(bnb_bitkub_rate),roundDec(result_bath),roundDec(result_percentage), "%"))

   if result_percentage >= 5:
        five_per = ('เกิน 5 เปอร์เซ็นต์ สามารถทำ Abritage ได้!!')
        messenger.sendtext('\nRate BNB : %.2f USD\nRate BNB (Binance) : %.2f Baht\nRate BNB (Bitkub) : %.2f Baht\nDiff (Baht): %.2f Baht\nDiff (per.): %.2f %s'%(roundDec(price_bnb),roundDec(biannce_thai_rate),roundDec(bnb_bitkub_rate),roundDec(result_bath),roundDec(result_percentage), "%"))
   elif result_percentage >= 3:
         messenger.sendtext('เกิน 3 เปอร์เซ็นต์เกือบ Abritage ได้แล้ว')
   elif result_percentage >= 1:
         messenger.sendtext('เกิน 1 เปอร์เซ็นต์กำลังจะมีโอกาส')
   elif result_percentage <= 0.99:
         messenger.sendtext('ยังไม่มีโอกาส')

# Read ค่า config
read_config("./config.ini")
timer(TIME)




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