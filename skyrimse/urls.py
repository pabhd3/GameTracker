from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r"^progress/$", views.progress),
    url(r"^progress/[a-zA-Z0-9]+$", views.progressDetail),
    url(r"^progress/addDifficulty", views.addDifficulty),
    url(r"^progress/deleteDifficulty", views.deleteDifficulty),
    url(r"^progress/levelSkill=\w+&difficulty=\w+", views.levelSkill)
]