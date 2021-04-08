from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import requests
import numpy
import tensorflow as tf
import json
import subprocess

app=Flask(__name__)
api=Api(app)

client=MongoClient("mongodb://db:27017")
db=client.ImageRecognizeDB
users=db["Users"]
admin=db["Admin"]


def verify_usr(usr):
    
    if users.find({"Username":usr}).count()==0:
        return False
    else:
        return True
    
def verify_pw(usr,pwd):
    hashed_pw=users.find({"Username": usr})[0]["Password"]
    
    if bcrypt.hashpw(pwd.encode("utf8"),hashed_pw) == hashed_pw:
        
        return True
    else:
        return False
    
    
def verify_credentials(usr,pwd):
    
    chk_usr=verify_usr(usr)
    
    if not chk_usr:
        return jsonify(generate_retjson(301,"Invalid user!")), True
    
    
    chk_pwd = verify_pw(usr, pwd)
    
    if not chk_pwd:
        return jsonify(generate_retjson(302,"Invalid Credentials!")), True
    else:
        return None, False
        
    
'''   
    hashed_pw=users.find({"Username": usr})[0]["Password"]
    
    if bcrypt.hashpw(pwd.encode("utf8"),hashed_pw) == hashed_pw:
        
        return None, False
    
    else:
        return jsonify(generate_retjson(302,"Invalid Credentials!")), True
'''        
    
def generate_retjson(status,msg):
    
    retJson={
                "status": status, "Message": msg
            }
    return retJson


def count_tk(usr):
    tk= users.find({"Username":usr})[0]["Tokens"]
    return tk
        
def verify_admin(pwd):
    
    hashed_pwd=admin.find({"Username":"root"})[0]["Password"]
    
    if bcrypt.hashpw(pwd.encode("utf8"), hashed_pwd) == hashed_pwd:
        
        return True
    else:
        return False
    
    

class Register(Resource):
    def post (self):
        d=request.get_json()
        usr=d["username"]
        pwd=d["password"]
        
        chk_usr=verify_usr(usr)
        
        if chk_usr :
            retJson={"status":301, "Message": "Sorry, user already exists"}
            return jsonify(retJson)
        
        hash_pwd=bcrypt.hashpw(pwd.encode('utf8'),bcrypt.gensalt())
        
        users.insert({"Username":usr,"Password": hash_pwd, "Tokens":5 })
        
        retJson={"status":200, "Message": "User registered successfully!"}
        return jsonify(retJson)
        
class Classify(Resource):
    def post(self):
        d=request.get_json()
        usr=d["username"]
        pwd=d["password"]
        url=d["url"]
        
        retJson, error= verify_credentials(usr,pwd)
        
        if error:
            return retJson
            
        tokens= count_tk(usr)
        
        if tokens <= 0:
            return(jsonify(generate_retjson(303,"Out of tokens!")))
            
        r=requests.get(url)
        retJson={}
        with open("temp.jpg","wb") as f:
            f.write(r.content)
        
        
        proc= subprocess.Popen("python classify_image.py --model_dir=. --image_file=./temp.jpg", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        proc.communicate()[0]
        proc.wait()
        
        with open("text.txt") as g:
            retJson=json.load(g)
        
            
        users.update({"Username": usr},{"$set":{"Tokens": tokens - 1}})
        
        return retJson
        
class Refill(Resource):
    def post(self):
        d=request.get_json()
        usr=d["username"]
        pwd=d["admin_pwd"]
        
        refill=d["refill_amt"]
        
        chk_usr=verify_usr(usr)
        if not chk_usr:
            return jsonify(generate_retjson(301,"User doesn't exist"))
        
        chk_admin= verify_admin(pwd)
        
        if not chk_admin:
            return jsonify(generate_retjson(304,"Invalid Administrator Password!"))
        
        tokens=count_tk(usr)
        
        users.update({"Username":usr},{"$set":{ "Tokens": tokens + refill }})
        
        return jsonify(generate_retjson(200, "Refilled successfully!"))
        
        
api.add_resource(Register,'/register')
api.add_resource(Classify,'/classify')
api.add_resource(Refill,'/refill')


if __name__== "__main__":
    
    if admin.find({"Username":"root"}).count() == 0:
        
        hash_pw=bcrypt.hashpw("abc123".encode("utf8"), bcrypt.gensalt() )
        admin.insert({"Username": "root", "Password": hash_pw })
    
    app.run(host="0.0.0.0")
            
        
        
        
        
        
        