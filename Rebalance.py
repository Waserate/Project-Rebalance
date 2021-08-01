import hashlib
import hmac
import json
import requests

# API info
API_HOST = 'https://api.bitkub.com'
API_KEY = '9b38595cab407d7bb6ebf5e4fb7d85b4'
API_SECRET = b'202d71b0fc94501e290ac32ca023020c'

def json_encode(data):
	return json.dumps(data, separators=(',', ':'), sort_keys=True)

def sign(data):
	j = json_encode(data)
	print('Signing payload: ' + j)
	h = hmac.new(API_SECRET, msg=j.encode(), digestmod=hashlib.sha256)
	return h.hexdigest()

# check server time
response = requests.get(API_HOST + '/api/servertime')
ts = int(response.text)
print('Server time: ' + response.text)

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

print('Payload with signature: ' + json_encode(data))
# response = requests.post(API_HOST + '/api/market/balances', headers=header, data=json_encode(data))

# print('Balances: ' + response.text)

def symbol_bitkub(): #ตรวจสอบสัญลักษณ์คู่เทรด
    response = requests.get(API_HOST + '/api/market/symbols')
    print (response.text) 
    
def ticker(): #หาราคาต่าง ๆ ของคู่เหรียญที่เราต้องการบอกราคาล่าสุด สูง ต่ำ เปอร์ที่เปลี่ยนแปลง 
    response = requests.get(API_HOST + '/api/market/ticker',params='sym=THB_BTC')
    print (response.text)


def bids(): #โชว์ดูราคา Bid 
    response = requests.get(API_HOST + '/api/market/bids',params='sym=THB_BNB&lmt=1')
    print (response.text)

def buy(): #ใช้ในการตั้งราคาซื้อ 
    data = {
	'sym': 'THB_BTC', #คู่ที่เราจะเทรด
	'amt': 10, # THB amount you want to spend
	'rat': 260000, #ราคาที่ต้องการจะเข้าซื้อ 
	'typ': 'limit', #รูปแบบที่จะเทรด
	'ts': ts, #ต้องมีติดไว้ทุกอันที่ใช้ Post
    }
    signature = sign(data)
    data['sig'] = signature

    print('Payload with signature: ' + json_encode(data))
    response = requests.post(API_HOST + '/api/market/place-bid', headers=header, data=json_encode(data))
    print (response.text)

def sell(): #ขาย
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

symbol_bitkub()