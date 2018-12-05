from django.db import models
from mongoengine import Document, EmbeddedDocument, fields
from mongoengine.context_managers import switch_db
from json import dumps

###################################
##### Progress Related Models #####
###################################
class Completion(EmbeddedDocument):
    vanilla = fields.FloatField(min_value=0, max_value=1)
    mod = fields.FloatField(min_value=0, max_value=1)

class Skill(EmbeddedDocument):
    level = fields.IntField(min_value=0)
    legendary = fields.IntField(min_value=0)

class Skills(EmbeddedDocument):
    alchemy = fields.EmbeddedDocumentField(Skill)
    alteration = fields.EmbeddedDocumentField(Skill)
    archery = fields.EmbeddedDocumentField(Skill)
    block = fields.EmbeddedDocumentField(Skill)
    conjuration = fields.EmbeddedDocumentField(Skill)
    destruction = fields.EmbeddedDocumentField(Skill)
    enchanting = fields.EmbeddedDocumentField(Skill)
    heavyArmor = fields.EmbeddedDocumentField(Skill)
    illusion = fields.EmbeddedDocumentField(Skill)
    lightArmor = fields.EmbeddedDocumentField(Skill)
    lockpicking = fields.EmbeddedDocumentField(Skill)
    oneHanded = fields.EmbeddedDocumentField(Skill)
    pickPocket = fields.EmbeddedDocumentField(Skill)
    restoration = fields.EmbeddedDocumentField(Skill)
    smithing = fields.EmbeddedDocumentField(Skill)
    sneak = fields.EmbeddedDocumentField(Skill)
    speech = fields.EmbeddedDocumentField(Skill)
    twoHanded = fields.EmbeddedDocumentField(Skill)

class Collected(EmbeddedDocument):
    quests = fields.IntField(min_value=0)
    modQuests = fields.IntField(min_value=0)
    perks = fields.IntField(min_value=0)
    modPerks = fields.IntField(min_value=0)
    total = fields.IntField(min_value=0)
    modTotal = fields.IntField(min_value=0)

class Progress(Document):
    created = fields.StringField(max_length=50)
    difficulty = fields.StringField(max_length=10)
    completion = fields.EmbeddedDocumentField(Completion)
    level = fields.IntField(min_value=0)
    health = fields.IntField(min_value=0)
    magicka = fields.IntField(min_value=0)
    stamina = fields.IntField(min_value=0)
    skills = fields.EmbeddedDocumentField(Skills)
    collected = fields.EmbeddedDocumentField(Collected)
    collectedTotal = fields.EmbeddedDocumentField(Collected)

    def __str__(self):
        data = {"created": self.created, "difficulty": self.difficulty}
        return dumps(data, indent=4) 

#########################
##### Quest Related #####
#########################
class Tracker(EmbeddedDocument):
    novice = fields.IntField(min_value=0)
    apprentice = fields.IntField(min_value=0)
    adept = fields.IntField(min_value=0)
    expert = fields.IntField(min_value=0)
    master = fields.IntField(min_value=0)
    legendary = fields.IntField(min_value=0)

class Quest(Document):
    name = fields.StringField()
    questLine = fields.StringField()
    source = fields.StringField()
    section = fields.StringField()
    completion = fields.EmbeddedDocumentField(Tracker)
    radiant = fields.BooleanField()

###############################
##### Perk Related Models #####
###############################
class Perk(Document):
    skill = fields.StringField()
    name = fields.StringField()
    description = fields.StringField()
    level = fields.IntField()
    source = fields.StringField()
    completion = fields.EmbeddedDocumentField(Tracker)

################################
##### Shout Related Models #####
################################
class Word(EmbeddedDocument):
    original = fields.StringField()
    translation = fields.StringField()
    cooldown = fields.IntField()
    location = fields.StringField()
    completion = fields.EmbeddedDocumentField(Tracker)

class Shout(Document):
    name = fields.StringField()
    source = fields.StringField()
    description = fields.StringField()
    words = fields.EmbeddedDocumentListField(Word)