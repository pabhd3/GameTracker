from django.http import HttpResponse
from django.shortcuts import render, redirect
from skyrimse.models import *
from mongoengine.context_managers import switch_db
from datetime import datetime
from .customScripts import plotRader
from json import load, loads, dumps

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
    plotRader(values=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], difficulty=difficulty)
    return redirect("/skyrimse/progress")

def deleteDifficulty(request):
    deleteID = request.path.split("=")[1]
    Progress.objects(id=deleteID).delete()
    return redirect("/skyrimse/progress")

def levelSkill(request):
    paramsStr = request.path.split("/skyrimse/progress/")[1]
    params = {param.split("=")[0]: param.split("=")[1] for param in paramsStr.split("&")}
    progress = Progress.objects(id=params["difficulty"]).first()
    if(params["levelSkill"] == "alchemy"):
        progress.update(inc__skills__alchemy=1)
    elif(params["levelSkill"] == "alteration"):
        progress.update(inc__skills__alteration=1)
    elif(params["levelSkill"] == "archery"):
        progress.update(inc__skills__archery=1)
    elif(params["levelSkill"] == "block"):
        progress.update(inc__skills__block=1)
    elif(params["levelSkill"] == "conjuration"):
        progress.update(inc__skills__conjuration=1)
    elif(params["levelSkill"] == "destruction"):
        progress.update(inc__skills__destruction=1)
    elif(params["levelSkill"] == "enchanting"):
        progress.update(inc__skills__enchanting=1)
    elif(params["levelSkill"] == "heavyArmor"):
        progress.update(inc__skills__heavyArmor=1)
    elif(params["levelSkill"] == "illusion"):
        progress.update(inc__skills__illusion=1)
    elif(params["levelSkill"] == "lightArmor"):
        progress.update(inc__skills__lightArmor=1)
    elif(params["levelSkill"] == "lockpicking"):
        progress.update(inc__skills__lockpicking=1)
    elif(params["levelSkill"] == "oneHanded"):
        progress.update(inc__skills__oneHanded=1)
    elif(params["levelSkill"] == "pickPocket"):
        progress.update(inc__skills__pickPocket=1)
    elif(params["levelSkill"] == "restoration"):
        progress.update(inc__skills__restoration=1)
    elif(params["levelSkill"] == "smithing"):
        progress.update(inc__skills__smithing=1)
    elif(params["levelSkill"] == "sneak"):
        progress.update(inc__skills__sneak=1)
    elif(params["levelSkill"] == "speech"):
        progress.update(inc__skills__speech=1)
    elif(params["levelSkill"] == "twoHanded"):
        progress.update(inc__skills__twoHanded=1)
    progress.save()
    newLevels = [progress.skills.alchemy, progress.skills.alteration, progress.skills.archery, progress.skills.block,
        progress.skills.conjuration, progress.skills.destruction, progress.skills.enchanting, progress.skills.heavyArmor,
        progress.skills.illusion, progress.skills.lightArmor, progress.skills.lockpicking, progress.skills.oneHanded,
        progress.skills.pickPocket, progress.skills.restoration, progress.skills.smithing, progress.skills.sneak,
        progress.skills.speech, progress.skills.twoHanded]
    plotRader(values=newLevels, difficulty=progress.difficulty)
    return redirect("/skyrimse/progress/{id}".format(id=progress.id))

def progressDetail(request):
    progressID = request.path.split("/skyrimse/progress/")[1]
    data = Progress.objects(id=progressID).first()
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
                data["sources"][source][quest.questLine] = progData = {"novice": {"complete": len(Quest.objects(questLine=quest.questLine, source=source, completion__novice__gt=0)), 
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
    allSections = set([q.section for q in allQuests])
    data = {"source": questSource, "questLine": questLine,
            "sections": {}}
    for section in allSections:
        data["sections"][section] = []
        for quest in allQuests:
            if(quest.section == section):
                data["sections"][section].append(quest)
    return render(request, "skyrimseQuestLine.html", {'data': data})