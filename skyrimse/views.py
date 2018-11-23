from django.shortcuts import render
from skyrimse.models import Progress
from mongoengine.context_managers import switch_db

# Create your views here.
def index(request):
    return render(request, 'skyrimseIndex.html')

def progress(request):
    switch_db(cls=Progress, db_alias="skyrimse")
    data = Progress.objects.all()
    return render(request, 'skyrimseProgress.html', {'data': data})

def progressDetail(request):
    data = {"id": request.path.split("/skyrimse/progress/")[1]}
    return render(request, "skyrimseProgressDetail.html", {'data': data})