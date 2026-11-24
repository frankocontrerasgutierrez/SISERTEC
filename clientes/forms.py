from django import forms

from core.validadores import normalizar_rut

from .models import Cliente, Equipo


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["rut", "nombre", "email", "telefono", "direccion"]
        widgets = {"rut": forms.TextInput(attrs={"placeholder": "12.345.678-5"})}

    def clean_rut(self):
        # Se normaliza antes de validar unicidad, así '12.345.678-5' y '12345678-5' son el mismo RUT.
        rut = normalizar_rut(self.cleaned_data["rut"])
        existe = Cliente.objects.filter(rut=rut).exclude(pk=self.instance.pk).exists()
        if existe:
            raise forms.ValidationError("Ya existe un cliente con este RUT.")
        return rut

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if len(nombre) < 3:
            raise forms.ValidationError("Ingrese el nombre completo.")
        return nombre


class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ["cliente", "tipo", "marca", "modelo", "numero_serie", "descripcion"]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3})}
