from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'skyrimseIndex.html')

def progress(request):
    return render(request, template_name="skyrimseProgress.html")