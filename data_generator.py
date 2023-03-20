import random
import csv
activity = {
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



names = ["Alice", "Bob", "Charlie", "David", "Emily", "Frank", "Grace", "Harry", "Isabella", "Jack",
         "Karen", "Liam", "Mia", "Noah", "Olivia", "Penelope", "Quentin", "Rose", "Sophia", "Thomas",
         "Ursula", "Victoria", "William", "Xander", "Yara", "Zoe", "Avery", "Benjamin", "Caleb", "Dylan",
         "Ella", "Faith", "Gabriel", "Hannah", "Isaac", "Jacob", "Kaitlyn", "Landon", "Madison", "Nathan",
         "Owen", "Piper", "Quinn", "Riley", "Samuel", "Tessa", "Uriel", "Violet", "Wyatt", "Xavier"]

categories = ["parks", "museums", "galleries", "shopping centers", "theaters", "amusement_parks",
              "swimming_pools", "sports_clubs", "salons", "cinemas", "bars", "restaurants", "clubs" ,"cafes"]


cuisine = ["Any", "Indian", "Seafood", "Italian", "Japanese - Sushi", "Chinese", "Mexican",
                    "Thai", "French", "Middle Eastern", "Vietnamese", "Hamburger", "Pizza"]


def select_random_places(activity):
    activities = []
    for key in random.sample(list(activity.keys()), 3):
        activities.append(random.choice(activity[key]))
    return activities

with open("activities.csv", "w", newline="") as file:
    writer = csv.writer(file)


    writer.writerow(["Name", "Time", "3Categories", "Budget", "Cuisine", "Bar Payment", "Top Recommendations"])


    for i in range(3000):

        name = random.choice(names)
        time = random.randint(1, 6)
        top_3_categories = random.sample(categories, 3)
        budget = random.randint(50, 300)
        cuisine = random.choice(cuisine)
        bar_payment = random.choice(["cash", "credit card", "debit card"])
        places_recommendation = select_random_places(activity)
        writer.writerow([name, time, top_3_categories, budget, cuisine, bar_payment,places_recommendation])

print("CSV file generated successfully!")



