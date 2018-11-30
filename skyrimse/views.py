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
    docs = Progress.objects.all()
    data = {"Novice": None, "Apprentice": None, "Adept": None,
            "Expert": None, "Master": None, "Legendary": None}
    for doc in docs:
        data[doc.difficulty] = doc
    return render(request, 'skyrimseProgress.html', {'data': data})

def addDifficulty(request):
    progress = Progress()
    difficulty = request.path.split("=")[1]
    progress.created = datetime.strftime(datetime.now(), "%A %B %d, %Y %H:%M:%S:%f %Z")
    progress.difficulty = difficulty
    progress.completion = Completion(vanilla=0, mod=0)
    progress.skills = Skills(alchemy=0, alteration=0, archery=0, block=0, conjuration=0, 
            destruction=0, enchanting=0, heavyArmor=0, illusion=0, lightArmor=0, 
            lockpicking=0, oneHanded=0, pickPocket=0, restoration=0, smithing=0, 
            sneak=0, speech=0, twoHanded=0)
    progress.save()
    newLevels = [progress.skills.alchemy, progress.skills.alteration, progress.skills.archery, progress.skills.block,
        progress.skills.conjuration, progress.skills.destruction, progress.skills.enchanting, progress.skills.heavyArmor,
        progress.skills.illusion, progress.skills.lightArmor, progress.skills.lockpicking, progress.skills.oneHanded,
        progress.skills.pickPocket, progress.skills.restoration, progress.skills.smithing, progress.skills.sneak,
        progress.skills.speech, progress.skills.twoHanded]
    plotRader(values=newLevels, difficulty=progress.difficulty)
    return redirect("/skyrimse/progress")

def deleteDifficulty(request):
    deleteID = request.path.split("=")[1]
    progress = Progress.objects(id=deleteID).first()
    strFile = "skyrimse/static/images/progress/skills-{difficulty}.png".format(difficulty=progress.difficulty)
    if(os.path.isfile(strFile)):
        os.remove(strFile)
    progress.delete()
    return redirect("/skyrimse/progress")

def levelSkill(request):
    paramsStr = request.path.split("/skyrimse/progress/")[1]
    skill = paramsStr.split("&")[0].split("=")[1]
    difficulty = paramsStr.split("&")[1].split("=")[1]
    progress = Progress.objects(id=difficulty).first()
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
    newLevels = [progress.skills.alchemy, progress.skills.alteration, progress.skills.archery, progress.skills.block,
        progress.skills.conjuration, progress.skills.destruction, progress.skills.enchanting, progress.skills.heavyArmor,
        progress.skills.illusion, progress.skills.lightArmor, progress.skills.lockpicking, progress.skills.oneHanded,
        progress.skills.pickPocket, progress.skills.restoration, progress.skills.smithing, progress.skills.sneak,
        progress.skills.speech, progress.skills.twoHanded]
    plotRader(values=newLevels, difficulty=progress.difficulty)
    return redirect("/skyrimse/progress/{difficulty}".format(difficulty=progress.difficulty))

def progressDetail(request):
    progressID = request.path.split("/skyrimse/progress/")[1]
    data = Progress.objects(difficulty=progressID).first()
    return render(request, "skyrimseProgressDetail.html", {'data': data})

##########################
##### Quests Related #####
##########################
def quests(request):
    allQuests = Quest.objects.all()
    allSources = set([q.source for q in allQuests])
    allQuestLines = set([q.questLine for q in allQuests])
    data = {"counts": {
                "vanilla": len(Quest.objects(source="vanilla")),
                "dawnguard": len(Quest.objects(source="dawnguard")),
                "dragonborn": len(Quest.objects(source="dragonborn"))},
            "sources": {}}
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
    toLoad = "skyrimse/static/json/{source}Quests.json".format(source=request.path.split("=")[1])
    with open(file=toLoad, mode="r") as f:
        jsonData = load(f)
        f.close()
    for questData in jsonData:
        quest = Quest(name=questData["name"], questLine=questData["questLine"], source=questData["source"],
                      section=questData["section"], radiant=questData["radiant"],
                      completion = Tracker(novice=0, apprentice=0, adept=0, expert=0, master=0, legendary=0))
        quest.save()
    return redirect("/skyrimse/quests")

def questLine(request):
    questSource = request.path.replace("/skyrimse/quests/", "").split("-")[0]
    questLine = request.path.replace("/skyrimse/quests/", "").split("-")[1]
    allQuests = Quest.objects(source=questSource, questLine=questLine)
    allSections = [q.section for q in allQuests]
    data = {"source": questSource, "questLine": questLine, "test": allQuests[0], "sections": {}}
    for section in allSections:
        data["sections"][section] = []
        for quest in allQuests:
            if(quest.section == section):
                data["sections"][section].append(quest)
    return render(request, "skyrimseQuestLine.html", {'data': data})

def completeQuest(request):
    params = request.path.split("/skyrimse/quests/")[1]
    questID = params.split("&")[0].split("=")[1]
    difficulty = params.split("&")[1].split("=")[1]
    questLine = params.split("&")[2].split("=")[1]
    quest = Quest.objects(id=questID).first()
    if(difficulty == "novice"):
        quest.update(inc__completion__novice=1)
    elif(difficulty == "apprentice"):
        quest.update(inc__completion__apprentice=1)
    elif(difficulty == "adept"):
        quest.update(inc__completion__adept=1)
    elif(difficulty == "expert"):
        quest.update(inc__completion__expert=1)
    elif(difficulty == "master"):
        quest.update(inc__completion__master=1)
    elif(difficulty == "legendary"):
        quest.update(inc__completion__legendary=1)
    quest.save()
    return(redirect("/skyrimse/quests/{questLine}".format(questLine=questLine)))