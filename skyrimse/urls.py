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
    url(r"^progress/backupProgress=\w+", views.backup),
    url(r"^progress/loadBackup=\w+", views.loadBackup),
    # Quest Related
    url(r"^quests/$", views.quests),
    url(r"^quests/loadQuests=\w+", views.questsLoad),
    url(r"^quests/details/", views.questDetails),
    url(r"^quests/completeQuest=\w+", views.completeQuest),
    # Perk Related
    url(r"^perks/$", views.perks),
    url(r"^perks/loadPerks=\w+", views.perksLoad),
    url(r"^perks/details/", views.perkDetails),
    url(r"^perks/learnPerk=\w+", views.learnPerk),
    # Shout Related
    url(r"^shouts/$", views.shouts),
    url(r"^shouts/loadShouts=\w+", views.shoutsLoad),
    url(r"^shouts/learnWord=\w+", views.learnWord),
    url(r"^shouts/details/", views.shoutsDetail),
    # Location Related
    url(r"^locations/$", views.locations),
    url(r"^locations/loadLocations=\w+", views.locationsLoad),
    url(r"^locations/visitLocation=\w+", views.visitLocation),
    url(r"^locations/details/+", views.locationsDetail),
    # Spells Related
    url(r"^spells/$", views.spells),
    url(r"^spells/loadSpells=\w+", views.spellsLoad),
    url(r"^spells/learnSpell=\w+", views.learnSpell), 
    url(r"^spells/details/", views.spellDetails),
    # Enchantment Related
    url(r"^enchantments/$", views.enchantments),
    url(r"^enchantments/loadEnchantments=\w+", views.enchantmentsLoad),
    url(r"^enchantments/learnEnchantment=\w+", views.learnEnchantment),
    url(r"^enchantments/details/", views.enchantmentDetails),
    # Ingredients Related
    url(r"^ingredients/$", views.ingredients),
    url(r"^ingredients/loadIngredients=\w+", views.ingredientsLoad),
    url(r"^ingredients/learnEffect=\w+", views.learnEffect),
    url(r"^ingredients/details/", views.ingredientsDetail),
    # Weapon Related
    url(r"^weapons/$", views.weapons),
    url(r"^weapons/loadWeapons=\w+", views.weaponsLoad),
    url(r"^weapons/collectWeapon=\w+", views.collectWeapon),
    url(r"^weapons/details/", views.weaponDetails),
    # Armor Related
    url(r"^armors/$", views.armors),
    url(r"^armors/loadArmors=\w+", views.armorsLoad),
    url(r"^armors/collectArmor=\w+", views.collectArmor),
    url(r"^armors/details/", views.armorDetails),
    # Jewelry Related
    url(r"^jewelry/$", views.jewelry),
    url(r"^jewelry/loadJewelry=\w+", views.jewelryLoad),
    url(r"^jewelry/collectJewelry=\w+", views.collectJewelry),
    url(r"^jewelry/details/", views.jewelryDetails),
    # Books Related
    url(r"^books/$", views.books),
    url(r"^books/loadBooks=\w+", views.booksLoad),
    url(r"^books/readBook=\w+", views.readBook),
    url(r"^books/details/", views.bookDetails),
    # Keys Related
    url(r"^keys/$", views.keys),
    url(r"^keys/loadKeys=\w+", views.keysLoad),
    url(r"^keys/collectKey=\w+", views.collectKey),
    url(r"^keys/details/", views.keyDetails),
    # Collectibles Related
    url(r"^collectibles/$", views.collectibles),
    url(r"^collectibles/loadCollectibles=\w+", views.collectiblesLoad),
    url(r"^collectibles/collectCollectible=\w+", views.collectCollectible),
    url(r"^collectibles/details/", views.collectibleDetails),
    url(r"^collectibleNotes=\w+", views.collectibleNotes),
    # Testing Area
    url(r"^testing/$", views.testing)
]