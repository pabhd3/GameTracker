from django import forms

class Search(forms.Form):
    search = forms.CharField(label="search")