from django import forms


class SingleInputForm(forms.Form):
    name = forms.CharField(max_length=100)
