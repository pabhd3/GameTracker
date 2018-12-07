from django.http import HttpResponse
from django.shortcuts import render, redirect
from skyrimse.models import *
from mongoengine.context_managers import switch_db
from datetime import datetime
from .customScripts import plotRader
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
    questCount = sum([len(Quest.objects(source=source)) for source in ["vanilla", "dawnguard", "dragonborn"]])
    modQuestCount = len(Quest.objects.all()) - questCount
    perkCount = len(Perk.objects(source="vanilla"))
    modPerkCount = len(Perk.objects.all()) - perkCount
    wordCount = sum([len(Shout.objects(source=source)) for source in ["vanilla", "dawnguard", "dragonborn"]]) * 3
    modWordCount = (len(Shout.objects.all()) * 3) - wordCount
    locationCount = sum([len(Location.objects(source=source)) for source in ["vanilla", "dawnguard", "dragonborn"]])
    modLocationCount = (len(Location.objects.all())) - locationCount
    totalCount = sum([questCount, perkCount, wordCount, locationCount])
    modTotalCount = sum([modQuestCount, modPerkCount, modWordCount, modLocationCount])
    progress.collected = Collected(quests=0, modQuests=0, perks=0, modPerks=0, 
        words=0, modWords=0, locations=0, modLocations=0, total=0, modTotal=0)
    progress.collectedTotal = Collected(quests=questCount, modQuests=modQuestCount, perks=perkCount, 
        words=wordCount, modWords=modWordCount, modPerks=modPerkCount, locations=locationCount, 
        modLocations=modLocationCount, total=totalCount, modTotal=modTotalCount)
    progress.save()
    # Generate a Radar Graph for the progress
    plotRader(values=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], difficulty=progress.difficulty)
    return redirect("/skyrimse/progress")

def deleteDifficulty(request):
    # Pull progress.id from HTTP request.path
    deleteID = request.path.split("=")[1]
    progress = Progress.objects(id=deleteID).first()
    # Delete the Radar Graph graph
    strFile = "skyrimse/static/images/progress/skills-{difficulty}.png".format(difficulty=progress.difficulty)
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
    newLevels = [progress.skills.alchemy.level, progress.skills.alteration.level, 
        progress.skills.archery.level, progress.skills.block.level, progress.skills.conjuration.level, 
        progress.skills.destruction.level, progress.skills.enchanting.level, progress.skills.heavyArmor.level, 
        progress.skills.illusion.level, progress.skills.lightArmor.level, progress.skills.lockpicking.level, 
        progress.skills.oneHanded.level, progress.skills.pickPocket.level, progress.skills.restoration.level, 
        progress.skills.smithing.level, progress.skills.sneak.level, progress.skills.speech.level, 
        progress.skills.twoHanded.level]
    plotRader(values=newLevels, difficulty=progress.difficulty)
    return redirect("/skyrimse/progress/{difficulty}".format(difficulty=progress.difficulty))

def progressDetail(request):
    # Pull id from HTTP request.path
    progressID = request.path.split("/skyrimse/progress/")[1]
    progress = Progress.objects(difficulty=progressID).first()
    data = {"id": progress.id, "difficulty": progress.difficulty, "created": progress.created, 
        "skills": {}, "stats": {}}
    for skill in progress.skills:
        data["skills"][skill] = {"level": progress["skills"][skill]["level"],
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
        if(quest.source in ("vanilla", "dawnguard", "dragonborn")):
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
        if(perk.source in ("vanilla", "dawnguard", "dragonborn")):
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
            if(shout.source in ("vanilla", "dawnguard", "dragonborn")):
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
    if(location.source in ("vanilla", "dawnguard", "dragonborn")):
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