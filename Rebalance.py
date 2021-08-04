import hashlib
import hmac
import json
import requests
from time import time, sleep
from datetime import datetime


# API info
API_HOST = 'https://api.bitkub.com'
API_KEY = '9b38595cab407d7bb6ebf5e4fb7d85b4'
API_SECRET = b'202d71b0fc94501e290ac32ca023020c'

# Config
COIN_CURRENCY = 'THB_BTC'
# TIME = 3600 #เวลาเช็คทุกๆ 1 ชั่วโมง
TIME = 60
a = 0

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

# print('Payload with signature: ' + json_encode(data))
# response = requests.post(API_HOST + '/api/market/balances', headers=header, data=json_encode(data))

# print('Balances: ' + response.text)

def symbol_bitkub(): #ตรวจสอบสัญลักษณ์คู่เทรด
    response = requests.get(API_HOST + '/api/market/symbols')
    print (response.text) 
    
def ticker(coin = 'THB_BTC', variable = 'percentChange'): #หาราคาต่าง ๆ ของคู่เหรียญที่เราต้องการบอกราคาล่าสุด สูง ต่ำ เปอร์ที่เปลี่ยนแปลง 
    response = requests.get(API_HOST + '/api/market/ticker',params='sym='+coin) 
    responseJson = json.loads(response.text) #ต้องใช้ Load เพื่อให้สามารถเอาตัวแปรเข้ามาใช้งานได้จริง 
    result = ''
    if (variable == ''):
        result = responseJson[coin]
    else:
        result = responseJson[coin][variable]
    print (result)
    return result

def buy(): #ใช้ในการตั้งราคาซื้อ 
    data = {
	'sym': 'THB_BTC', #คู่ที่เราจะเทรด
	'amt': 10, # THB amount you want to spend
	'rat': 260000, #ราคาที่ต้องการจะเข้าซื้อ 
	'typ': 'limit', #รูปแบบที่จะเทรด หากใช้ market จะเป็นเอาราคาปัจจุบันเลย
	'ts': ts, #ต้องมีติดไว้ทุกอันที่ใช้ Post
    }
    signature = sign(data)
    data['sig'] = signature

    print('Payload with signature: ' + json_encode(data))
    response = requests.post(API_HOST + '/api/market/place-bid', headers=header, data=json_encode(data))
    print (response.text)

def sell(): #ขายวัดจากจำนวนเหรียญที่มี 
    data = {
	'sym': 'THB_BTC', #คู่ที่เราจะเทรด
	'amt': 0.01, # BTC amount you want to sell
	'rat': 260000, #ราคาที่ต้องการจะเข้าขาย
	'typ': 'limit', #รูปแบบที่จะเทรด
	'ts': ts, #ต้องมีติดไว้ทุกอันที่ใช้ Post
    }
    signature = sign(data)
    data['sig'] = signature

    print('Payload with signature: ' + json_encode(data))
    response = requests.post(API_HOST + '/api/market/place-ask', headers=header, data=json_encode(data))
    print (response.text)

def check_wallet():

    print('Payload with signature: ' + json_encode(data))
    response = requests.post(API_HOST + '/api/market/wallet', headers=header, data=json_encode(data))
    print (response.text)

def check_balance():
    
    print('Payload with signature: ' + json_encode(data))
    response = requests.post(API_HOST + '/api/market/balances', headers=header, data=json_encode(data))
    print (response.text)

def sell_fiat(): #ขายจำนวนเงินบาทที่ต้องการ ได้ใช้แน่ ๆ 
    data = {
	'sym': 'THB_BTC', #คู่ที่เราจะเทรด
	'amt': 15, # BTC amount you want to sell
	'rat': 260000, #ราคาที่ต้องการจะเข้าขาย
	'typ': 'limit', #รูปแบบที่จะเทรด
	'ts': ts, #ต้องมีติดไว้ทุกอันที่ใช้ Post
    }
    signature = sign(data)
    data['sig'] = signature

    print('Payload with signature: ' + json_encode(data))
    response = requests.post(API_HOST + '/api/market/place-ask-by-fiat', headers=header, data=json_encode(data))
    print (response.text)

def timer(seconds): #ตัวนับเวลาถอยหลัง 
    total = 0
    while True:
        total = total + seconds
        sleep(seconds - time() % seconds)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print('sleep ' + str(total) + ' seconds ::: ' + current_time)

def check_order():
    data = {
	'sym': 'THB_BTC', #คู่ที่เราจะเทรด
    'p' : 1,
	'ts': ts, #ต้องมีติดไว้ทุกอันที่ใช้ Post
    }
    signature = sign(data)
    data['sig'] = signature

    print('Payload with signature: ' + json_encode(data))
    response = requests.post(API_HOST + '/api/market/my-order-history', headers=header, data=json_encode(data))
    print (response.text)

timer(TIME)

'''
เช็ค API ก่อนว่าทำงานได้ไหม def check api

เช็คยอดเงินคงเหลือว่ามีเท่าไหร่ def check balance , 
    if  Bitcoin = 0 ให้ทำดังนี้ 
      a = เก็บค่า Balance Bath ออกมาด้วย หากยังให้ทำตามด้านล่าง 
      เสร็จแล้วให้นำค่าออกมาแล้วหาร 2 ,
         b(เงินส่วนที่ต้องนำไปซื้อ Bitcoin) = a/2 
      นำครึ่งนึงไปซื้อ BTC ตามที่จำนวนมี , 
          def buy(b) 
      ให้ไปเก็บค่าใน Order history ออกมาไว้เพื่ออ้างอิงต่อไป , 
         c = def price_order_history ล่าสุด 
         จบขั้นตอนแรกเป็นอันจบ

         a = balance ที่มี 
         b = จำนวนเงินรอบแรกที่ต้องนำไปซื้อ Bitcoin 
         c = ราคาล่าสุดที่ซื้อ Bitcoin ไป 
    else pass
       

เริ่มการนับถอยหลัง 1 ชั่วโมง , def timer 1h 

    เมื่อครบให้เริ่มรันโดยการเช็คว่า c กับราคาปัจจุบันมีความห่างกันที่เท่าไหร่ให้คิดให้เรียบร้อยก่อน พอได้เปอร์เซ็นต์มาก็ให้นำไปแทนที่เป็น d
        d = (((ราคาปัจจุบัน - c)/c)*100)

        if d >= 1 #ต้องขาย Bitcoin ออก 
            ทำสูตร Rebalance สำหรับขาย Bitcoin ออก 
            e = (((มูลค่า Bitcoin ของเราปัจจุบัน * ราคาปัจจุบันของ Bitcoin)+เงินบาทปัจจุบัน)/2)+เงินพิเศษหากมี) ,จะรู้ว่าเราต้องทำให้เงินบาทมีมูลค่าเท่าไหร่ 
            f =  e - เงินบาทที่เราปัจจุบัน , จะได้รู้ส่วนต่างว่าต้องการอีกเท่าไหร่
            def sell bitcoin ออกมาตามค่า f 
                โดยใช้การขายการตั้งขายโดยอิงจากเงินบาท 
                
            เก็บค่าใหม่ ไปใช้อ้างอิง 
                    1.มูลค่าเงินบาทที่มี
                    2.จำนวนเหรียญ Bitcoin ที่มี
                    3.ราคาปัจจุบันของ Bitcoin 
                    4.ราคาเข้าซื้อหรือขาย Bitcoin ล่าสุด
                
        elif d <= -1 #ต้องเอาเงิน Bath ไปซื้อเพิ่ม 
                ทำสูตร Rebalance สำหรับซื้อ Bitcoin เพิ่ม 
                e = (((มูลค่า Bitcoin ของเราปัจจุบัน * ราคาปัจจุบันของ Bitcoin)+เงินบาทปัจจุบัน)/2)+เงินพิเศษหากมี) ,จะรู้ว่าเราต้องทำให้เงินบาทมีมูลค่าเท่าไหร่ 
                f = เงินบาทที่เรามีปัจจุบัน - e , จะได้รู้ส่วนต่างว่าต้องนำเท่าไหร่ไปซื้อเพิ่ม
                def buy bitcoin ออกมาให้ได้ตามค่า F 
                   โดยใช้การซื้อทั่วไป 

                เก็บค่าใหม่ ไปใช้อ้างอิง 
                    1.มูลค่าเงินบาทที่มี
                    2.จำนวนเหรียญ Bitcoin ที่มี
                    3.ราคาปัจจุบันของ Bitcoin 
                    4.ราคาเข้าซื้อหรือขาย Bitcoin ล่าสุด

        elif  :
            pass 
 
def เช็ดเงินโดยรวม 
   แสดงมูลค่า Bitcoin 
   แสดงมูลค่า Bath 
   มูลค่าโดยรวมทั้งพอร์ต =  เงินบาทที่มี + (จำนวนเหรียญ Bitcoin*ราคาปัจจุบัน)

แล้วถ้าปิดโปรแกรมไปแล้วเปิดใหม่จะทำให้ไงให้มันข้ามตอนแรกไป
'''