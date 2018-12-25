from django.db import models
from mongoengine import Document, EmbeddedDocument, fields
from mongoengine.context_managers import switch_db
from json import dumps

###################################
##### Progress Related Models #####
###################################
class Completion(EmbeddedDocument):
    vanilla = fields.FloatField(min_value=0)
    mod = fields.FloatField(min_value=0)

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
    words = fields.IntField(min_value=0)
    modWords = fields.IntField(min_value=0)
    locations = fields.IntField(min_value=0)
    modLocations = fields.IntField(min_value=0)
    spells = fields.IntField(min_value=0)
    modSpells = fields.IntField(min_value=0)
    enchantments = fields.IntField(min_value=0)
    modEnchantments = fields.IntField(min_value=0)  
    ingredients = fields.IntField(min_value=0)
    modIngredients = fields.IntField(min_value=0) 
    weapons = fields.IntField(min_value=0)
    modWeapons = fields.IntField(min_value=0)
    armors = fields.IntField(min_value=0)
    modArmors = fields.IntField(min_value=0)
    jewelry = fields.IntField(min_value=0)
    modJewelry = fields.IntField(min_value=0)
    books = fields.IntField(min_value=0)
    modBooks = fields.IntField(min_value=0)
    keys = fields.IntField(min_value=0)
    modKeys = fields.IntField(min_value=0)
    collectibles = fields.IntField(min_value=0)
    modCollectibles = fields.IntField(min_value=0)
    total = fields.IntField(min_value=0)
    modTotal = fields.IntField(min_value=0)

    def __str__(self):
        return dumps({"quests": {"vanilla": self.quests, "mod": self.modQuests},
            "perks": {"vanilla": self.perks, "mod": self.modPerks},
            "words": {"vanilla": self.words, "mod": self.modWords},
            "locations": {"vanilla": self.locations, "mod": self.modLocations},
            "spells": {"vanilla": self.spells, "mod": self.modSpells},
            "enchantments": {"vanilla": self.enchantments, "mod": self.modEnchantments},
            "ingredients": {"vanilla": self.ingredients, "mod": self.modIngredients},
            "weapons": {"vanilla": self.weapons, "mod": self.modWeapons},
            "armors": {"vanilla": self.armors, "mod": self.modArmors},
            "jewelry": {"vanilla": self.jewelry, "mod": self.modJewelry},
            "books": {"vanilla": self.books, "mod": self.modBooks},
            "keys": {"vanilla": self.keys, "mod": self.modKeys},
            "collectibles": {"vanilla": self.collectibles, "mod": self.modCollectibles},
            "total": {"vanilla": self.total, "mod": self.modTotal}}, indent=4)
    

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
        return dumps({"created": self.created, "difficulty": self.difficulty,
            "completion": {"vanilla": self.completion.vanilla, "mod": self.completion.mod},
            "level": self.level, "health": self.health, "magicka": self.magicka, 
            "stamina": self.stamina}, indent=4)
    
    meta = {'db_alias': 'skyrimse'}

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

    def __str__(self):
        return dumps({"novice": self.novice, "apprentice": self.apprentice,
            "adept": self.adept, "expert": self.expert, "master": self.master,
            "legendary": self.legendary}, indent=4)

class Quest(Document):
    name = fields.StringField()
    questLine = fields.StringField()
    source = fields.StringField()
    section = fields.StringField()
    completion = fields.EmbeddedDocumentField(Tracker)
    radiant = fields.BooleanField()

    def __str__(self):
        return dumps({"name": self.name, "questLine": self.questLine, 
            "source": self.source, "section": self.section, 
            "radiant": self.radiant}, indent=4) 

    meta = {'indexes': [
        {'fields': ['$name', "$source", "$questLine"],
         'default_language': 'english',
         'weights': {'name': 10, 'source': 2, 'questLine': 5}
        }
    ]}

###############################
##### Perk Related Models #####
###############################
class Perk(Document):
    name = fields.StringField()
    source = fields.StringField()
    description = fields.StringField()
    skill = fields.StringField()
    level = fields.IntField()
    completion = fields.EmbeddedDocumentField(Tracker)

    def __str__(self):
        return dumps({"name": self.name, "skill": self.skill, 
            "description": self.description, "level": self.level, 
            "source": self.source}, indent=4) 

    meta = {'indexes': [
        {'fields': ['$name', "$source", "$description", "$skill"],
         'default_language': 'english',
         'weights': {'name': 10, 'source': 2, 'description': 7, 'skill': 5}
        }
    ]}

################################
##### Shout Related Models #####
################################
class Word(EmbeddedDocument):
    original = fields.StringField()
    translation = fields.StringField()
    cooldown = fields.IntField()
    location = fields.StringField()
    completion = fields.EmbeddedDocumentField(Tracker)

    def __str__(self):
        return dumps({"original": self.original, "translation": self.translation,
            "location": self.location}, indent=4)

class Shout(Document):
    name = fields.StringField()
    source = fields.StringField()
    description = fields.StringField()
    words = fields.EmbeddedDocumentListField(Word)

    def __str__(self):
        data = {"name": self.name, "source": self.source, 
            "description": self.description}
        return dumps(data, indent=4)

    meta = {'indexes': [
        {'fields': ['$name', "$source", "$description"],
         'default_language': 'english',
         'weights': {'name': 10, 'source': 2, 'description': 7}
        }
    ]}

############################
##### Location Related #####
############################
class Location(Document):
    name = fields.StringField()
    source = fields.StringField()
    locationType = fields.StringField()
    completion = fields.EmbeddedDocumentField(Tracker)

    def __str__(self):
        return dumps({"name": self.name, "source": self.source,
            "location": self.locationType}, indent=4)

    meta = {'indexes': [
        {'fields': ['$name', "$source"],
         'default_language': 'english',
         'weights': {'name': 10, 'source': 2}
        }
    ]}

#########################
##### Spell Related #####
#########################
class Spell(Document):
    name = fields.StringField()
    source = fields.StringField()
    school = fields.StringField()
    level = fields.StringField()
    description = fields.StringField()
    completion = fields.EmbeddedDocumentField(Tracker)

    def __str__(self):
        return dumps({"name": self.name, "source": self.source, "school": self.school,
            "level": self.level, "description": self.description}, indent=4)

    meta = {'indexes': [
        {'fields': ['$name', "$source", "$description"],
         'default_language': 'english',
         'weights': {'name': 10, 'source': 2, 'description': 7}
        }
    ]}

###############################
##### Enchantment Related #####
###############################
class Enchantment(Document):
    name = fields.StringField()
    source = fields.StringField()
    enchantmentType = fields.StringField()
    description = fields.StringField()
    completion = fields.EmbeddedDocumentField(Tracker)

    def __str__(self):
        return dumps({"name": self.name, "source": self.source, 
            "type": self.enchantmentType, "description": self.description}, indent=4)

    meta = {'indexes': [
        {'fields': ['$name', "$source", "$description"],
         'default_language': 'english',
         'weights': {'name': 10, 'source': 2, 'description': 7}
        }
    ]}

##############################
##### Ingredient Related #####
##############################
class Effect(EmbeddedDocument):
    name = fields.StringField()
    order = fields.StringField()
    completion = fields.EmbeddedDocumentField(Tracker)

    def __str__(self):
        return dumps({"name": self.name, "order": self.order}, indent=4)

class Ingredient(Document):
    name = fields.StringField()
    source = fields.StringField()
    locations = fields.StringField()
    effects = fields.EmbeddedDocumentListField(Effect)

    def __str__(self):
        return dumps({"name": self.name, "source": self.source}, indent=4)

    meta = {'indexes': [
        {'fields': ['$name', "$source"],
         'default_language': 'english',
         'weights': {'name': 10, 'source': 2}
        }
    ]}

##########################
##### Weapon Related #####
##########################
class Weapon(Document):
    name = fields.StringField()
    source = fields.StringField()
    weaponClass = fields.StringField()
    weaponType = fields.StringField()
    completion = fields.EmbeddedDocumentField(Tracker)

    def __str__(self):
        return dumps({"name": self.name, "source": self.source,
            "class": self.weaponClass, "type": self.weaponType}, indent=4)

    meta = {'indexes': [
        {'fields': ['$name', "$source", "$weaponClass", "$weaponType"],
         'default_language': 'english',
         'weights': {'name': 10, 'source': 2, 'weaponClass': 1, 'weaponType': 1}
        }
    ]}

#########################
##### Armor Related #####
#########################
class Armor(Document):
    name = fields.StringField()
    source = fields.StringField()
    armorClass = fields.StringField()
    armorType = fields.StringField()
    completion = fields.EmbeddedDocumentField(Tracker)

    def __str__(self):
        return dumps({"name": self.name, "source": self.source,
            "class": self.armorClass, "type": self.armorType}, indent=4)

    meta = {'indexes': [
        {'fields': ['$name', "$source", "$armorClass", "$armorType"],
         'default_language': 'english',
         'weights': {'name': 10, 'source': 2, 'armorClass': 1, 'armorType': 1}
        }
    ]}

###########################
##### Jewelry Related #####
###########################
class Jewelry(Document):
    name = fields.StringField()
    source = fields.StringField()
    jewelryClass = fields.StringField()
    jewelryType = fields.StringField()
    completion = fields.EmbeddedDocumentField(Tracker)

    def __str__(self):
        return dumps({"name": self.name, "source": self.source,
            "class": self.jewelryClass, "type": self.jewelryType}, indent=4)

    meta = {'indexes': [
        {'fields': ['$name', "$source", "$jewelryClass", "$jewelryType"],
         'default_language': 'english',
         'weights': {'name': 10, 'source': 2, 'jewelryClass': 1, 'jewelryType': 1}
        }
    ]}

########################
##### Book Related #####
########################
class Book(Document):
    name = fields.StringField()
    source = fields.StringField()
    bookType = fields.StringField()
    startsWith = fields.StringField()
    completion = fields.EmbeddedDocumentField(Tracker)

    def __str__(self):
        return dumps({"name": self.name, "source": self.source,
            "type": self.bookType}, indent=4)
    
    meta = {'indexes': [
        {'fields': ['$name', "$source", "$bookType"],
         'default_language': 'english',
         'weights': {'name': 10, 'source': 2, 'bookType': 1}
        }
    ]}

#######################
##### Key Related #####
#######################
class Key(Document):
    name = fields.StringField()
    source = fields.StringField()
    location = fields.StringField()
    completion = fields.EmbeddedDocumentField(Tracker)

    def __str__(self):
        return dumps({"name": self.name, "source": self.source,
            "location": self.location}, indent=4)
    
    meta = {'indexes': [
        {'fields': ['$name', "$source", "$location"],
         'default_language': 'english',
         'weights': {'name': 10, 'source': 2, 'location': 1}
        }
    ]}

###############################
##### Collectible Related #####
###############################
class Collectible(Document):
    name = fields.StringField()
    source = fields.StringField()
    collectibleType = fields.StringField()
    notes = fields.ListField()
    completion = fields.EmbeddedDocumentField(Tracker)

    def __str__(self):
        return dumps({"name": self.name, "source": self.source, 
            "type": self.collectibleType, "notes": self.notes}, indent=4)
    
    meta = {'indexes': [
        {'fields': ['$name', "$source", "$notes"],
         'default_language': 'english',
         'weights': {'name': 10, 'source': 2, 'notes': 2}
        }
    ]}

##########################
##### Backup Related #####
##########################
class Backup(Document):
    ts = fields.StringField(max_length=50)
    difficulty = fields.StringField(max_length=10)
    level = fields.IntField(min_value=0)
    health = fields.IntField(min_value=0)
    magicka = fields.IntField(min_value=0)
    stamina = fields.IntField(min_value=0)
    skills = fields.EmbeddedDocumentField(Skills)
    completion = fields.EmbeddedDocumentField(Completion)
    quests = fields.DictField()
    perks = fields.DictField()
    words = fields.DictField()
    locations = fields.DictField()
    spells = fields.DictField()
    enchantments = fields.DictField()
    ingredients = fields.DictField()
    weapons = fields.DictField()
    armors = fields.DictField()
    jewelry = fields.DictField()
    books = fields.DictField()
    keys = fields.DictField()
    collectibles = fields.DictField()