from flask import Flask,jsonify,request
import json
import requests
import pymongo
import hashlib

app = Flask(__name__)

myclient=pymongo.MongoClient("mongodb://user_mongodb:27017/")
mydb=myclient["USER"]
user=mydb["users"]

@app.route('/api/v1/users',methods=['PUT']) 
def add_framework():
	username = request.json['username']
	password = request.json['password']
	d={}
	d["column_name"]="user"
	d["data"]={"username":username}
	d["work"]="INS"
	query=requests.post('http://localhost:8000/api/v1/db/read',data=json.dumps(d))
	if(query.text=="1"):
		x= hashlib.sha1(password.encode())
		password=str(x.hexdigest())
		d["data"]={"username":username,"password":password}
		query=requests.post('http://localhost:8000/api/v1/db/write',data=json.dumps(d))
		return(query.text,200)
	else:
		return ({},400)
	

@app.route('/api/v1/users/<username>',methods=['DELETE'])
def delete_value(username):
	d={}
	d["column_name"]="user"
	d["data"]={"username":username}
	d["work"]="DEL"
	query=requests.post('http://localhost:8000/api/v1/db/read',data=json.dumps(d))
	if(query.text=="0"):
		query=requests.post('http://localhost:8000/api/v1/db/write',data=json.dumps(d))
		return (query.text,200)
	else:
		return({},400)


@app.route('/api/v1/users',methods=['GET'])
def list_users():
	d={}
	d["column_name"]="user"
	d["work"]='LIST'
	query=requests.post('http://localhost:8000/api/v1/db/read',data=json.dumps(d))
	if(query.text=="1"):
		return("",400)
	return(query.text,200)
	

@app.route('/api/v1/db/clear',methods=['POST'])
def clear_db():
	x=user.find_one()
	if(type(x)==type(None)):
		return({},400)
	x=user.delete_many({})
	return({},200)

@app.route('/api/v1/db/read',methods=['POST'])
def db_read():
	dataDict=json.loads(request.data)
	column=dataDict["column_name"]
	where=dataDict["work"]
	if(where=='LIST' and column=="user"):
		y=user.find()
		if(type(y)==type(None)):
			return({},400)
		result=[]
		for x in user.find():
			result.append(x["username"])
		return jsonify({"output":result})
	elif((where=='INS' or where=='DEL' or where=='INS1') and (column=="user" or column=="ride")):
		y=user.find_one(dataDict["data"])
		if(type(y)==type(None)):
			return str(1)
		else:
			return str(0)


@app.route('/api/v1/db/write',methods=['POST'])
def db_write():
	dataDict=json.loads(request.data)
	if(dataDict["work"]=="DEL"):
		y=user.find_one(dataDict["data"])
		if(type(y)!=type(None)):
			user.delete_one(dataDict["data"])
			return (jsonify(1))
		else:
			return (jsonify(0))
	elif(dataDict["work"]=='INS'):
		mydict=dataDict["data"]
		framework_id=user.insert_one(mydict).inserted_id
		new_framework=user.find_one({"_id":framework_id})
		output={"name":new_framework["username"],"password":new_framework["password"]}
		return(jsonify({"result":output}))
		
if __name__ == '__main__':      	
	app.run(host='0.0.0.0',port='8000',debug=True)
	print("HELLO")
