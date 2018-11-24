from django.db import models
import mongoengine
from mongoengine.context_managers import switch_db

# Create your models here.
class Progress(mongoengine.Document):
    created = mongoengine.fields.StringField(max_length=50)
    difficulty = mongoengine.fields.StringField(max_length=10)