from flask import Flask, request
from flask import render_template
from urllib.parse import urlencode, unquote
import requests
import json
import datetime
import pymysql

app= Flask(__name__)
db=pymysql.connect(host='localhost',user='root',password='1234',db='weather',charset='utf8')
@app.route("/")
def home():
	today = datetime.datetime.today()
	daystr = str(today.year) +"년" + str(today.month) +"월"+str(today.day) +"일"
	return render_template("index.html",title="승원이의 성장일기",today=daystr)

@app.route("/local")
def local():
	cur=db.cursor()
	cur.execute("Select level3, x, y From localxy Where level2='원주시' and level3!=''")
	rows=cur.fetchall()
	dongs =[]

	for row in rows:
		dong=[]
		dong.append(row[0])
		dong.append(row[1])
		dong.append(row[2])
		dongs.append(dong)
	print(dongs)
	return render_template("local.html",dong_list=dongs)
	

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
