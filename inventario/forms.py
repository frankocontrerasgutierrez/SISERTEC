from django import forms

from .models import Repuesto


class RepuestoForm(forms.ModelForm):
    class Meta:
        model = Repuesto
        fields = ["codigo", "nombre", "descripcion", "stock", "stock_minimo", "precio_unitario"]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 2})}

    def clean_codigo(self):
        return self.cleaned_data["codigo"].strip().upper()
