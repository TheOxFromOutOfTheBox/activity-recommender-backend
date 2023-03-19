from fastapi import FastAPI,Request
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
import requests
import json
from io import BytesIO
import csv

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# class PyObjectId(ObjectId):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, v):
#         if not ObjectId.is_valid(v):
#             raise ValueError("Invalid objectid")
#         return ObjectId(v)

#     @classmethod
#     def __modify_schema__(cls, field_schema):
#         field_schema.update(type="string")

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




@app.post('/test')
async def test(request:Request):
    json_data = await request.body()
    a=BytesIO(json_data)
    data=json.loads(a.getvalue())
    print(data)
    latitude=data['latitude']
    longitude=data['longitude']
    radius=data['radius']
    activity=data['activity']
    print(f'activiity is {activity}')
    open_now=data['opennow']
    API_KEY='AIzaSyAdPKAhAgQP53GPUmaNIaeVd7icH2EEXhg'
    b={
        "Bars":"bar",
        "Amusement Parks":"amusement_park",
        "Beauty Salons":"beauty_salon",
        "Cafe":"cafe",
        "Cinemas":"cinema",
        "Clubs":"club",
        "Galleries":"gallery",
        "Museums":"museum",
        "Parks":"park",
        "Restaurants":"restaurant",
        "Shopping Centres":"shopping_center",
        "Sports Club":"sports_club",
        "Swimming pools":"swimming_pool",
        "Theatres":"theater"
    }
    a={
        'bar':f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude}%2C{longitude}&radius={radius}&type=bar&keyword=bar&key=',
        'theater':f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude}%2C{longitude}&radius={radius}&type=movie_theater&keyword=movie%20theater&key=',
        'sports_club':f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude}%2C{longitude}&radius={radius}&type=gym&keyword=gym&key=',
        'cafe':f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude}%2C{longitude}&radius={radius}&type=cafe&keyword=cafe&key=',
        'gallery':f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude}%2C{longitude}&radius={radius}&type=gallery&keyword=gallery&key=',
        'park':f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude}%2C{longitude}&radius={radius}&type=park&keyword=park&key=',
        'museum':f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude}%2C{longitude}&radius={radius}&type=museum&keyword=museum&key=',
        'beauty_salon':f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude}%2C{longitude}&radius={radius}&type=beauty_salon&keyword=beauty%20salon&key=',
        'restaurant':f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude}%2C{longitude}&radius={radius}&type=restaurant&keyword=restaurant&key=',
        'shopping_center':f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude}%2C{longitude}&radius={radius}&type=mall&keyword=mall&key=',
        'swimming_pools':f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude}%2C{longitude}&radius={radius}&type=swimming_pools&keyword=swimming%20pools&key=',
        'club':f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude}%2C{longitude}&radius={radius}&type=club&keyword=club&key=',
        'cinema':f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude}%2C{longitude}&radius={radius}&type=cinema&keyword=cinema&key=',
        'amusement_park':f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude}%2C{longitude}&radius={radius}&type=amusement_park&keyword=amusement%20park&key='

    }
    r1=requests.get(f'{a[b[activity]]}{API_KEY}&opennow={open_now}')
    # print(r1.content)
    return {"data":r1.json()}

# @app.delete("/users/delete/{id}")
# async def deleteOne(id):
#     coll=db['UserData']
#     delete_result=await coll.delete_one({"_id":id})
#     if (delete_result.deleted_count == 1):
#         return {"message":"deleted successfully!"}

@app.post('/getMatching')
async def getMatching(request:Request):
    json_data = await request.body()
    a=BytesIO(json_data)
    data=json.loads(a.getvalue())
    print(data)
    activity_dict = {
     "parks": ["Mount Royal Park", "La Fontaine Park", "Parc des Rapides", "Parc Jean-Drapeau", "Parc Jarry"],
    "museums": ["Musée des beaux-arts de Montréal", "Biodome de Montreal", "Barbie Expo", "Pointe-a-Calliere, Montreal Archaeology and History Complex", "Museum of Jewish Montreal", "Chateau Ramezay Historic Site and Museum of Montreal", "Insectarium de Montréal", "Montreal Science Centre"],
    "galleries": ["Fondation Phi", "L'Affichiste Vintage Poster Gallery", "Galerie d'art Blanche", "Galerie Images Boreales", "Galerie Bloom", "Espace Culturel Ashukan", "Beaverbrook Art Gallery, Fredericton, New Brunswick", "Musee d'art contemporain de Montreal, Montreal, Quebec", "Art Gallery of Nova Scotia, Halifax, Nova"],
    "shopping_centers": ["Promenades Cathédrale", "Alexis Nihon", "Galeries d'Anjou", "Place Versailles", "Complexe Desjardins", "Marché Central", "Centre Rockland", "Premium Outlets Montréal"],
    "theatres": ["Centaur Theatre", "IMAX Old Port", "Braquage Ezkapaz", "Tohu", "Theatre St-Denis", "Théâtre Rialto", "Segal"],
    "amusement_parks": ["Aquazilla", "La Ronde", "Voiles en Voiles", "PI-O Amusement Park", "Elevation Trampoline & Amusement Park", "Au Pays Des Merveilles"],
    "swimming_pools": ["Piscine John-F.", "Parc du Pélican", "Piscine Lévesque", "Piscine Saint-Charles", "Piscine du Cégep Vieux Montréal", "Piscine Saint-Roch", "Piscine Maisonneuve", "Confederation Park Pool"],
    "sports_clubs": ["Les Chickens - Club de triathlon", "Apneacity - Freediving School", "Club de Ski Snow de l'Université de Montréal"],
    "salons": ["Salon Deauville Coiffure & Spa", "Au Premier Coiffure Spa", "Le Salon Rose Doré", "Deauville au Masculin", "Salon Beurling", "Fusion 2000 Coiffure Inc"],
    "clubs": ["Les Chickens - Club de triathlon", "Apneacity - Freediving School", "Club de Ski Snow de l'Université de Montréal"],
    "cafes": ["Café Olimpico", "Café Myriade", "Café Parvis", "Café Névé", "Café Pista"],
    "bars": ["Brasserie Harricana", "Le Mal Nécessaire", "Furco", "Le 4e Mur", "Bar le Lab"],
    "restaurants": ["Toqué!", "Joe Beef", "Le Mousso", "Au Pied de Cochon", "L'Express"],
    "cinema": ["Cinéma Banque Scotia", "Cinéma Cineplex Forum", "Cinéma du Parc", "Cinéma Guzzo", "Cinéma Impérial", "Cinéma Beaubien", "Cinéma Starcité Montréal"]}

    cuisines_dict = {
        "Any":["Toqué!", "Joe Beef", "Le Mousso", "Au Pied de Cochon", "L'Express","McGill Pizzeria", "Pizza Il Focolaio", "Pizza Dany", "Wienstein & Gavino's", "Pizza Bella","MIDDLE EAST RESTAURANT", "Mezze", "Arabian Terrace - Multi Cuisine", "Q3 ARABIAN","Pamika", "Mae Sri Comptoir Thai", "Tiramisu","Parma Café", "Beatrice", "Café Il Cortile", "Da Vinci Restaurant", "Trattoria Trestevere", "Wienstein & Gavino's","Royal Biryani Restaurant", "Madras Curry House", "Maison ChaïShaï", "Le Taj", "Curry Mahal","Restaurant La Mer Rouge", "Le Filet", "Garde Manger", "Ferreira Café", "Chez Delmo"],
        "Indian": ["Royal Biryani Restaurant", "Madras Curry House", "Maison ChaïShaï", "Le Taj", "Curry Mahal"],
        "Seafood": ["Restaurant La Mer Rouge", "Le Filet", "Garde Manger", "Ferreira Café", "Chez Delmo"],
        "Italian": ["Parma Café", "Beatrice", "Café Il Cortile", "Da Vinci Restaurant", "Trattoria Trestevere", "Wienstein & Gavino's"],
        "Japanese": ["KINKA IZAKAYA MONTREAL", "Sushi Okeya Kyujiro", "K2+ Bistro", "Otto Yakitori Izakaya", "YEN CUISINE JAPONAISE"],
        "Chinese": ["Sammi & Soupe Dumpling", "Chez Chen", "Restaurant Shi Tang", "Cuisine AuntDai", "Mr. Gao"],
        "Mexican": ["M4 Burritos Concordia", "La Capital Tacos", "Tacos Frida", "La Cantina"],
        "Thai": ["Pamika", "Mae Sri Comptoir Thai", "Tiramisu"],
        "Sushi": ["KINKA IZAKAYA MONTREAL", "Sushi Okeya Kyujiro", "K2+ Bistro", "Otto Yakitori Izakaya", "YEN CUISINE JAPONAISE"],
        "French": ["Renoir Restaurant", "Le Pois Penche", "L’Autre Saison", "Tiramisu"],
        "Middle Eastern": ["MIDDLE EAST RESTAURANT", "Mezze", "Arabian Terrace - Multi Cuisine", "Q3 ARABIAN"],
        "Vietnamese": ["Pho Bac", "Pho Nguyen", "Restaurant I AM Pho"],
        "Hamburger": ["Dunn's Famous", "Burger Bar Crescent", "Notre-Boeuf-de-Grâce", "La Belle & La Boeuf"],
        "Pizza": ["McGill Pizzeria", "Pizza Il Focolaio", "Pizza Dany", "Wienstein & Gavino's", "Pizza Bella"]
    }


    with open('activities.csv', 'r') as f:
        reader = csv.DictReader(f)
        activities = list(reader)

    def recommend_places(activity_list, cuisine=None):
        for activity in activity_list:
            if activity == 'restaurants' and cuisine:
                places = cuisines_dict[cuisine]
                return random.choice(places)
            elif activity in activity_dict:
                places = activity_dict[activity]
                return random.choice(places)
        return "No places found for given activities."


    # name = input("What is your name? ")
    name="KMH"
    # time = int(input("How many hours do you have? (1-6) "))
    time=4
    activity_list = ["parks", "museums", "galleries", "shopping centers", "theaters", "amusement_parks", "swimming_pools", "sports_clubs", "salons", "cinemas", "bars", "restaurants", "clubs","cafes"]
    options = []

    # print("Activity Options:")
    # for i in range(len(activity_list)):
    #     print(f"{i+1}. {activity_list[i]}")
    for i in range(3):
        # option = int(input(f"Please select your option {i+1} (1-14): "))
        option=11
        category =activity_list[option-1]
        options.append(category)
        if category == "restaurants":
            cuisines = ["Any", "Indian", "Seafood", "italian", "Japanese", "Sushi", "Chinese", "Mexican", "Thai", "French", "Middle Eastern", "Vietnamese", "Hamburger", "Pizza"]
            print("Cuisine options:")
            # for i in range(len(cuisines)):
            #     print(f"{i+1}. {cuisines[i]}")
            # cuisine = int(input("Which cuisine would you like to have? (1-14): "))
            cuisine=10
            if cuisine >= 1 and cuisine <= 14:
                cuisine = cuisines[cuisine-1]
            else:
                cuisine = None
        elif category == "bars":
            # print("The options for bar payment:")
            # payment = ["$", "$$", "$$$", "$$$$"]
            # for i in range(len(payment)):
            #     print(f"{i+1}. {payment[i]}")
            # payment =  (input("Select range out of 4 options: "))
            payment="$$"

    # budget = int(input("How much would you like to spend? (CAD) "))
    budget=4000
    matches = []
    for activity in activities:
        if int(activity["Budget"]) > budget:
            continue
        categories = eval(activity["3Categories"])
        if set(options).intersection(categories) != set(options):
            continue
        if int(activity["Time"]) > time:
            continue
        matches.append(activity["Name"])


    if 'cuisine' in locals():
        recommended = recommend_places(options, cuisine)
    else:
        recommended = recommend_places(options)
    matches=list(set(matches))
        
    if len(matches) > 0:
        print(f"Potential matches for {name}: {', '.join(matches)} and they like to visit {options} also they should meet at {recommended}")
    else:
        print(f"No matches found for {name}.")
    return {
        "matches":matches,
        "recommended":recommended
    }
