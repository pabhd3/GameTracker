from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index), # added url object
    url(r"^progress/$", views.progress),
    url(r"^progress/[a-zA-Z0-9]+$", views.progressDetail)
]