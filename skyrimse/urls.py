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
    url(r"^progress/refreshProgress=\w+", views.refreshProgress),
    url(r"^progress/levelProgress=\w+", views.levelProgress),
    # Quest Related
    url(r"^quests/$", views.quests),
    url(r"^quests/loadQuests=\w+", views.questsLoad),
    url(r"^quests/\w+-\w+", views.questLine),
    url(r"^quests/completeQuest=\w+", views.completeQuest)
]