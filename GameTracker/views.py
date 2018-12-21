import sys
from django.shortcuts import render
from mongoengine.context_managers import switch_db

# Import views
sys.path.insert(0, "/skyrimse/")
from skyrimse.models import Progress

# Create your views here.
def index(request):
    data = {}
    # Load Skyrim Data
    data["skyrimse"] = sum([(doc["completion"]["vanilla"] + doc["completion"]["mod"])/2 for doc in Progress.objects.all()])/6
    return render(request, 'index.html', {'data': data})