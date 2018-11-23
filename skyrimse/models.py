from django.db import models
import mongoengine
from mongoengine.context_managers import switch_db

# Create your models here.
class Progress(mongoengine.Document):
    difficulty = mongoengine.fields.StringField()
