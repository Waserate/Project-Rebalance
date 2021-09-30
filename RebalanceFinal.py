import hashlib
import hmac
import json
import requests
from time import time, sleep
from datetime import datetime
import configparser
from songline import Sendline 
import math

# API info
API_HOST = 'https://api.bitkub.com'

# TIME = 3600 #เวลาเช็คทุกๆ 1 ชั่วโมง

global_config_val = {}
config = configparser.ConfigParser()

def read_config():
    global config
    config.read("config.ini")
    global global_config_val
    global_config_val = config['CONFIG']
    
## อ่านค่า config ##
read_config()
last_price = global_config_val['last_price']

### อ่านค่า line token ### 
token = global_config_val['line_token']
messenger = Sendline(token)
second = int(global_config_val['time'])
balance = ''

def timer(seconds): #ตัวนับเวลาถอยหลัง 
    total = 0
    while True:
        total = total + seconds
        sleep(seconds - time() % seconds)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        rebalance_process()
        report()

def json_encode(data):
	return json.dumps(data, separators=(',', ':'), sort_keys=True)

def sign(data):
	j = json_encode(data)
	# print('Signing payload: ' + j)
	h = hmac.new(bytes(global_config_val['api_secret'], encoding='utf-8'), msg=j.encode(), digestmod=hashlib.sha256)
	return h.hexdigest()

# check server time
def check_server_time():
    response = requests.get(API_HOST + '/api/servertime')
    timestamp = int(response.text)
    return timestamp
# print('Server time: ' + response.text)
# check balances
header = {
	'Accept': 'application/json',
	'Content-Type': 'application/json',
	'X-BTK-APIKEY': global_config_val['api_key'],
}
data = {
	'ts': check_server_time(),
}
signature = sign(data)
data['sig'] = signature

# def symbol_bitkub(): #ตรวจสอบสัญลักษณ์คู่เทรด
#     response = requests.get(API_HOST + '/api/market/symbols')
#     print (response.text) 
    
def ticker(coin = '', variable = ''): #หาราคาต่าง ๆ ของคู่เหรียญที่เราต้องการบอกราคาล่าสุด สูง ต่ำ เปอร์ที่เปลี่ยนแปลง 
    response = requests.get(API_HOST + '/api/market/ticker',params='sym='+coin) 
    responseJson = json.loads(response.text) #ต้องใช้ Load เพื่อให้สามารถเอาตัวแปรเข้ามาใช้งานได้จริง 
    result = ''
    if (variable == ''):
        result = responseJson[coin]
    else:
        result = responseJson[coin][variable]
    # print (result)
    return result
    
def check_balance():
    # print('Payload with signature: ' + json_encode(data))
    response = requests.post(API_HOST + '/api/market/balances', headers=header, data=json_encode(data))
    # print (response.text)

def check_order():
    data = {
	'sym': global_config_val['trade_sym'], #คู่ที่เราจะเทรด ควร Config ได้
    'p' : 1,
    'lmt' :1,
	'ts': check_server_time(), #ต้องมีติดไว้ทุกอันที่ใช้ Post
    }
    signature = sign(data)
    data['sig'] = signature
    # print('Payload with signature: ' + json_encode(data))
    response = requests.post(API_HOST + '/api/market/my-order-history',headers=header, data=json_encode(data)) 
    responseJson = json.loads(response.text) #ต้องใช้ Load เพื่อให้สามารถเอาตัวแปรเข้ามาใช้งานได้จริง
    return responseJson['result'][0]['rate']
    
def sell_fiat(signal_sell): #ขายจำนวนเงินบาทที่ต้องการ ได้ใช้แน่ ๆ
    global last_price 
    data = {
	'sym': global_config_val['trade_sym'], #คู่ที่เราจะเทรด
	'amt': signal_sell, # BTC amount you want to sell
	'rat': 0, #ราคาที่ต้องการจะเข้าขาย
	'typ': 'market', #รูปแบบที่จะเทรด
	'ts': check_server_time(), #ต้องมีติดไว้ทุกอันที่ใช้ Post
    }
    signature = sign(data)
    data['sig'] = signature
    # print('Payload with signature: ' + json_encode(data))
    response = requests.post(API_HOST + '/api/market/place-ask-by-fiat', headers=header, data=json_encode(data))
    print (response.text)
    last_price = check_order() 
    config.set('CONFIG', 'last_price', str(last_price))
    with open('config.ini', 'w') as f:
        config.write(f)

def buy(signal_buy): #ใช้ในการตั้งราคาซื้อ 
    global last_price
    data = {
	'sym': global_config_val['trade_sym'], #คู่ที่เราจะเทรด
	'amt': signal_buy, # THB amount you want to spend
	'rat': 0, #ราคาที่ต้องการจะเข้าซื้อ 
	'typ': 'market', #รูปแบบที่จะเทรด หากใช้ market จะเป็นเอาราคาปัจจุบันเลย
	'ts': check_server_time(), #ต้องมีติดไว้ทุกอันที่ใช้ Post
    }
    signature = sign(data)
    data['sig'] = signature   
    # print('Payload with signature: ' + json_encode(data))
    response = requests.post(API_HOST + '/api/market/place-bid', headers=header, data=json_encode(data))
    print (response.text)
    last_price = check_order() 
    config.set('CONFIG', 'last_price', str(last_price))
    with open('config.ini', 'w') as f:
        config.write(f)

# def CheckAPIBitkub(showError): #เช็ค API ว่าทำงานได้ไหม
#     # print('checking error :', showError)
#     if showError == 0 :  
#         print("------------------------------")
#         print("Bitkub API Checking : ok ")
#         print("------------------------------")

#     else:
#         print("--------------------------------")
#         print("Bitkub API Checking : Error!!!!! ")
#         print("Please recheck your API . . . ")
#         print("----------------------------------")

def rebalance_process(): #ขั้นตอนในการ Reblalnce 
    global last_price 
    global price_now
    global bath_balance
    global amount_asset
    price_now = ticker(global_config_val['trade_sym'],'highestBid')
    diffchange = (((price_now - last_price)/last_price)*100)
    print ('Diff ขั้น Rebalance :' , diffchange )
    print ('Bath ขั้น Rebalance:' , bath_balance) # ไม่อัพ 
    print ('Last Price ขั้น Rebalance:' , last_price )
    print ('Price Now ขั้น Rebalance:' , price_now )
    print ('amount asset ขั้น Rebalance:' , amount_asset )# ไม่อัพ  
    diff_txt = ('Diff :' , diffchange)
    messenger.sendtext(diff_txt)

    if diffchange >= float(global_config_val['percent']) : #ด้านที่ราคาสินทรัพย์ที่ถือขึ้นเราต้องนำไปขาย 
        rebalance = (((amount_asset * price_now)+bath_balance)/2) 
        signal_sell = rebalance - bath_balance
        print ('Sell ขั้น Rebalance :' , signal_sell ,'Bath')
        sell_fiat (signal_sell)
        last_price = check_order() 
        config.set('CONFIG', 'last_price', str(last_price))
        with open('config.ini', 'w') as f:
          config.write(f)     
        signal_sell_txt = ('Sell  :' , signal_sell ,'Bath')
        messenger.sendtext(signal_sell_txt)

    elif diffchange <= (((0-float(global_config_val['percent'])*2)+float(global_config_val['percent']))): #ด้านที่ราคาสินทรัพย์ที่ถือลงเราต้องนำเงินบาทไปซื้อ
        rebalance = (((amount_asset * price_now)+bath_balance)/2)
        signal_buy = (rebalance - bath_balance)
        signal_buy_reverse = (signal_buy - (signal_buy*2)) #ต้องกลับด้านสูตรไม่อย่างงั้น Parameter จะติดลบแล้ว Def buy จะใช้การไม่ได้ 
        print ('ทำให้ทุนบาทลดลง ขั้น Rebalance:' , signal_buy ,'Bath') #ปริ้นค่าจริงที่ติดลบออกมาให้ดู 
        print ('Buy ในบอทที่กลับค่าคือ ขั้น Rebalance',signal_buy_reverse)
        buy(signal_buy_reverse) #แต่ตอนส่งจริงต้องใช้ตัวที่กลับด้านไม่ให้ติดลบ 
        last_price = check_order() 
        config.set('CONFIG', 'last_price', str(last_price))
        with open('config.ini', 'w') as f:
          config.write(f)    
        signal_buy_txt = ('Buy :' , signal_buy_reverse ,'Bath')
        messenger.sendtext(signal_buy_txt)
        
    else :
        last_price = check_order() 
        config.set('CONFIG', 'last_price', str(last_price))
        with open('config.ini', 'w') as f:
            config.write(f)
        print (' Wait Next time ขั้น Re ')
        messenger.sendtext(' Wait Next time ')

#สร้าง Def ใหม่เพื่องาน Amount Asset กับ Bath Balnce 

difft = 0 
def report(): # รายงานสรุปผล ผิด หากรีไปแล้วรอบนึง ค่ายังเป็นแบบเดิมแล้วรีซ้ำมันจะจำค่าเก่าอยู่และรีเบี่ยงเบนไปประมาณนึง ทางแก้คือต้องให้อัพ ฟamountAsset กับ Bathbalnce หลังจากที่มีการซื้อขาย
    global difft 
    global last_price 
    global price_now
    global bath_balance
    global amount_asset
    global balance_All
    # balance_All = result_balance()['result']
    # main_asset = float(balance_All[asset_sym]['available'])
    # amount_asset = main_asset
    # bath_balance = float(balance_All['THB']['available'])
    result_balance()
    price_now = ticker(global_config_val['trade_sym'],'highestBid')
    print ('amount_assetขั้น Report'+ asset_sym +'ที่มี :', amount_asset )
    print ('bath มีขั้น Report :', bath_balance )
    print ('มูลค่าพอร์ตโดยรวมขั้น Report :' , (amount_asset * price_now) + bath_balance , 'บาท') 
    report_txt = (f'จำนวนเหรียญ {asset_sym} ที่มี :, {amount_asset}\n จำนวนเงินบาทที่มี :, {bath_balance} \n มูลค่าพอร์ตโดยรวม :, {(amount_asset * price_now) + bath_balance} , บาท')
    messenger.sendtext(report_txt)
    print ('Last price ขีั้น Report' + str(last_price))
    print ('Price now ขั้น Report '+ str(price_now))
    difft = (((price_now - last_price)/last_price)*100)
    print ('ความต่างขั้น Report :' , difft)
    print ('---------------')
        
# temp = global_config_val['api_secret']
# bytes(temp, encoding='utf-8')
# print(bytes(temp, encoding='utf-8'))

## Start ##
## ต้องเพิ่มตัวเก็บค่า error #####
def result_balance():
    global balance
    global bath_balance
    global amount_asset
    global balance_All
    data = {
	    'ts': check_server_time(),
    }
    signature = sign(data)
    data['sig'] = signature
    response = requests.post(API_HOST + '/api/market/balances', headers=header, data=json_encode(data))
    balance = response.json()
    # showError = balance['error']  #แสดงค่า error ต้องเป็น 0 ถึงรันต่อได้
    # print('checking error :', showError)
    # CheckAPIBitkub(balance['error'])
    balance_All = balance['result']
    amount_asset = float(balance_All[asset_sym]['available']) #balance ของ main asset 
    bath_balance = float(balance_All['THB']['available'])

# info balance 
print("-- Welcome to Rebalance BOT --")
asset_sym = global_config_val['trade_sym'].split('_')[1] #ใส่ใน config เปลี่ยนค่าได้
# balance_All = balance['result'] #balance ทั้งหมดใน wallet
balance_All = ''
amount_asset = 0.0
bath_balance = ''
result_balance()
# main_asset = 10000.00 Test 
first_buy = bath_balance/2 # นำTHB ไปซื้อ asset ครึ่งหนึ่ง 
price_now = ticker(global_config_val['trade_sym'],'highestBid') #ตัวในช่องแรกควร Config ได้เพื่อเปลี่ยนคู่ Rebalnce
# amount_asset = main_asset
last_price = check_order() 
# last_price = 0 Test 
config.set('CONFIG', 'last_price', str(last_price))
with open('config.ini', 'w') as f:
    config.write(f) 

# print(float(global_config_val['last_price']))

# print("-------------------------------------------------------")
print ('Your Rebalance :',global_config_val['trade_sym'])
print ('Diff Rebalance :',global_config_val['percent']) 
print(f'{asset_sym} : {amount_asset}')
print(f'THB  : {bath_balance}')

resulttradesym_txt = 'Your Rebalance :',global_config_val['trade_sym']
resultDiff_txt = 'Diff Rebalance :',global_config_val['percent']
resultAsset_txt = (f'{asset_sym} : {amount_asset}')
resultBathbalance_txt = (f'THB  : {bath_balance}')
messenger.sendtext(f'\n{resulttradesym_txt}\n{resultDiff_txt}\n{resultAsset_txt}\n{resultBathbalance_txt}')
time_text = ""

def time_text_fx(second):
    global time_text
    if(second < 3600):
        time_text = "นับถอยหลัง " + str(int(second/60)) + " นาที"
        if(second < 60):
            time_text = "นับถอยหลัง " + str(int(second)) + " วินาที"
    else:
        time_text_sec = ""
        if(int((second/60)%60) != 0):
            time_text_sec = " " + str(int((second/60)%60)) + " นาที"
        time_text = "นับถอยหลัง " + str(int(second/60/60)) + " ชั่วโมง" + time_text_sec
    return time_text

if amount_asset == 0.0 :
    print(f'ต้องนำไปซื้อ {asset_sym} : {first_buy} THB')
    messenger.sendtext(f'ต้องนำไปซื้อ {asset_sym} : {first_buy} THB')
    buy(first_buy) #ยังไม่เอาขึ้นเพราะเดียวมันไปซื้อจริง
    report()
    timer(second)
else:
    print (time_text_fx(int(second)))
    messenger.sendtext(time_text_fx(int(second)))
    last_price = check_order() 
    rebalance_process()
    report()
    config.set('CONFIG', 'last_price', str(last_price))
    with open('config.ini', 'w') as f:
        config.write(f)
    timer(second)

