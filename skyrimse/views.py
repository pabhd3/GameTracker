from django.http import HttpResponse
from django.shortcuts import render, redirect
from skyrimse.models import *
from mongoengine.context_managers import switch_db
from datetime import datetime
from .customScripts import plotRadars
from json import load, loads, dumps
import os

#####################
##### Home Page #####
#####################
def index(request):
    return render(request, 'skyrimseIndex.html')

############################
##### Progress Related #####
############################
def progress(request):
    switch_db(cls=Progress, db_alias="skyrimse")
    # Pull list of progress objects
    docs = Progress.objects.all()
    data = {"novice": None, "apprentice": None, "adept": None,
            "expert": None, "master": None, "legendary": None}
    # Set whether an object exists
    for doc in docs:
        data[doc.difficulty] = {"level": doc.level, "health": doc.health, 
            "magicka": doc.magicka,"stamina": doc.stamina,
            "completion": {"vanilla": doc.completion.vanilla, "mod": doc.completion.mod}}
    return render(request, 'skyrimseProgress.html', {'data': data})

def addDifficulty(request):
    # Start a new progress object
    progress = Progress()
    # Pull difficulty from HTTP Request.path
    difficulty = request.path.split("=")[1]
    # Set/save starting info for a progress object
    progress.created = datetime.strftime(datetime.now(), "%A %B %d, %Y %H:%M:%S:%f %Z")
    progress.difficulty = difficulty
    progress.level = 0
    progress.health = 0
    progress.magicka = 0
    progress.stamina = 0
    progress.completion = Completion(vanilla=0, mod=0)
    progress.skills = Skills(alchemy=Skill(level=0, legendary=0), alteration=Skill(level=0, legendary=0), 
            archery=Skill(level=0, legendary=0), block=Skill(level=0, legendary=0), 
            conjuration=Skill(level=0, legendary=0), destruction=Skill(level=0, legendary=0), 
            enchanting=Skill(level=0, legendary=0), heavyArmor=Skill(level=0, legendary=0), 
            illusion=Skill(level=0, legendary=0), lightArmor=Skill(level=0, legendary=0), 
            lockpicking=Skill(level=0, legendary=0), oneHanded=Skill(level=0, legendary=0), 
            pickPocket=Skill(level=0, legendary=0), restoration=Skill(level=0, legendary=0), 
            smithing=Skill(level=0, legendary=0), sneak=Skill(level=0, legendary=0), 
            speech=Skill(level=0, legendary=0), twoHanded=Skill(level=0, legendary=0))
    questCount = sum([len(Quest.objects(source=source)) for source in ["vanilla", "dawnguard", "dragonborn", "hearthfire"]])
    modQuestCount = len(Quest.objects.all()) - questCount
    perkCount = sum([len(Perk.objects(source=source)) for source in ["vanilla", "dawnguard", "dragonborn", "hearthfire"]])
    modPerkCount = len(Perk.objects.all()) - perkCount
    wordCount = sum([len(Shout.objects(source=source)) for source in ["vanilla", "dawnguard", "dragonborn", "hearthfire"]]) * 3
    modWordCount = (len(Shout.objects.all()) * 3) - wordCount
    locationCount = sum([len(Location.objects(source=source)) for source in ["vanilla", "dawnguard", "dragonborn", "hearthfire"]])
    modLocationCount = (len(Location.objects.all())) - locationCount
    spellCount = sum([len(Spell.objects(source=source)) for source in ["vanilla", "dawnguard", "dragonborn", "hearthfire"]])
    modSpellCount = (len(Spell.objects.all())) - spellCount
    enchantmentCount = sum([len(Enchantment.objects(source=source)) for source in ["vanilla", "dawnguard", "dragonborn", "hearthfire"]])
    modEnchantmentCount = (len(Enchantment.objects.all())) - enchantmentCount
    ingredientCount = sum([len(Ingredient.objects(source=source)) for source in ["vanilla", "dawnguard", "dragonborn", "hearthfire"]])
    modIngredientCount = (len(Ingredient.objects.all())) - ingredientCount
    totalCount = sum([questCount, perkCount, wordCount, locationCount, spellCount, enchantmentCount,
        ingredientCount])
    modTotalCount = sum([modQuestCount, modPerkCount, modWordCount, modLocationCount, modSpellCount,
        modEnchantmentCount, modIngredientCount])
    progress.collected = Collected(quests=0, modQuests=0, perks=0, modPerks=0, 
        words=0, modWords=0, locations=0, modLocations=0, spells=0, modSpells=0, enchantments=0,
        modEnchantments=0, ingredients=0, modIngredients=0,total=0, modTotal=0)
    progress.collectedTotal = Collected(quests=questCount, modQuests=modQuestCount, perks=perkCount, 
        words=wordCount, modWords=modWordCount, modPerks=modPerkCount, locations=locationCount, 
        modLocations=modLocationCount, spells=spellCount, modSpells=modSpellCount, 
        enchantments=enchantmentCount, modEnchantments=modEnchantmentCount, ingredients=ingredientCount, 
        modIngredients=modIngredientCount, total=totalCount, modTotal=modTotalCount)
    progress.save()
    # Generate a Radar Graph for the progress
    skillLevels = {"Alchemy": 0, "Alteration": 0, "Archery": 0, "Block": 0, "Conjuration": 0, 
        "Destruction": 0, "Enchanting": 0, "Heavy Armor": 0, "Illusion": 0, "Light Armor": 0, 
        "Lockpicking": 0, "One-Handed": 0, "Pickpocket": 0, "Restoration": 0, "Smithing": 0, 
        "Sneak": 0, "Speech": 0, "Two-Handed": 0}
    plotRadars(values=skillLevels, difficulty=progress.difficulty)
    return redirect("/skyrimse/progress")

def deleteDifficulty(request):
    # Pull progress.id from HTTP request.path
    deleteID = request.path.split("=")[1]
    progress = Progress.objects(id=deleteID).first()
    # Delete the Radar Graph graph
    for area in ["combat", "magic", "stealth"]:
        strFile = "skyrimse/static/images/progress/{area}-skills-{difficulty}.png".format(area=area, difficulty=progress.difficulty)
        if(os.path.isfile(strFile)):
            os.remove(strFile)
    progress.delete()
    # Delete Quest Data
    for quest in Quest.objects.all():
        quest["completion"][progress.difficulty] = 0
        quest.save()
    # Delete Perk Data
    for perk in Perk.objects.all():
        perk["completion"][progress.difficulty] = 0
        perk.save
    return redirect("/skyrimse/progress")

def levelSkill(request):
    # Pull skill and difficulty from HTTP request.path
    paramsStr = request.path.split("/skyrimse/progress/")[1]
    skill = paramsStr.split("&")[0].split("=")[1]
    difficulty = paramsStr.split("&")[1].split("=")[1]
    levelType = paramsStr.split("&")[2].split("=")[1]
    progress = Progress.objects(id=difficulty).first()
    # Update skill level
    if(levelType == "level"):
        progress["skills"][skill]["level"] += 1
    else:
        progress["skills"][skill]["level"] = 0
        progress["skills"][skill]["legendary"] += 1
    progress.save()
    # Pull levels for new Radar Graph
    skillLevels = {"Alchemy": progress.skills.alchemy.level, "Alteration": progress.skills.alteration.level, 
        "Archery": progress.skills.archery.level, "Block": progress.skills.block.level, 
        "Conjuration": progress.skills.conjuration.level, "Destruction": progress.skills.destruction.level, 
        "Enchanting": progress.skills.enchanting.level, "Heavy Armor": progress.skills.heavyArmor.level, 
        "Illusion": progress.skills.illusion.level, "Light Armor": progress.skills.lightArmor.level, 
        "Lockpicking": progress.skills.lockpicking.level, "One-Handed": progress.skills.oneHanded.level, 
        "Pickpocket": progress.skills.pickPocket.level, "Restoration": progress.skills.restoration.level, 
        "Smithing": progress.skills.smithing.level, "Sneak": progress.skills.sneak.level, 
        "Speech": progress.skills.speech.level, "Two-Handed": progress.skills.twoHanded.level}
    plotRadars(values=skillLevels, difficulty=progress.difficulty)
    return redirect("/skyrimse/progress/{difficulty}".format(difficulty=progress.difficulty))

def progressDetail(request):
    # Pull id from HTTP request.path
    progressID = request.path.split("/skyrimse/progress/")[1]
    progress = Progress.objects(difficulty=progressID).first()
    data = {"id": progress.id, "difficulty": progress.difficulty, "created": progress.created, 
        "skills": {"combat": {}, "magic": {}, "stealth": {}}, "stats": {}}
    for skill in progress.skills:
        if(skill in ["archery", "block", "heavyArmor", "oneHanded", "smithing", "twoHanded"]):
            area = "combat"
        elif(skill in ["alteration", "conjuration", "destruction", "enchanting", "illusion", "restoration"]):
            area = "magic"
        else:
            area = "stealth"
        data["skills"][area][skill] = {"level": progress["skills"][skill]["level"],
            "legendary": progress["skills"][skill]["legendary"]}
    for stat in progress.collected:
        data["stats"][stat] = {"collected": progress["collected"][stat], 
            "total": progress["collectedTotal"][stat]}
    return render(request, "skyrimseProgressDetail.html", {'data': data})

def refreshProgress(request):
    return(HttpResponse("Test"))

def levelProgress(request):
    # Pull stat and difficulty to level up
    paramStr = request.path.split("/skyrimse/progress/")[1]
    stat = paramStr.split("&")[0].split("=")[1]
    difficulty = paramStr.split("&")[1].split("=")[1]
    # Pull the progress object
    progress = Progress.objects(difficulty=difficulty).first()
    if(stat == "level"):
        progress.update(inc__level=1)
    elif(stat == "health"):
        progress.update(inc__health=10)
    elif(stat == "magicka"):
        progress.update(inc__magicka=10)
    elif(stat == "stamina"):
        progress.update(inc__stamina=10)
    progress.save()
    return redirect("/skyrimse/progress")

##########################
##### Quests Related #####
##########################
def quests(request):
    # Pull all the quests, quest's cources, and quest's questlines
    allQuests = Quest.objects.all()
    allSources = set([q.source for q in allQuests])
    allQuestLines = set([q.questLine for q in allQuests])
    # Dynamically load quest sources
    questFiles = list(filter(lambda x: "Quests" in x, [f for f in os.listdir('skyrimse/static/json/quests/')]))
    data = {"counts": {}, "sources": {}}
    for f in questFiles:
        source = f.replace("Quests.json", "")
        data["counts"][source] = len(Quest.objects(source=source))
    # Sort questlines into sources, and get counts per difficulty per questline
    for source in allSources:
        data["sources"][source] = {}
        for quest in allQuests:
            if(quest.questLine not in data["sources"][source] and quest.source == source):
                total = len(Quest.objects(questLine=quest.questLine, source=source))
                progData = {"novice": {"complete": len(Quest.objects(questLine=quest.questLine, source=source, completion__novice__gt=0)), 
                            "total": total},
                            "apprentice": {"complete": len(Quest.objects(questLine=quest.questLine, source=source, completion__apprentice__gt=0)), 
                            "total": total},
                            "adept": {"complete": len(Quest.objects(questLine=quest.questLine, source=source, completion__adept__gt=0)), 
                            "total": total},
                            "expert": {"complete": len(Quest.objects(questLine=quest.questLine, source=source, completion__expert__gt=0)), 
                            "total": total},
                            "master": {"complete": len(Quest.objects(questLine=quest.questLine, source=source, completion__master__gt=0)), 
                            "total": total},
                            "legendary": {"complete": len(Quest.objects(questLine=quest.questLine, source=source, completion__legendary__gt=0)), 
                            "total": total}}
                data["sources"][source][quest.questLine] = progData
    return render(request, "skyrimseQuests.html", {'data': data})

def questsLoad(request):
    # Pull data from JSON file
    toLoad = "skyrimse/static/json/quests/{source}Quests.json".format(source=request.path.split("=")[1])
    with open(file=toLoad, mode="r") as f:
        jsonData = load(f)
        f.close()
    # Create and save a Quest object
    for questData in jsonData:
        quest = Quest(name=questData["name"], questLine=questData["questLine"], source=questData["source"],
                      section=questData["section"], radiant=questData["radiant"],
                      completion = Tracker(novice=0, apprentice=0, adept=0, expert=0, master=0, legendary=0))
        quest.save()
    return redirect("/skyrimse/quests")

def questLine(request):
    # Pull source and questline from HTTP request.path
    questSource = request.path.replace("/skyrimse/quests/", "").split("-")[0]
    questLine = request.path.replace("/skyrimse/quests/", "").split("-")[1]
    # Pull all quests and quest's sections
    allQuests = Quest.objects(source=questSource, questLine=questLine)
    allSections = [q.section for q in allQuests]
    data = {"source": questSource, "questLine": questLine, "sections": {},
            "progress": {"novice": None, "apprentice": None, "adept": None, 
                            "expert": None, "master": None, "legendary": None}}
    # Add each quest to the appropriate section
    for section in allSections:
        data["sections"][section] = {}
        for quest in allQuests:
            if(quest.section == section):
                data["sections"][section][quest.name] ={"id": quest.id, "radiant": quest.radiant,
                    "completion": {"novice": {"times": quest.completion.novice, "started": None}, 
                        "apprentice": {"times": quest.completion.apprentice, "started": None},
                        "adept": {"times": quest.completion.adept, "started": None}, 
                        "expert": {"times": quest.completion.expert, "started": None},
                        "master": {"times": quest.completion.master, "started": None}, 
                        "legendary": {"times": quest.completion.legendary, "started": None}}}
    for doc in Progress.objects.all():
        data["progress"][doc.difficulty] = doc
        for quest in allQuests:
            data["sections"][quest.section][quest.name]["completion"][doc.difficulty]["started"] = True
    return render(request, "skyrimseQuestLine.html", {'data': data})

def completeQuest(request):
    # Determine params from HTTP request
    params = request.path.split("/skyrimse/quests/")[1]
    questID = params.split("&")[0].split("=")[1]
    difficulty = params.split("&")[1].split("=")[1]
    questLine = params.split("&")[2].split("=")[1]
    # Pull the Quest and Progress objects
    quest = Quest.objects(id=questID).first()
    progress = Progress.objects(difficulty=difficulty).first()
    # Update the Quest Object
    if(quest["completion"][difficulty] == 0):
        if(quest.source in ("vanilla", "dawnguard", "dragonborn", "hearthfire")):
            progress["collected"]["quests"] += 1
            progress["collected"]["total"] += 1
            progress["completion"]["vanilla"] = progress.collected.total / progress.collectedTotal.total
        else:
            progress["collected"]["modQuests"] += 1
            progress["collected"]["modTotal"] += 1
            progress["completion"]["mod"] = progress.collected.modTotal / progress.collectedTotal.modTotal
        quest["completion"][difficulty] += 1
    quest.save()
    progress.save()
    return(redirect("/skyrimse/quests/{questLine}".format(questLine=questLine)))

########################
##### Perk Related #####
########################
def perks(request):
    # Pull all the questsallPerks, quest's cources, and quest's questlines
    allPerks = Perk.objects.all()   
    allSources = set([p.source for p in allPerks])
    allSkills = set([p.skill for p in allPerks])
    # Dynamically load quest sources
    perkFiles = list(filter(lambda x: "Perks" in x, [f for f in os.listdir('skyrimse/static/json/perks/')]))
    data = {"counts": {}, "skills": {}}
    for p in perkFiles:
        source = p.replace("Perks.json", "")
        data["counts"][source] = len(Perk.objects(source=source))
    # Sort skills into sources, and get counts per difficulty per questline
    for skill in allSkills:
        data["skills"][skill] = {}
        for source in allSources:
            total = len(Perk.objects(skill=skill, source=source))
            progData = {"novice": {"complete": len(Perk.objects(skill=skill, source=source, completion__novice__gt=0)), 
                        "total": total},
                        "apprentice": {"complete": len(Perk.objects(skill=skill, source=source, completion__apprentice__gt=0)), 
                        "total": total},
                        "adept": {"complete": len(Perk.objects(skill=skill, source=source, completion__adept__gt=0)), 
                        "total": total},
                        "expert": {"complete": len(Perk.objects(skill=skill, source=source, completion__expert__gt=0)), 
                        "total": total},
                        "master": {"complete": len(Perk.objects(skill=skill, source=source, completion__master__gt=0)), 
                        "total": total},
                        "legendary": {"complete": len(Perk.objects(skill=skill, source=source, completion__legendary__gt=0)), 
                        "total": total}}
            data["skills"][skill][source] = progData
    return render(request, "skyrimsePerks.html", {'data': data})

def perksLoad(request):
    # Pull data from JSON file
    toLoad = "skyrimse/static/json/perks/{source}Perks.json".format(source=request.path.split("=")[1])
    with open(file=toLoad, mode="r") as f:
        jsonData = load(f)
        f.close()
    # Create and save a Quest object
    for perkData in jsonData:
        perk = Perk(skill=perkData["skill"], source=perkData["source"], name=perkData["name"],
            description=perkData["description"], level=perkData["level"], 
            completion = Tracker(novice=0, apprentice=0, adept=0, expert=0, master=0, legendary=0))
        perk.save()
    return redirect("/skyrimse/perks")

def perkDetail(request):
    # Pull source and questline from HTTP request.path
    perkSource = request.path.replace("/skyrimse/perks/", "").split("-")[0]
    skill = request.path.replace("/skyrimse/perks/", "").split("-")[1]
    # Pull all perks
    allPerks = Perk.objects(source=perkSource, skill=skill)
    data = {"source": perkSource, "skill": skill, "perks": {}, 
            "skillLevels": {"novice": None, "apprentice": None, "adept": None, 
                            "expert": None, "master": None, "legendary": None}}
    # Add perk data
    for perk in allPerks:
        data["perks"][perk.name] = {"id": perk.id, "description": perk.description, "level": perk.level,
            "completion": {"novice": {"learned": perk.completion.novice, "skillLevel": None},
                        "apprentice": {"learned": perk.completion.apprentice, "skillLevel": None},
                        "adept": {"learned": perk.completion.adept, "skillLevel": None},
                        "expert": {"learned": perk.completion.expert, "skillLevel": None},
                        "master": {"learned": perk.completion.master, "skillLevel": None},
                        "legendary": {"learned": perk.completion.legendary, "skillLevel": None}}}
    # Find character skill levels
    for progress in Progress.objects.all():
        for perk in data["perks"]:
            data["perks"][perk]["completion"][progress.difficulty]["skillLevel"] = progress["skills"][skill]["level"]
    return render(request, 'skyrimsePerksDetail.html', {'data': data})

def learnPerk(request):
    # Determine params from HTTP request
    params = request.path.split("/skyrimse/perks/")[1]
    perkID = params.split("&")[0].split("=")[1]
    difficulty = params.split("&")[1].split("=")[1]
    sourceSkill = params.split("&")[2].split("=")[1]
    # Pull the Perk and Progress objects
    perk = Perk.objects(id=perkID).first()
    progress = Progress.objects(difficulty=difficulty).first()
    # Update the Quest Object
    if(perk["completion"][difficulty] == 0):
        if(perk.source in ("vanilla", "dawnguard", "dragonborn", "hearthfire")):
            progress["collected"]["perks"] += 1
            progress["collected"]["total"] += 1
            progress["completion"]["vanilla"] = progress.collected.total / progress.collectedTotal.total
        else:
            progress["collected"]["modPerks"] += 1
            progress["collected"]["modTotal"] += 1
            progress["completion"]["mod"] = progress.collected.modTotal / progress.collectedTotal.modTotal
        perk["completion"][difficulty] += 1
    perk.save()
    progress.save()
    return redirect("/skyrimse/perks/{sourceSkill}".format(sourceSkill=sourceSkill))

#########################
##### Shout Related #####
#########################
def shouts(request):
    # Pull all the quests, quest's cources, and quest's questlines
    allShouts = Shout.objects.all()
    allSources = set([s.source for s in allShouts])
    # Dynamically load quest sources
    shoutFiles = list(filter(lambda x: "Shouts" in x, [f for f in os.listdir('skyrimse/static/json/shouts')]))
    data = {"counts": {}, "sources": {}}
    for f in shoutFiles:
        source = f.replace("Shouts.json", "")
        data["counts"][source] = len(Shout.objects(source=source))
    # Start completion data
    for source in allSources:
        data["sources"][source] = {"novice": {"complete": 0, "total": 0}, 
            "apprentice": {"complete": 0, "total": 0}, "adept": {"complete": 0, "total": 0},
            "expert": {"complete": 0, "total": 0}, "master": {"complete": 0, "total": 0},
            "legendary": {"complete": 0, "total": 0}}
    # Count Completion data
    for shout in allShouts:
        for word in shout["words"]:
            for difficulty in word["completion"]:
                if(shout["words"][shout["words"].index(word)]["completion"][difficulty]):
                    data["sources"][shout.source][difficulty]["complete"] += 1
                data["sources"][shout.source][difficulty]["total"] += 1
    return render(request, "skyrimseShouts.html", {'data': data})

def shoutsLoad(request):
    # Pull data from JSON file
    toLoad = "skyrimse/static/json/shouts/{source}Shouts.json".format(source=request.path.split("=")[1])
    with open(file=toLoad, mode="r") as f:
        jsonData = load(f)
        f.close()
    # Create and save a Quest object
    for shoutData in jsonData:
        shout = Shout(name=shoutData["name"], source=shoutData["source"], 
            description=shoutData["description"], words=[])
        for wordData in shoutData["words"]:
            word = Word(original=wordData["original"], translation=wordData["translation"],
                cooldown=wordData["cooldown"], location=wordData["location"],
                completion=Tracker(novice=0, apprentice=0, adept=0, expert=0, master=0, legendary=0))
            shout["words"].append(word)
        shout.save()
    return redirect("/skyrimse/shouts")

def shoutsDetail(request):
    # Pull source from HTTP request.path
    source = request.path.split("/shouts/")[1]
    # Load all the shouts from Mongo
    allShouts = Shout.objects(source=source)
    data = {"source": source, "shouts": {}}
    # Pull Progress Data
    docs = {"novice": None, "apprentice": None, "adept": None,
        "expert": None, "master": None, "legendary": None}
    for progress in Progress.objects.all():
        docs[progress.difficulty] = True
    # Add the generic shout data
    for shout in allShouts:
        data["shouts"][shout.name] = {"id": shout.id, "description": shout.description, "words": []}
        for word in shout.words:
            data["shouts"][shout.name]["words"].append({"original": word.original,
                "translation": word.translation, "cooldown": word.cooldown,
                "completion": {"novice": {"learned": word.completion.novice, "started": docs["novice"]},
                    "apprentice": {"learned": word.completion.apprentice, "started": docs["apprentice"]},
                    "adept": {"learned": word.completion.adept, "started": docs["adept"]},
                    "expert": {"learned": word.completion.expert, "started": docs["expert"]},
                    "master": {"learned": word.completion.master, "started": docs["master"]},
                    "legendary": {"learned": word.completion.legendary, "started": docs["legendary"]}}})
    return render(request, 'skyrimseShoutsDetail.html', {'data': data})

def learnWord(request):
    # Pull shout.id, shout.word, and difficulty from HTTP request.path
    shoutID = request.path.split("/shouts/")[1].split("&")[0].split("=")[1]
    wordName = request.path.split("/shouts/")[1].split("&")[1].split("=")[1]
    difficulty = request.path.split("/shouts/")[1].split("&")[2].split("=")[1]
    # Pull the Shout and Progress object
    shout = Shout.objects(id=shoutID).first()
    progress = Progress.objects(difficulty=difficulty).first()
    # Update the Shout and Progress objects
    for word in shout.words:
        if(word.translation == wordName):
            word["completion"][difficulty] += 1
            if(shout.source in ("vanilla", "dawnguard", "dragonborn", "hearthfire")):
                progress["collected"]["words"] += 1
                progress["collected"]["total"] += 1
                progress["completion"]["vanilla"] = progress.collected.total / progress.collectedTotal.total
            else:
                progress["collected"]["modWords"] += 1
                progress["collected"]["modTotal"] += 1
                progress["completion"]["mod"] = progress.collected.modTotal / progress.collectedTotal.modTotal
            break
    shout.save()
    progress.save()
    return redirect("/skyrimse/shouts/{source}".format(source=shout.source))

############################
##### Location Related #####
############################
def locations(request):
    # Pull all the quests, quest's cources, and quest's questlines
    allLocations = Location.objects.all()
    allSources = set([s.source for s in allLocations])
    # Dynamically load quest sources
    locationFiles = list(filter(lambda x: "Locations" in x, [f for f in os.listdir('skyrimse/static/json/locations')]))
    data = {"counts": {}, "sources": {}}
    for f in locationFiles:
        source = f.replace("Locations.json", "")
        data["counts"][source] = len(Location.objects(source=source))
    # Start completion data
    for source in allSources:
        data["sources"][source] = {"novice": {"complete": 0, "total": 0}, 
            "apprentice": {"complete": 0, "total": 0}, "adept": {"complete": 0, "total": 0},
            "expert": {"complete": 0, "total": 0}, "master": {"complete": 0, "total": 0},
            "legendary": {"complete": 0, "total": 0}}
    # Count Completion data
    for location in allLocations:
        for difficulty in location["completion"]:
            if(location["completion"][difficulty]):
                data["sources"][location.source][difficulty]["complete"] += 1
            data["sources"][location.source][difficulty]["total"] += 1
    return render(request, 'skyrimseLocations.html', {'data': data})

def locationsLoad(request):
    # Pull data from JSON file
    toLoad = "skyrimse/static/json/locations/{source}Locations.json".format(source=request.path.split("=")[1])
    with open(file=toLoad, mode="r") as f:
        jsonData = load(f)
        f.close()
    # Create and save a Quest object
    for locationData in jsonData:
        location = Location(name=locationData["name"], source=locationData["source"], 
            locationType=locationData["type"], 
            completion=Tracker(novice=0, apprentice=0, adept=0, expert=0, master=0, legendary=0))
        location.save()
    return redirect("/skyrimse/locations")

def locationsDetail(request):
    # Pull source from HTTP request.path
    source = request.path.split("/locations/")[1]
    # Load all the shouts from Mongo
    allLocations = Location.objects(source=source)
    allTypes = set([l.locationType for l in allLocations])
    data = {"source": source, "types": {}}
    # Pull Progress Data
    docs = {"novice": None, "apprentice": None, "adept": None,
        "expert": None, "master": None, "legendary": None}
    for progress in Progress.objects.all():
        docs[progress.difficulty] = True
    # Load the location data
    for locationType in allTypes:
        data["types"][locationType] = {}
    for location in allLocations:
        data["types"][location.locationType][location.name] = {"id": location.id,
            "completion": {
            "novice": {"visited": location.completion.novice, "started": docs["novice"]},
            "apprentice": {"visited": location.completion.novice, "started": docs["apprentice"]},
            "adept": {"visited": location.completion.novice, "started": docs["adept"]},
            "expert": {"visited": location.completion.novice, "started": docs["expert"]},
            "master": {"visited": location.completion.novice, "started": docs["master"]},
            "legendary": {"visited": location.completion.novice, "started": docs["legendary"]}}
        }
    return render(request, 'skyrimseLocationsDetail.html', {'data': data})

def visitLocation(request):
    # Pull shout.id, shout.word, and difficulty from HTTP request.path
    locationID = request.path.split("/locations/")[1].split("&")[0].split("=")[1]
    difficulty = request.path.split("/locations/")[1].split("&")[1].split("=")[1]
    # Pull the Location and Progress objects
    location = Location.objects(id=locationID).first()
    progress = Progress.objects(difficulty=difficulty).first()
    # Update the Location and Progress objects
    location["completion"][difficulty] += 1
    if(location.source in ("vanilla", "dawnguard", "dragonborn", "hearthfire")):
        progress["collected"]["locations"] += 1
        progress["collected"]["total"] += 1
        progress["completion"]["vanilla"] = progress.collected.total / progress.collectedTotal.total
    else:
        progress["collected"]["modLocations"] += 1
        progress["collected"]["modTotal"] += 1
        progress["completion"]["mod"] = progress.collected.modTotal / progress.collectedTotal.modTotal
    location.save()
    progress.save()
    return redirect("/skyrimse/locations/{source}".format(source=location.source))

#########################
##### Spell Related #####
#########################
def spells(request):
    # Pull all the spells, spell's cources, and quest's questlines
    allSpells = Spell.objects.all()
    allSources = set([s.source for s in allSpells])
    allSchools = set([s.school for s in allSpells])
    # Dynamically load quest sources
    spellFiles = list(filter(lambda x: "Spells" in x, [f for f in os.listdir('skyrimse/static/json/spells')]))
    data = {"counts": {}, "schools": {}}
    for s in spellFiles:
        source = s.replace("Spells.json", "")
        data["counts"][source] = len(Spell.objects(source=source))
    # Start Spell Completion Data
    for school in allSchools:
        data["schools"][school] = {}
        for spell in allSpells:
            if(spell.school not in data["schools"][school] and spell.school == school):
                data["schools"][school][spell.source] = {"novice": {"learned": 0, "total": 0}, 
                    "apprentice": {"learned": 0, "total": 0}, "adept": {"learned": 0, "total": 0}, 
                    "expert": {"learned": 0, "total": 0}, "master": {"learned": 0, "total": 0}, 
                    "legendary": {"learned": 0, "total": 0}}
    # Finish Spell Data
    for spell in allSpells:
        for difficulty in spell.completion:
            if(spell["completion"][difficulty]):
                data["schools"][spell.school][spell.source][difficulty]["learned"] += 1
            data["schools"][spell.school][spell.source][difficulty]["total"] += 1

    return render(request, 'skyrimseSpells.html', {'data': data})

def spellsLoad(request):
    # Pull data from JSON file
    toLoad = "skyrimse/static/json/spells/{source}Spells.json".format(source=request.path.split("=")[1])
    with open(file=toLoad, mode="r") as f:
        jsonData = load(f)
        f.close()
    # Create and save a Quest object
    for spellsData in jsonData:
        spell = Spell(name=spellsData["name"], source=spellsData["source"], 
            school=spellsData["school"], level=spellsData["level"], description=spellsData["description"], 
            completion=Tracker(novice=0, apprentice=0, adept=0, expert=0, master=0, legendary=0))
        spell.save()
    return redirect("/skyrimse/spells")

def spellSchool(request):
    # Pull the school and source from HTTP request.path
    source = request.path.split("/spells/")[1].split("-")[0]
    school = request.path.split("/spells/")[1].split("-")[1]
    # Pull all the spells
    allSpells = Spell.objects(school=school, source=source)
    docs = {"novice": None, "apprentice": None, "adept": None,
        "expert": None, "master": None, "legendary": None}
    for doc in Progress.objects.all():
        docs[doc.difficulty] = doc["skills"][school]["level"]
    # Start the data object
    data = {"source": source, "school": school, "spells": {}}
    # Load Spells into Data object
    spellLevels = {"novice": 0, "apprentice": 25, "adept": 50, "expert": 75, "master": 100}
    for spell in allSpells:
        data["spells"][spell.name] = {"id": spell.id, "description": spell.description, "level": spellLevels[spell.level], 
            "completion": {"novice": {"skillLevel": docs["novice"], "learned": spell.completion.novice},
                "apprentice": {"skillLevel": docs["apprentice"], "learned": spell.completion.apprentice},
                "adept": {"skillLevel": docs["adept"], "learned": spell.completion.adept},
                "expert": {"skillLevel": docs["expert"], "learned": spell.completion.expert},
                "master": {"skillLevel": docs["master"], "learned": spell.completion.master},
                "legendary": {"skillLevel": docs["legendary"], "learned": spell.completion.legendary}}}
    return render(request, 'skyrimseSpellSchool.html', {'data': data})

def learnSpell(request):
    # Pull shout.id, shout.word, and difficulty from HTTP request.path
    spellID = request.path.split("/spells/")[1].split("&")[0].split("=")[1]
    difficulty = request.path.split("/spells/")[1].split("&")[1].split("=")[1]
    # Pull the Location and Progress objects
    spell = Spell.objects(id=spellID).first()
    progress = Progress.objects(difficulty=difficulty).first()
    # Update the Location and Progress objects
    spell["completion"][difficulty] += 1
    if(spell.source in ("vanilla", "dawnguard", "dragonborn", "hearthfire")):
        progress["collected"]["spells"] += 1
        progress["collected"]["total"] += 1
        progress["completion"]["vanilla"] = progress.collected.total / progress.collectedTotal.total
    else:
        progress["collected"]["modSpells"] += 1
        progress["collected"]["modTotal"] += 1
        progress["completion"]["mod"] = progress.collected.modTotal / progress.collectedTotal.modTotal
    spell.save()
    progress.save()
    return redirect("/skyrimse/spells/{source}-{school}".format(source=spell.source, school=spell.school))

###############################
##### Enchantment Related #####
###############################
def enchantments(request):
    # Pull all the enchantments, enchantment's sources, and enchantment's types
    allEnchantments = Enchantment.objects.all()
    allSources = set([e.source for e in allEnchantments])
    allTypes = set([e.enchantmentType for e in allEnchantments])
    # Dynamically load quest sources
    enchantmentFiles = [f for f in os.listdir('skyrimse/static/json/enchantments')]
    data = {"counts": {}, "types": {}}
    for e in enchantmentFiles:
        source = e.replace("Enchantments.json", "")
        data["counts"][source] = len(Enchantment.objects(source=source))
    # Start the data
    for enchantment in allEnchantments:
        # Check if type exists
        if(not data["types"].get(enchantment.enchantmentType)):
            data["types"][enchantment.enchantmentType] = {}
        # Check if source in type exists
        if(not data["types"][enchantment.enchantmentType].get(enchantment.source)):
            data["types"][enchantment.enchantmentType][enchantment.source] = {
                "novice": {"learned": 0, "total": 0}, "apprentice": {"learned": 0, "total": 0}, 
                "adept": {"learned": 0, "total": 0}, "expert": {"learned": 0, "total": 0}, 
                "master": {"learned": 0, "total": 0}, "legendary": {"learned": 0, "total": 0}}
        # Check if complete per difficulty
        for difficulty in enchantment.completion:
            if(enchantment["completion"][difficulty] > 0):
                data["types"][enchantment.enchantmentType][enchantment.source][difficulty]["learned"] += 1
            data["types"][enchantment.enchantmentType][enchantment.source][difficulty]["total"] += 1
    return render(request, 'skyrimseEnchantments.html', {'data': data})

def enchantmentsLoad(request):
    # Pull data from JSON file
    toLoad = "skyrimse/static/json/enchantments/{source}Enchantments.json".format(source=request.path.split("=")[1])
    with open(file=toLoad, mode="r") as f:
        jsonData = load(f)
        f.close()
    # Create and save a Quest object
    for enchantmentData in jsonData:
        enchantment = Enchantment(name=enchantmentData["name"], source=enchantmentData["source"], 
            enchantmentType=enchantmentData["type"], description=enchantmentData["description"], 
            completion=Tracker(novice=0, apprentice=0, adept=0, expert=0, master=0, legendary=0))
        enchantment.save()
    return redirect("/skyrimse/enchantments")

def enchantmentType(request):
    # Pull the school and source from HTTP request.path
    source = request.path.split("/enchantments/")[1].split("-")[0]
    enchantmentType = request.path.split("/enchantments/")[1].split("-")[1]
    # Pull all the spells
    allEnchantments = Enchantment.objects(enchantmentType=enchantmentType, source=source)
    docs = {"novice": None, "apprentice": None, "adept": None,
        "expert": None, "master": None, "legendary": None}
    for doc in Progress.objects.all():
        docs[doc.difficulty] = True
    # Start the data object
    data = {"source": source, "type": enchantmentType, "enchantments": {}}
    # Load Spells into Data object
    for enchantment in allEnchantments:
        data["enchantments"][enchantment.name] = {"id": enchantment.id, "description": enchantment.description, 
            "completion": {"novice": {"started": docs["novice"], "learned": enchantment.completion.novice},
                "apprentice": {"started": docs["apprentice"], "learned": enchantment.completion.apprentice},
                "adept": {"started": docs["adept"], "learned": enchantment.completion.adept},
                "expert": {"started": docs["expert"], "learned": enchantment.completion.expert},
                "master": {"started": docs["master"], "learned": enchantment.completion.master},
                "legendary": {"started": docs["legendary"], "learned": enchantment.completion.legendary}}}
    return render(request, 'skyrimseEnchantmentType.html', {'data': data})

def learnEnchantment(request):
    # Pull shout.id, shout.word, and difficulty from HTTP request.path
    enchantmentID = request.path.split("/enchantments/")[1].split("&")[0].split("=")[1]
    difficulty = request.path.split("/enchantments/")[1].split("&")[1].split("=")[1]
    # Pull the Location and Progress objects
    enchantment = Enchantment.objects(id=enchantmentID).first()
    progress = Progress.objects(difficulty=difficulty).first()
    # Update the Location and Progress objects
    enchantment["completion"][difficulty] += 1
    if(enchantment.source in ("vanilla", "dawnguard", "dragonborn", "hearthfire")):
        progress["collected"]["enchantments"] += 1
        progress["collected"]["total"] += 1
        progress["completion"]["vanilla"] = progress.collected.total / progress.collectedTotal.total
    else:
        progress["collected"]["modEnchantments"] += 1
        progress["collected"]["modTotal"] += 1
        progress["completion"]["mod"] = progress.collected.modTotal / progress.collectedTotal.modTotal
    enchantment.save()
    progress.save()
    return redirect("/skyrimse/enchantments/{source}-{type}".format(source=enchantment.source, type=enchantment.enchantmentType))

###############################
##### Ingredients Related #####
###############################
def ingredients(request):
    # Pull all the ingredients, ingredient's sources, and ingredients's effects
    allIngredients = Ingredient.objects.all()
    allSources = set([i.source for i in allIngredients])
    # Dynamically load quest sources
    ingredientFiles = [f for f in os.listdir('skyrimse/static/json/ingredients')]
    data = {"counts": {}, "sources": {}, "effects": {}}
    for i in ingredientFiles:
        source = i.replace("Ingredients.json", "")
        data["counts"][source] = len(Ingredient.objects(source=source))
    for ingredient in allIngredients:
        if(not data["sources"].get(ingredient.source)):
            data["sources"][ingredient.source] = {
                "novice": {"learned": 0, "total": 0}, "apprentice": {"learned": 0, "total": 0}, 
                "adept": {"learned": 0, "total": 0}, "expert": {"learned": 0, "total": 0}, 
                "master": {"learned": 0, "total": 0}, "legendary": {"learned": 0, "total": 0}}
        for effect in ingredient.effects:
            effectIndex = ingredient["effects"].index(effect)
            effectKnown = False
            for difficulty in effect.completion:
                if(ingredient["effects"][effectIndex]["completion"][difficulty] > 0):
                    data["sources"][ingredient.source][difficulty]["learned"] += 1
                    effectKnown = True
                data["sources"][ingredient.source][difficulty]["total"] += 1
            if(effectKnown):
                if(not data["effects"].get(effect.name)):
                    data["effects"][effect.name] = ""
                data["effects"][effect.name] += ", {}".format(ingredient.name)
    return render(request, 'skyrimseIngredients.html', {'data': data})

def ingredientsLoad(request):
    # Pull data from JSON file
    toLoad = "skyrimse/static/json/ingredients/{source}Ingredients.json".format(source=request.path.split("=")[1])
    with open(file=toLoad, mode="r") as f:
        jsonData = load(f)
        f.close()
    # Create and save a Quest object
    for ingredientData in jsonData:
        ingredient = Ingredient(name=ingredientData["name"], source=ingredientData["source"],
            locations=ingredientData["location"], effects=[])
        for effect in ["primary", "secondary", "tertiary", "quatrary"]:
            effect = Effect(name=ingredientData[effect], order=effect,
                completion=Tracker(novice=0, apprentice=0, adept=0, expert=0, master=0, legendary=0))
            ingredient["effects"].append(effect)
        ingredient.save()
    return redirect("/skyrimse/ingredients")

def ingredientsDetail(request):
    # Pull the school and source from HTTP request.path
    source = request.path.split("/ingredients/")[1]
    # Pull all the ingredients
    allIngredients = Ingredient.objects(source=source)
    docs = {"novice": None, "apprentice": None, "adept": None,
        "expert": None, "master": None, "legendary": None}
    for doc in Progress.objects.all():
        docs[doc.difficulty] = True
    # Create the Data
    data = {"source": source, "ingredients": []}
    for ingredient in allIngredients:
        tempIngredient = {"id": ingredient.id, "name": ingredient.name,
            "location": ingredient.locations, "effects": []}
        for effect in ingredient["effects"]:
            effectIndex = ingredient["effects"].index(effect)
            tempEffect = {"name": effect.name, "order": effect.order, "known": False,
                "completion": {
                    "novice": {"started": docs["novice"], "learned": ingredient["effects"][effectIndex]["completion"]["novice"]},
                    "apprentice": {"started": docs["apprentice"], "learned": ingredient["effects"][effectIndex]["completion"]["apprentice"]},
                    "adept": {"started": docs["adept"], "learned": ingredient["effects"][effectIndex]["completion"]["adept"]},
                    "expert": {"started": docs["expert"], "learned": ingredient["effects"][effectIndex]["completion"]["expert"]},
                    "master": {"started": docs["master"], "learned": ingredient["effects"][effectIndex]["completion"]["master"]},
                    "legendary": {"started": docs["legendary"], "learned": ingredient["effects"][effectIndex]["completion"]["legendary"]}}}
            for difficulty in ["novice", "apprentice", "adept", "expert", "master", "legendary"]:
                if(tempEffect["completion"][difficulty]["learned"] > 0):
                    tempEffect["known"] = True
                    break
            tempIngredient["effects"].append(tempEffect)
        data["ingredients"].append(tempIngredient)
    return render(request, 'skyrimseIngredientsDetail.html', {'data': data})

def learnEffect(request):
    # Pull shout.id, shout.word, and difficulty from HTTP request.path
    ingredientID = request.path.split("/ingredients/")[1].split("&")[0].split("=")[1]
    effectName = request.path.split("/ingredients/")[1].split("&")[1].split("=")[1]
    difficulty = request.path.split("/ingredients/")[1].split("&")[2].split("=")[1]
    # Pull the Ingredient and Progress objects
    ingredient = Ingredient.objects(id=ingredientID).first()
    progress = Progress.objects(difficulty=difficulty).first()
    # Update the Location and Progress objects
    for effect in ingredient.effects:
        if(effect.name == effectName):
            effectIndex = ingredient["effects"].index(effect)
            ingredient["effects"][effectIndex]["completion"][difficulty] += 1
            break
    if(ingredient.source in ("vanilla", "dawnguard", "dragonborn", "hearthfire")):
        progress["collected"]["ingredients"] += 1
        progress["collected"]["total"] += 1
        progress["completion"]["vanilla"] = progress.collected.total / progress.collectedTotal.total
    else:
        progress["collected"]["modIngredients"] += 1
        progress["collected"]["modTotal"] += 1
        progress["completion"]["mod"] = progress.collected.modTotal / progress.collectedTotal.modTotal
    ingredient.save()
    progress.save()
    return redirect("/skyrimse/ingredients/{source}".format(source=ingredient.source))