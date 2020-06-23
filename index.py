from flask import Flask, request #flask: 파이썬의 라이브러리
from flask import render_template #import: 라이브러리 호출
from urllib.parse import urlencode, unquote
import requests
import json
import datetime
import pymysql

app= Flask(__name__)
db=pymysql.connect(host='localhost',user='root',password='1234',db='weather',charset='utf8') #mysql 설정
@app.route("/") #웹페이지 설정
def home(): # 합수
	today = datetime.datetime.today() # today변수에 오늘 시간 저장
	daystr = str(today.year) +"년" + str(today.month) +"월"+str(today.day) +"일" # dayst변수에 오늘 연월일 저장
	return render_template("index.html",title="승원이의 성장일기",today=daystr) #웹페이지에 저장된 값을 출력

@app.route("/local") #local웹페이지 설정
def local():# 합수
	cur=db.cursor() #cur 변수에 db.cursor 값을 저장
	cur.execute("Select level3, x, y From localxy Where level2='원주시' and level3!=''") # cur.execute에 원주시의 동,x,y값을 저장
	rows=cur.fetchall()# rows에cur.fetchall를 저장
	dongs =[] # dongs의 값을 저장

	for row in rows: #반복문
		dong=[] # dongs안에 리스트
		dong.append(row[0]) # dong 값 할당
		dong.append(row[1]) # x 값 할당
		dong.append(row[2]) # y 값 할당
		dongs.append(dong)  # dong 값이 dongs에 할당
	print(dongs) #dongs 출력
	return render_template("local.html",dong_list=dongs) #웹페이지에 dong 출력
	

@app.route("/weather")
def weather():
	dong=request.values.get("dong","error")
	x = request.values.get("x","error")
	y = request.values.get("y","error")
	if x=="error" or y=="error":
		return "x와 y값을 바르게 입력하시오"
	url= "http://apis.data.go.kr/1360000/VilageFcstInfoService/getVilageFcst"
	qs = "?" + urlencode(
		{
			"serviceKey" : unquote("3rEfTtuHnc7zEvwZewPaH8eQ958F8L6oxXRdFhI7VzfMdGFSwaNNjn6Ivz%2F2ZLpV76Y1eVDT6uTjPmqsrjnqeg%3D%3D")
			,"pageNO" : "1"
			,"numOfRows":"30"
			,"dataType":"JSON"
			,"base_date":"20200623"
			,"base_time": "0500"
			,"nx":x
			,"ny":y
		}
	)
	response=requests.get(url+qs)
	json_weather = json.loads(response.text)
	wth_response = json_weather.get("response")
	wth_body= wth_response.get("body")
	wth_items=wth_body.get("items")
	
	result={'강수확률':0,'최고기온':0,'습도':0}
	
	for wth_item in wth_items.get("item"):
		if wth_item.get("category")=="POP":
			result['강수확률']=wth_item.get("fcstValue")
		elif wth_item.get("category")=="TMX":
			result['최고기온']=wth_item.get("fcstValue")
		elif wth_item.get("category")=="REH":
			result['습도']=wth_item.get("fcstValue")
	return render_template("weather.html",dong=dong,pop=result['강수확률'],tmx=result['최고기온'],reh=result['습도'])
	

@app.route("/short")
def short():
	x = request.values.get("x","error")
	y = request.values.get("y","error")
	if x=="error" or y=="error":
		return "x와 y값을 바르게 입력하시오"
	url= "http://apis.data.go.kr/1360000/VilageFcstInfoService/getUltraSrtFcst"
	qs = "?" + urlencode(
		{
			"serviceKey" : unquote("3rEfTtuHnc7zEvwZewPaH8eQ958F8L6oxXRdFhI7VzfMdGFSwaNNjn6Ivz%2F2ZLpV76Y1eVDT6uTjPmqsrjnqeg%3D%3D")
			,"pageNO" : "1"
			,"numOfRows":"30"
			,"dataType":"JSON"
			,"base_date":"20200623"
			,"base_time": "0630"
			,"nx":x
			,"ny":y
		}
	)
	response=requests.get(url+qs)
	json_short = json.loads(response.text)
	sho_response = json_short.get("response")
	sho_body= sho_response.get("body")
	sho_items=sho_body.get("items")
	
	result1={'강수형태':0,'낙뢰':0,'하늘상태':0}
	for sho_item in sho_items.get("item"):
		if sho_item.get("category")=="PTY":
			if sho_item.get("fcstValue")=='0':
				result1['강수형태']="없음"
			elif sho_item.get("fcstValue")=='1':
				result1['강수형태']="비"
			elif sho_item.get("fcstValue")=='2':
				result1['강수형태']="비/눈"
			elif sho_item.get("fcstValue")=='3':
				result1['강수형태']="눈"
			elif sho_item.get("fcstValue")=='4':
				result1['강수형태']="소나기"
		elif sho_item.get("category")=="LGT":
			if sho_item.get("fcstValue")=='0':
				result1['낙뢰']="확률없음"
			elif sho_item.get("fcstValue")=='1':
				result1['낙뢰']= "낮음"
			elif sho_item.get("fcstValue")=='2':
				result1['낙뢰']= "중간"
			elif sho_item.get("fcstValue")=='3':
				result1['낙뢰']="높음"
		elif sho_item.get("category")=="SKY":
			if sho_item.get("fcstValue")=='1':
				result1['하늘상태']="맑음"
			elif sho_item.get("fcstValue")=='3':
				result1['하늘상태']="구름많음"
			elif sho_item.get("fcstValue")=='4':
				result1['하늘상태']="흐림"
	
		
		
		

	return render_template("short.html",pty=result1['강수형태'],lgt=result1['낙뢰'],sky=result1['하늘상태'])
	

def before_request():
	app.jinja_env.cache = {}	
	
if __name__ == "__main__":
	app.before_request(before_request)
	app.run(host="0.0.0.0",port="80")
