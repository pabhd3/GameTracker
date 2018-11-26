from django.conf.urls import url
from . import views

urlpatterns = [
    # Home Page
    url(r'^$', views.index),
    # Difficulty Progress Related
    url(r"^progress/$", views.progress),
    url(r"^progress/[a-zA-Z0-9]+$", views.progressDetail),
    url(r"^progress/addDifficulty=\w+", views.addDifficulty),
    url(r"^progress/deleteDifficulty=\w+", views.deleteDifficulty),
    url(r"^progress/levelSkill=\w+&difficulty=\w+", views.levelSkill),
    # Quest Related
    url(r"^quests/$", views.quests),
    url(r"^quests/loadQuests=\w+", views.questsLoad)
]