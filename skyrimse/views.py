from django.shortcuts import render, redirect
from skyrimse.models import *
from mongoengine.context_managers import switch_db
from datetime import datetime

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
    progress.created = datetime.strftime(datetime.now(), "%A %B %d, %Y %H:%M:%S:%f %Z")
    progress.difficulty = request.path.split("=")[1]
    progress.completion = Completion(vanilla=0, mod=0)
    progress.save()
    return redirect("/skyrimse/progress")

def deleteDifficulty(request):
    deleteID = request.path.split("=")[1]
    Progress.objects(id=deleteID).delete()
    return redirect("/skyrimse/progress")

def progressDetail(request):
    progressID = request.path.split("/skyrimse/progress/")[1]
    data = Progress.objects(id=progressID)[0]
    return render(request, "skyrimseProgressDetail.html", {'data': data})