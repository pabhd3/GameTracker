from django.db import models
from mongoengine import Document, EmbeddedDocument, fields
from mongoengine.context_managers import switch_db

###################################
##### Progress Related Models #####
###################################
class Completion(EmbeddedDocument):
    vanilla = fields.FloatField(min_value=0, max_value=1)
    mod = fields.FloatField(min_value=0, max_value=1)

class Skills(EmbeddedDocument):
    alchemy = fields.IntField(min_value=0)
    alteration = fields.IntField(min_value=0)
    archery = fields.IntField(min_value=0)
    block = fields.IntField(min_value=0)
    conjuration = fields.IntField(min_value=0)
    destruction = fields.IntField(min_value=0)
    enchanting = fields.IntField(min_value=0)
    heavyArmor = fields.IntField(min_value=0)
    illusion = fields.IntField(min_value=0)
    lightArmor = fields.IntField(min_value=0)
    lockpicking = fields.IntField(min_value=0)
    oneHanded = fields.IntField(min_value=0)
    pickPocket = fields.IntField(min_value=0)
    restoration = fields.IntField(min_value=0)
    smithing = fields.IntField(min_value=0)
    sneak = fields.IntField(min_value=0)
    speech = fields.IntField(min_value=0)
    twoHanded = fields.IntField(min_value=0)

class Progress(Document):
    created = fields.StringField(max_length=50)
    difficulty = fields.StringField(max_length=10)
    completion = fields.EmbeddedDocumentField(Completion)
    skills = fields.EmbeddedDocumentField(Skills)

#########################
##### Quest Related #####
#########################
class Quest(Document):
    name = fields.StringField()
    questLine = fields.StringField()
    source = fields.StringField()