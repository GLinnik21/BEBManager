from django import forms


class BoardForm(forms.Form):
    name = forms.CharField(max_length=100)
