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
                objList = []
                for result in obj["type"].objects.search_text(searchTerm):
                    if(not data["Skyrim SE"].get(obj["group"])):
                        data["Skyrim SE"][obj["group"]] = []
                    url = "{base}/details/{name}".format(base=obj["url"], name=result["name"])
                    objList.append({"name": result["name"], "source": result["source"], "url": url})
                data["Skyrim SE"][obj["group"]] = sorted(objList, key=lambda k: k["name"])
            return render(request, 'searchResults.html', {'data': data})
    return redirect("/")