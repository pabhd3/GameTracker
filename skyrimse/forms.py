from django import forms

class CollectibleNotes(forms.Form):
    notes = forms.CharField(label="Notes")