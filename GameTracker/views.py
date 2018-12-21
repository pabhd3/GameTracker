import sys
from django.shortcuts import render, redirect
from mongoengine.context_managers import switch_db
from .forms import *

# Import views
sys.path.insert(0, "/skyrimse/")
from skyrimse.models import *

# Create your views here.
def index(request):
    data = {}
    # Load Skyrim Data
    data["skyrimse"] = sum([(doc["completion"]["vanilla"] + doc["completion"]["mod"])/2 for doc in Progress.objects.all()])/6
    return render(request, 'index.html', {'data': data})

def search(request):
    if(request.method == "POST"):
        form = Search(request.POST)
        if(form.is_valid()):
            data = {"Skyrim SE": {}}
            searchTerm = form.cleaned_data["search"]
            # Search SkyrimSE Documents
            documents = [{"group": "Quests", "type": Quest, "url": "/skyrimse/quests"}, {"group": "Perks", "type": Perk, "url": "/skyrimse/perks"}, 
                {"group": "Shouts", "type": Shout, "url": "/skyrimse/shouts"}, {"group": "Locations", "type": Location, "url": "/skyrimse/locations"}, 
                {"group": "Spells", "type": Spell, "url": "/skyrimse/spells"}, {"group": "Enchantments", "type": Enchantment, "url": "/skyrimse/enchantments"}, 
                {"group": "Ingedients", "type": Ingredient, "url": "/skyrimse/ingredients"}, {"group": "Weapons", "type": Weapon, "url": "/skyrimse/weapons"}, 
                {"group": "Armors", "type": Armor, "url": "/skyrimse/armors"}, {"group": "Jewelry", "type": Jewelry, "url": "/skyrimse/jewelry"}, 
                {"group": "Books", "type": Book, "url": "/skyrimse/books"}, {"group": "Keys", "type": Key, "url": "/skyrimse/keys"}, 
                {"group": "Collectibles", "type": Collectible, "url": "/skyrimse/collectibles"}] 
            for obj in documents:
                for result in obj["type"].objects.search_text(searchTerm):
                    if(not data["Skyrim SE"].get(obj["group"])):
                        data["Skyrim SE"][obj["group"]] = []
                    if("quests" in obj["url"]):
                        url = "{base}/{source}-{questLine}".format(base=obj["url"], source=result["source"], questLine=result["questLine"])
                    elif("perks" in obj["url"]):
                        url = "{base}/{source}-{skill}".format(base=obj["url"], source=result["source"], skill=result["skill"])
                    elif("spells" in obj["url"]):
                        url = "{base}/{source}-{school}".format(base=obj["url"], source=result["source"], school=result["school"])
                    elif("enchantments" in obj["url"]):
                        url = "{base}/{source}-{enchantmentType}".format(base=obj["url"], source=result["source"], enchantmentType=result["enchantmentType"])
                    elif("weapons" in obj["url"]):
                        url = "{base}/{source}-{type}".format(base=obj["url"], source=result["source"], type=result["weaponType"])
                    elif("armors" in obj["url"]):
                        url = "{base}/{source}-{type}".format(base=obj["url"], source=result["source"], type=result["armorType"])
                    elif("jewelry" in obj["url"]):
                        url = "{base}/{source}-{type}".format(base=obj["url"], source=result["source"], type=result["jewelryType"])
                    elif("books" in obj["url"]):
                        url = "{base}/{startsWith}".format(base=obj["url"], startsWith=result["startsWith"])
                    elif("keys" in obj["url"]):
                        url = "{base}/{source}-{location}".format(base=obj["url"], source=result["source"], location=result["location"])
                    elif("collectibles" in obj["url"]):
                        url = "{base}/{source}-{type}".format(base=obj["url"], source=result["source"], type=result["collectibleType"])
                    else: # Shouts, Locations, Ingredients
                        url = "{base}/{source}".format(base=obj["url"], source=result["source"])
                    data["Skyrim SE"][obj["group"]].append({"name": result["name"], "url": url})
            return render(request, 'searchResults.html', {'data': data})
    return redirect("/")