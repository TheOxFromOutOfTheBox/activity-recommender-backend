from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pymongo
from pydantic import BaseModel,Field, EmailStr
from bson import ObjectId
import pandas as pd
from pymongoarrow.api import Schema
import time
import math
from bson.json_util import dumps, loads
import random

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    # allow_methods=["*"],
    allow_headers=["*"],
)

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class UserData(BaseModel):
    # id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str=Field(...)
    username:str=Field(...)
    email: EmailStr=Field(...)
    age: int=Field(...)

client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.po4gq8d.mongodb.net/test")
db=client['Users']


@app.get("/")
async def root():
    return{
        "message":"API is online!"
    }
@app.get("/users/getAll")
async def getAll():
    coll=db['UserData']
    print(coll)
    cursor=coll.find({},{"_id":0})
    return {"data":list(cursor)}

@app.get("/users/getOne/{username:str}")
async def getAll(username):
    coll=db['UserData']
    print(coll)
    cursor=coll.find({"username":username},{"_id":0})
    return {"data":list(cursor)}

@app.post("/users/createOne")
async def createOne(item:UserData):
    coll=db['UserData']
    print(type(item))
    coll.insert_one(dict(item))
    return {"message":"inserted successfully!"}

@app.put("/users/update/{username:str}")
async def updateOne(username,item:UserData):
    coll=db['UserData']
    coll.update_one({"username":username},{"$set":dict(item)})
    return {"message":"updated successfully!"}


# Defining filters. These filters will be made dynamic after Google api is integrated
places = ["restaurant","bar","club","cafe"]
cities = ["San Luis Potosi","Cuernavaca","Ciudad Victoria","Jiutepec","Soledad",""]
alcohol_type = ["No_Alcohol_Served","Wine-Beer","Full_Bar",""]
smoking_area = ["none","section","not permitted","permitted","only at bar"]
price_level = ["low","medium","high",""]
cuisine_type = ["American","French","Indian","Mexican","Japanese","Chinese","Italian","Greek","Spanish",""]

# Calculating the Haversine distance
def HaDist(x1, y1, x2, y2):
    # Converting latitutde and longitude to radians
    x1 = math.radians(x1)
    x2 = math.radians(x2)
    y1 = math.radians(y1)
    y2 = math.radians(y2)

    # Finding the difference between the latitude and longitude
    dx = x2 - x1
    dy = y2 - y1

    # Applying the Haversine formula
    a = math.sin(dx/2)**2 + math.cos(x1)*math.cos(x2)*math.sin(dy/2)**2
    c = 2*math.asin(math.sqrt(a))
    r = 6371    # Radius of the Earth
    return(c * r)

# Function to get the filters depending on the type of place
def getFilters(place):
    filters = {}    # Defining an empty dictionary
    filters["place"] = place    # Entering the type of place first (Eg: Restaurants, Clubs)

    # Generating random values for common filters and adding them to the dictionary
    city = random.choice(cities)
    # city=""
    price=""
    # price = random.choice(price_level)
    rating = round(random.uniform(3.25,5), 2)
    filters["city"] = city
    filters["price"] = price
    filters["rating"] = rating

    # Adding cuisine as a filter if restaurants or cafes are selected
    if(place == "cafe" or place == "restaurant"):
        # cuisine = random.choice(cuisine_type)
        cuisine=""
        filters["cuisine"] = cuisine

    # Adding alcohol and smoking as a filter if restaurants, clubs or bars are selected
    if(place == "restaurant" or place == "club" or place == "bar"):
        # alcohol = random.choice(alcohol_type)
        alcohol=""
        # smoking = random.choice(smoking_area)
        smoking=""
        filters["alcohol"] = alcohol
        filters["smoking"] = smoking

    print("Filters :",filters)      # Print the selected filters
    return filters

# Algorithm to recommend a place
def placeRecommender(lat, lon, distance, place):
    db1=client['MLModelData']
    coll=db1[place]
    cursor=coll.find()
    list_cur = list(cursor)
    series_obj = pd.Series( {"one":"index"} )
    series_obj.index = [ "one" ]
    print ("index:", series_obj.index)
    docs = pd.DataFrame(columns=[])
    for num, doc in enumerate( list_cur ):
        # convert ObjectId() to str
        doc["_id"] = str(doc["_id"])

        # get document _id from dict
        doc_id = doc["_id"]
        # create a Series obj from the MongoDB dict
        series_obj = pd.Series( doc, name=doc_id )

        # append the MongoDB Series obj to the DataFrame obj
        docs = docs.append(series_obj)
    filters = getFilters(place)     # Get the filters
    rest_set = []   # Define an array to save the results
    # For each place check the filters
    for index, row in docs.iterrows():
        
        # Calculate the distance of the place from user's location
        ha_dist = HaDist(lat, lon, float(row["latitude"]), float(row["longitude"]))

        # If distance is within the specified radius then proceed to the next filter
        if(ha_dist < distance):
            # For each filter, check if filter exists, if filter is empty, or the filter matches the place
            # Add the index number of the place to the rest_set if all conditions are satisfied
            if(filters["city"] == "" or filters["city"] == row["city"]):
                if(filters["price"] == "" or filters["price"] == row["price"]):
                    if(filters["rating"] == "" or filters["rating"] <= float(row["rating"])):
                        if("alcohol" in filters.keys() and (filters["alcohol"] == "" or filters["alcohol"] == row["alcohol"])):

                            if("smoking" in filters.keys() and (filters["smoking"] == "" or filters["smoking"] == row["smoking_area"])):
                                if("cuisine" in filters.keys() and (filters["cuisine"] == "" or filters["cuisine"] == row["Rcuisine"])):
        
                                    rest_set.append(index)

    if(len(rest_set) == 0):
        # If no places satisfy the filters, then print statement
        # print("No "+place+" available for the selected filters.")
        return placeRecommender(22.168110, -100.964089, 20, place)
    else:
        # Print names of the places if they satisfy all the conditions
        res=[]
        for rest in rest_set:
            # print(docs.iloc[[rest]]["name"])
            print(rest)
            res.append(docs[docs["_id"]==rest]["name"])
        print("res")
        return res


@app.get("/ml/hello")
async def hello():
    return {"data":"Hello to the ml model area."}


@app.get("/ml/place")
async def place():
    # place = random.choice(places)   # Choose a random type of place (Eg: Restaurants, bars, clubs, cafes)
    place="restaurant"
    res=placeRecommender(22.168110, -100.964089, 20, place)     # Run the algorithm (Static data has been chosen for now)
    return {"data":res}





# @app.delete("/users/delete/{id}")
# async def deleteOne(id):
#     coll=db['UserData']
#     delete_result=await coll.delete_one({"_id":id})
#     if (delete_result.deleted_count == 1):
#         return {"message":"deleted successfully!"}