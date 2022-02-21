from fastapi import FastAPI
from pydantic import BaseModel
import boto3
import hashlib
from mangum import Mangum

app = FastAPI()

class User (BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str

app = FastAPI()
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("project-users")


@app.post("/users/")
async def create_item(user: User):

    table.put_item(
        Item={
            "username":user.username,
            "password":hashlib.sha512(user.password.encode()).hexdigest(),
            "first_name":user.first_name,
            "last_name":user.last_name
            
        }
    )

    item_retrieved = table.get_item(Key={"username": user.username})

    return item_retrieved["Item"], 200

@app.get("/users/")
async def get_users(username):

    item_retrieved = table.get_item(Key={"username": username})
    if "Item" in item_retrieved.keys():
        return item_retrieved["Item"], 200
    return {"error": "item not found"}, 404

@app.post("/login/")
async def login(username, password):
    item_retrieved = table.get_item(Key={"username": username})

    if "Item" not in item_retrieved.keys():
        return ({"login": None}), 401
    
    if "password" not in item_retrieved["Item"]:
        return ({"login": None }), 401
        
    password = hashlib.sha512(password.encode()).hexdigest()
    if password != item_retrieved["Item"]["password"]:
        return ({"login": False}), 403

    return ({"login": True}), 200

    
handler = Mangum(app)
