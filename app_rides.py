from flask import Flask,jsonify,request
import requests
import json
import pymongo
import hashlib

app = Flask(__name__)

myclient=pymongo.MongoClient("mongodb://127.0.0.1:27017/")
mydb=myclient["RIDE"]
ride=mydb["rides"]

@app.route('/api/v1/rides',methods=['POST'])
def add_rides():
	d={}
	d["column_name"]="ride"
	d["work"]="INS"
	ride_id=request.json['id']
	username=request.json['created_by']
	d["data"]={"username":username}
	query=requests.post('http://localhost:8000/api/v1/db/read',data=json.dumps(d))
	if(query.text=="0"):
		d["data"]={"id":ride_id}
		query=requests.post('http://localhost:8080/api/v1/db/read',data=json.dumps(d))
		if(query.text=="0"):
			timestamp=request.json['timestamp']
			source=request.json['source']
			destination=request.json['destination']
			d["work"]="INS2"
			d["data"]={"id":ride_id,"created_by":username,"timestamp":timestamp,"source":source,"destination":destination,"usernames":[]}
			query=requests.post('http://localhost:8080/api/v1/db/write',data=json.dumps(d))
			return (query.text,201)
		else:
			return("",400)
	else:
		return("",400)


@app.route('/api/v1/rides/<source>/<destination>',methods=['GET'])
def print_rides(source,destination):
	d={}
	d["column_name"]="ride"
	d["data"]={"source":source,"destination":destination}
	d["work"]="PRINT"
	query=requests.post('http://localhost:8080/api/v1/db/read',data=json.dumps(d))
	if(query.text=="0"):
		return("",400)
	return (query.text,200)

@app.route('/api/v1/rides/<ride_id>',methods=['GET'])
def list_ride(ride_id):
	d={}
	d["column_name"]="ride"
	d["data"]={"id":ride_id}
	d["work"]="LIST"
	query=requests.post('http://localhost:8080/api/v1/db/read',data=json.dumps(d))
	if(query.text=="0"):
		return("",400)
	return (query.text,200)
  
@app.route('/api/v1/rides/<ride_id>',methods=['DELETE'])
def delete_ride(ride_id):
	d={}
	d["column_name"]="ride"
	d["data"]={"id":ride_id}
	d["work"]="DEL"
	query=requests.post('http://localhost:8080/api/v1/db/read',data=json.dumps(d))
	if(query.text=="1"):
		query=requests.post('http://localhost:8080/api/v1/db/write',data=json.dumps(d))
		return (query.text,200)
	else:
		return({},400)


@app.route('/api/v1/rides/<ride_id>',methods=['POST'])
def add_usernames(ride_id):
	d={}
	d["column_name"]="ride"
	d["data"]={"id":ride_id}
	d["work"]="INS1"
	query=requests.post('http://localhost:8080/api/v1/db/read',data=json.dumps(d))
	if(query.text=='1'):
		username=request.json['username']
		d["data"]={"username":username}
		query=requests.post('http://localhost:8000/api/v1/db/read',data=json.dumps(d))
		if(query.text=="0"):
			d["data"]={"id":ride_id,"username":username}
			query=requests.post('http://localhost:8080/api/v1/db/write',data=json.dumps(d))
			return (query.text,201)
		else:
			return ("",400)
	else:
		return("",400)

@app.route('/api/v1/db/clear',methods=['POST'])
def clear_db():
	x=ride.find_one()
	if(type(x)==type(None)):
		return({},400)
	x=ride.delete_many({})
	return({},200)


@app.route('/api/v1/db/read',methods=['POST'])
def db_read():
	dataDict=json.loads(request.data)
	column=dataDict["column_name"]
	where=dataDict["work"]
	if(column=="ride"):
		y=ride.find_one(dataDict["data"])
		if(type(y)!=type(None) and (where=='DEL' or where=='INS')):
			return(str(1))
		elif(type(y)!=type(None) and where=='LIST'):
			l={}
			l["created_by"]=y["created_by"]
			l["ride_id"]=y["id"]
			l["timestamp"]=y["timestamp"]
			l["source"]=y["source"]
			l["destination"]=y["destination"]
			l["username"]=y["usernames"]
			return(l)
		elif(type(y)!=type(None) and where=='PRINT'):
			l={}
			l["username"]=y["created_by"]
			l["timestamp"]=y["timestamp"]
			l["id"]=y["id"]
			return(l)
		else:
			return(str(0))


@app.route('/api/v1/db/write',methods=['POST'])
def db_write():
	dataDict=json.loads(request.data)
	column=dataDict['column_name']
	where=dataDict["work"]
	if(where=='DEL' and column=='ride'):
		ride.delete_one(dataDict["data"])
		return(str(1))
	elif(where=='INS1' and column=='ride'):
		ride.update_one({"id":dataDict["data"]["id"]},{"$addToSet":{"usernames":dataDict["data"]["username"]}})
		return(str(1))
	elif(where=="INS2" and column=='ride'):
		framework_id=ride.insert_one(dataDict["data"]).inserted_id
		new_framework=ride.find_one({"_id":framework_id})
		output={"id":new_framework["id"],"created_by":new_framework["created_by"],"timestamp":new_framework["timestamp"],"source":new_framework["source"],"destination":new_framework["destination"]}
		return(jsonify({"result":output}))
	else:
		return(str(0))

# main driver function 
if __name__ == '__main__':  
    app.run(host='0.0.0.0',port='8080',debug=True)