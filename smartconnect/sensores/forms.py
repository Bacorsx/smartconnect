from django import forms
from .models import Sensor, Barrera

class BootstrapForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput,)):
                field.widget.attrs['class'] = 'form-control'

class SensorForm(BootstrapForm):
    class Meta:
        model = Sensor
        fields = ['uid', 'alias', 'estado', 'departamento', 'usuario']

    def clean_uid(self):
        uid = self.cleaned_data['uid']
        if len(uid) < 4:
            raise forms.ValidationError("El UID debe tener al menos 4 caracteres.")
        return uid


class BarreraForm(BootstrapForm):
    class Meta:
        model = Barrera
        fields = ['estado']
