# -*- coding: utf-8 -*-
#抓取公开的pm2.5数据，存储在数据库
import pymysql,ast,hashlib,os,requests,pathlib
from bs4 import BeautifulSoup

#mysql链接配置
db_config={
		'host':'127.0.0.1',
		'port':3306,
		'user':'root',
		'password':'123456',
		'db':'pytest',
		'charset':'utf8'
}

#获得数据库连接以及游标
conn = pymysql.connect(**db_config)
cursor = conn.cursor()

#读取网页源代码
url = "http://api.help.bj.cn/apis/aqilist/"		#初始化网址
html = requests.get(url).text.encode('utf-8-sig')		#读取网页源代码

#判断网页是否更新
md5 = hashlib.md5(html).hexdigest() 	#生成新抓取网页的md5码
old_md5 = ''	#声明一个用于保存原有md5码的变量 初始值为空

if os.path.exists('E:/python/autotest/old.txt'):
	with open('E:/python/autotest/old.txt','r') as f:
		old_md5 = f.read()
with open('E:/python/autotest/old.txt','w') as f:
	f.write(md5)
print("old_md5="+old_md5+"; "+"md5="+md5)	#显示新老md5进行观察

if md5 != old_md5 or cursor.execute('select * from PM') == 0:
	print("数据已更新或第一次运行...")
	sp = BeautifulSoup(html,'html.parser')		#使用BeautifulSoup解析网页内容
	jsondata = ast.literal_eval(sp.text)	#jsondata取到的是字典类型数据
	js1 = jsondata.get('aqidata')	#取字典中key为aqidata的value
	cursor.execute('delete from PM')		#删除数据表中的内容
	conn.commit()
	n = 1
	for city in js1:	#city此时是列表js1中的第一条字典数据
		CityName = city['city']		#取出city字典数据中值为city的key
		PM25 = 0 if city['pm2_5'] == "" else int(city['pm2_5'])
		print("城市:{}		PM2.5={}".format(CityName,PM25))
		#新增一条记录
		sql = "insert into PM values({},'{}',{})".format(n,CityName,PM25)
		cursor.execute(sql)
		n+=1
		conn.commit()
else:
	print("数据未更新，从数据库读取。。。")
	cursor.execute("select * from PM")
	#print(cursor)
	rows = cursor.fetchall()
	for row in rows:
		print("城市：{}				PM2.5={}".format(row[1],row[2]))

#关闭数据库连接
conn.close()
	


