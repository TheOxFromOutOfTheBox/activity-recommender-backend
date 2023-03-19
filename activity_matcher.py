import csv
import random

import requests
import json
from geolocation.main import GoogleMaps
# pip install geolocation-python


def get_current_location():
    location = GoogleMaps(api_key='YOUR_API_KEY').get_location()
    return location['lat'], location['lng']

def get_google_data(latitude, longitude):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key=YOUR_API_KEY"
    response = requests.get(url)
    data = json.loads(response.text)
    return data


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
    "cinema": ["Cinéma Banque Scotia", "Cinéma Cineplex Forum", "Cinéma du Parc", "Cinéma Guzzo", "Cinéma Impérial", "Cinéma Beaubien", "Cinéma Starcité Montréal"]
}

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


name = input("What is your name? ")
time = int(input("How many hours do you have? (1-6) "))
activity_list = ["parks", "museums", "galleries", "shopping centers", "theaters", "amusement_parks", "swimming_pools", "sports_clubs", "salons", "cinemas", "bars", "restaurants", "clubs","cafes"]
options = []

print("Activity Options:")
for i in range(len(activity_list)):
    print(f"{i+1}. {activity_list[i]}")
for i in range(3):
    option = int(input(f"Please select your option {i+1} (1-14): "))
    category = ["parks", "museums", "galleries", "shopping centers", "theaters", "amusement_parks", "swimming_pools", "sports_clubs", "salons", "cinemas", "bars", "restaurants", "clubs" ,"cafes"][option-1]
    options.append(category)
    if category == "restaurants":
        cuisines = ["Any", "Indian", "Seafood", "italian", "Japanese", "Sushi", "Chinese", "Mexican", "Thai", "French", "Middle Eastern", "Vietnamese", "Hamburger", "Pizza"]
        print("Cuisine options:")
        for i in range(len(cuisines)):
            print(f"{i+1}. {cuisines[i]}")
        cuisine = int(input("Which cuisine would you like to have? (1-14): "))
        if cuisine >= 1 and cuisine <= 14:
            cuisine = cuisines[cuisine-1]
        else:
            cuisine = None
    elif category == "bars":
        print("The options for bar payment:")
        payment = ["$", "$$", "$$$", "$$$$"]
        for i in range(len(payment)):
            print(f"{i+1}. {payment[i]}")
        payment =  (input("Select range out of 4 options: "))

budget = int(input("How much would you like to spend? (CAD) "))
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

    
if len(matches) > 0:
    print(f"Potential matches for {name}: {', '.join(matches)} and they like to visit {options} also they should meet at {recommended}")
else:
    print(f"No matches found for {name}.")
