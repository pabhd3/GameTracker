from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index), # added url object
    url(r"^progress/", views.progress)
]