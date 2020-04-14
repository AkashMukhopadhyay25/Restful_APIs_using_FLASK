from flask import Flask,jsonify,request
import pymongo
import hashlib


app = Flask(__name__)

myclient=pymongo.MongoClient("mongodb://127.0.0.1:27017/")
mydb=myclient["Uber"]
user=mydb["users"]
ride=mydb["rides"]
 
@app.route('/api/v1/users',methods=['PUT']) 
def add_framework():

	username = request.json['username']
	password = request.json['password']
	y=user.find_one({"username":username})
	if(type(y)!=type(None)):
		return ('',400)
	else:
		x= hashlib.sha1(password.encode())
		password=str(x.hexdigest())
		mydict={"username":username, "password":password}
		framework_id=user.insert_one(mydict).inserted_id
		new_framework=user.find_one({"_id":framework_id})
		output={"name":new_framework["username"],"password":new_framework["password"]}
		return(jsonify({"result":output}),201)


@app.route('/api/v1/users/<username>',methods=['DELETE'])
def delete_value(username):
	y=user.find_one({"username":username})
	if(type(y)!=type(None)):
		user.delete_one({'username' : username})
		return ({},200)
	else:
		return ({},400)

	
@app.route('/api/v1/rides',methods=['POST'])
def add_rides():
	_id=request.json['id']
	username=request.json['created_by']
	timestamp=request.json['timestamp']
	source=request.json['source']
	destination=request.json['destination']
	y=user.find_one({"username":username})
	if(type(y)==type(None)):
		return ('',400)
	else:
		mydict={"id":_id,"created_by":username,"timestamp":timestamp,"source":source,"destination":destination,"usernames":[]}
		framework_id=ride.insert_one(mydict).inserted_id
		new_framework=ride.find_one({"_id":framework_id})
		output={"id":new_framework["id"],"created_by":new_framework["created_by"],"timestamp":new_framework["timestamp"],"source":new_framework["source"],"destination":new_framework["destination"]}
		return(jsonify({"result":output}),201)


@app.route('/api/v1/rides/<source>/<destination>',methods=['GET'])
def print_rides(source,destination):
	y=ride.find({"source":source,"destination":destination})
	if(type(y)==type(None)):
		return ({},400)
	else:
		result={}
		for x in y:
			output={"username":x["created_by"],"timestamp":x["timestamp"],"id":x["id"]}
			result.update(output)
	return (result,200)
	#return (str(y["destination"]))

@app.route('/api/v1/rides/<ride_id>',methods=['GET'])
def list_ride(ride_id):
	y=ride.find_one({"id":ride_id})
	if(type(y)==type(None)):
		return({},400)
	else:
		output={"rideId":y["id"],"created_by":y["created_by"],"timestamp":y["timestamp"],"source":y["source"],"destination":y["destination"],"username":y["usernames"]}
		return(output,200)
  
@app.route('/api/v1/rides/<ride_id>',methods=['DELETE'])
def delete_ride(ride_id):
	y=ride.find_one({"id":ride_id})
	if(type(y)==type(None)):
		return({},400)
	else:
		ride.delete_one({"id":ride_id})
		return({},200)


@app.route('/api/v1/rides/<ride_id>',methods=['POST'])
def add_usernames(ride_id):
	y=ride.find_one({"id":ride_id})
	if(type(y)==type(None)):
		return({},400)
	username=request.json['usernames']
	if(type(username)==type(None)):
		return({},204)
	ride.update_one({"id":ride_id},{"$addToSet":{"usernames":username}})
	return({},200)


# main driver function 
if __name__ == '__main__':  
    app.run(debug=True)
