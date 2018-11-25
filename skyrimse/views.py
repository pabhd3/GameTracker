from django.http import HttpResponse
from django.shortcuts import render, redirect
from skyrimse.models import *
from mongoengine.context_managers import switch_db
from datetime import datetime
from .customScripts import plotRader

# Create your views here.
def index(request):
    return render(request, 'skyrimseIndex.html')

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