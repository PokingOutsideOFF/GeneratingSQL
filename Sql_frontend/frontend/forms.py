
from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField(label_suffix=".csv")
