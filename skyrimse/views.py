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
        data[doc.difficulty] = doc
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
    progress.skills = Skills(alchemy=0, alteration=0, archery=0, block=0, conjuration=0, 
            destruction=0, enchanting=0, heavyArmor=0, illusion=0, lightArmor=0, 
            lockpicking=0, oneHanded=0, pickPocket=0, restoration=0, smithing=0, 
            sneak=0, speech=0, twoHanded=0)
    questCount = sum([len(Quest.objects(source=source)) for source in ["vanilla", "dawnguard", "dragonborn"]])
    modQuestCount = len(Quest.objects.all()) - questCount
    totalCount = sum([questCount])
    modTotalCount = sum([modQuestCount])
    progress.collected = Collected(quests=0, modQuests=0, total=0, modTotal=0)
    progress.collectedTotal = Collected(quests=questCount, modQuests=modQuestCount, total=totalCount, modTotal=modTotalCount)
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
        if(progress.difficulty == "Novice"):
            quest.update(set__completion__novice=0)
        elif(progress.difficulty == "Apprentice"):
            quest.update(set__completion__apprentice=0)
        elif(progress.difficulty == "Adept"):
            quest.update(set__completion__adept=0)
        elif(progress.difficulty == "Expert"):
            quest.update(set__completion__expert=0)
        elif(progress.difficulty == "Master"):
            quest.update(set__completion__master=0)
        elif(progress.difficulty == "Legendary"):
            quest.update(set__completion__legendary=0)
        quest.save()
    return redirect("/skyrimse/progress")

def levelSkill(request):
    # Pull skill and difficulty from HTTP request.path
    paramsStr = request.path.split("/skyrimse/progress/")[1]
    skill = paramsStr.split("&")[0].split("=")[1]
    difficulty = paramsStr.split("&")[1].split("=")[1]
    progress = Progress.objects(id=difficulty).first()
    # Update skill level
    if(skill == "alchemy"):
        progress.update(inc__skills__alchemy=1)
    elif(skill == "alteration"):
        progress.update(inc__skills__alteration=1)
    elif(skill == "archery"):
        progress.update(inc__skills__archery=1)
    elif(skill == "block"):
        progress.update(inc__skills__block=1)
    elif(skill == "conjuration"):
        progress.update(inc__skills__conjuration=1)
    elif(skill == "destruction"):
        progress.update(inc__skills__destruction=1)
    elif(skill == "enchanting"):
        progress.update(inc__skills__enchanting=1)
    elif(skill == "heavyArmor"):
        progress.update(inc__skills__heavyArmor=1)
    elif(skill == "illusion"):
        progress.update(inc__skills__illusion=1)
    elif(skill == "lightArmor"):
        progress.update(inc__skills__lightArmor=1)
    elif(skill == "lockpicking"):
        progress.update(inc__skills__lockpicking=1)
    elif(skill == "oneHanded"):
        progress.update(inc__skills__oneHanded=1)
    elif(skill == "pickPocket"):
        progress.update(inc__skills__pickPocket=1)
    elif(skill == "restoration"):
        progress.update(inc__skills__restoration=1)
    elif(skill == "smithing"):
        progress.update(inc__skills__smithing=1)
    elif(skill == "sneak"):
        progress.update(inc__skills__sneak=1)
    elif(skill == "speech"):
        progress.update(inc__skills__speech=1)
    elif(skill == "twoHanded"):
        progress.update(inc__skills__twoHanded=1)
    progress.save()
    # Pull levels for new Radar Graph
    newLevels = [progress.skills.alchemy, progress.skills.alteration, progress.skills.archery, progress.skills.block,
        progress.skills.conjuration, progress.skills.destruction, progress.skills.enchanting, progress.skills.heavyArmor,
        progress.skills.illusion, progress.skills.lightArmor, progress.skills.lockpicking, progress.skills.oneHanded,
        progress.skills.pickPocket, progress.skills.restoration, progress.skills.smithing, progress.skills.sneak,
        progress.skills.speech, progress.skills.twoHanded]
    plotRader(values=newLevels, difficulty=progress.difficulty)
    return redirect("/skyrimse/progress/{difficulty}".format(difficulty=progress.difficulty))

def progressDetail(request):
    # Pull id from HTTP request.path
    progressID = request.path.split("/skyrimse/progress/")[1]
    data = Progress.objects(difficulty=progressID).first()
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
    data = {"counts": {
                "vanilla": len(Quest.objects(source="vanilla")),
                "dawnguard": len(Quest.objects(source="dawnguard")),
                "dragonborn": len(Quest.objects(source="dragonborn"))},
            "sources": {}}
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
    toLoad = "skyrimse/static/json/{source}Quests.json".format(source=request.path.split("=")[1])
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
    data = {"source": questSource, "questLine": questLine, "test": allQuests[0], "sections": {},
            "progress": {"novice": None, "apprentice": None, "adept": None, 
                            "expert": None, "master": None, "legendary": None}}
    # Add each quest to the appropriate section
    for section in allSections:
        data["sections"][section] = []
        for quest in allQuests:
            if(quest.section == section):
                data["sections"][section].append(quest)
    for doc in Progress.objects.all():
        data["progress"][doc.difficulty] = doc
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
    if(difficulty == "novice"):
        if(quest.completion.novice == 0):
            if(quest.source in ("vanilla", "dawnguard", "dragonborn")):
                progress.update(inc__collected__quests=1)
                progress.update(inc__collected__total=1)
                progress.update(set__completion__vanilla=progress.collected.total/progress.collectedTotal.total)
            else:
                progress.update(inc__collected__modQuests=1)
                progress.update(inc__collected__modTotal=1)
                progress.update(set__completion__vanilla=progress.collected.modTotal/progress.collectedTotal.modTotal)
        quest.update(inc__completion__novice=1)
    elif(difficulty == "apprentice"):
        if(quest.completion.apprentice == 0):
            if(quest.source in ("vanilla", "dawnguard", "dragonborn")):
                progress.update(inc__collected__quests=1)
                progress.update(inc__collected__total=1)
                progress.update(set__completion__vanilla=progress.collected.total/progress.collectedTotal.total)
            else:
                progress.update(inc__collected__modQuests=1)
                progress.update(inc__collected__modTotal=1)
                progress.update(set__completion__vanilla=progress.collected.modTotal/progress.collectedTotal.modTotal)
        quest.update(inc__completion__apprentice=1)
    elif(difficulty == "adept"):
        if(quest.completion.adept == 0):
            if(quest.source in ("vanilla", "dawnguard", "dragonborn")):
                progress.update(inc__collected__quests=1)
                progress.update(inc__collected__total=1)
                progress.update(set__completion__vanilla=progress.collected.total/progress.collectedTotal.total)
            else:
                progress.update(inc__collected__modQuests=1)
                progress.update(inc__collected__modTotal=1)
                progress.update(set__completion__vanilla=progress.collected.modTotal/progress.collectedTotal.modTotal)
        quest.update(inc__completion__adept=1)
    elif(difficulty == "expert"):
        if(quest.completion.expert == 0):
            if(quest.source in ("vanilla", "dawnguard", "dragonborn")):
                progress.update(inc__collected__quests=1)
                progress.update(inc__collected__total=1)
                progress.update(set__completion__vanilla=progress.collected.total/progress.collectedTotal.total)
            else:
                progress.update(inc__collected__modQuests=1)
                progress.update(inc__collected__modTotal=1)
                progress.update(set__completion__vanilla=progress.collected.modTotal/progress.collectedTotal.modTotal)
        quest.update(inc__completion__expert=1)
    elif(difficulty == "master"):
        if(quest.completion.master == 0):
            if(quest.source in ("vanilla", "dawnguard", "dragonborn")):
                progress.update(inc__collected__quests=1)
                progress.update(inc__collected__total=1)
                progress.update(set__completion__vanilla=progress.collected.total/progress.collectedTotal.total)
            else:
                progress.update(inc__collected__modQuests=1)
                progress.update(inc__collected__modTotal=1)
                progress.update(set__completion__vanilla=progress.collected.modTotal/progress.collectedTotal.modTotal)
        quest.update(inc__completion__master=1)
    elif(difficulty == "legendary"):
        if(quest.completion.legendary == 0):
            if(quest.source in ("vanilla", "dawnguard", "dragonborn")):
                progress.update(inc__collected__quests=1)
                progress.update(inc__collected__total=1)
                progress.update(set__completion__vanilla=progress.collected.total/progress.collectedTotal.total)
            else:
                progress.update(inc__collected__modQuests=1)
                progress.update(inc__collected__modTotal=1)
                progress.update(set__completion__vanilla=progress.collected.modTotal/progress.collectedTotal.modTotal)
        quest.update(inc__completion__legendary=1)
    quest.save()
    progress.save()
    return(redirect("/skyrimse/quests/{questLine}".format(questLine=questLine)))