from django.db import models
import mongoengine
from mongoengine.context_managers import switch_db

###################################
##### Progress Related Models #####
###################################
class Completion(mongoengine.EmbeddedDocument):
    vanilla = mongoengine.fields.FloatField(min_value=0, max_value=1)
    mod = mongoengine.fields.FloatField(min_value=0, max_value=1)

class Progress(mongoengine.Document):
    created = mongoengine.fields.StringField(max_length=50)
    difficulty = mongoengine.fields.StringField(max_length=10)
    completion = mongoengine.fields.EmbeddedDocumentField(Completion)