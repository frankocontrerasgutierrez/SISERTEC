from django import forms
from django.contrib.auth.models import User

from core.roles import TECNICO
from inventario.models import Repuesto

from .models import OrdenTrabajo


class OrdenForm(forms.ModelForm):
    class Meta:
        model = OrdenTrabajo
        fields = ["equipo", "falla_reportada"]
        widgets = {"falla_reportada": forms.Textarea(attrs={"rows": 3})}

    def clean_falla_reportada(self):
        falla = self.cleaned_data["falla_reportada"].strip()
        if len(falla) < 5:
            raise forms.ValidationError("Describa la falla con más detalle.")
        return falla


class AsignarTecnicoForm(forms.Form):
    tecnico = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name=TECNICO, is_active=True), label="Técnico"
    )


class DiagnosticoPresupuestoForm(forms.Form):
    diagnostico = forms.CharField(label="Diagnóstico (falla real detectada)", widget=forms.Textarea(attrs={"rows": 3}))
    detalle = forms.CharField(label="Detalle del presupuesto", widget=forms.Textarea(attrs={"rows": 3}))
    monto = forms.DecimalField(label="Monto (CLP)", min_value=0, max_digits=10, decimal_places=0)


class RespuestaPresupuestoForm(forms.Form):
    respuesta = forms.ChoiceField(
        choices=[("APROBADO", "Cliente aprueba"), ("RECHAZADO", "Cliente rechaza")],
        widget=forms.RadioSelect,
    )


class ReparacionForm(forms.Form):
    descripcion = forms.CharField(label="Trabajo realizado", widget=forms.Textarea(attrs={"rows": 3}))
    repuesto = forms.ModelChoiceField(queryset=Repuesto.objects.all(), required=False, label="Repuesto utilizado")
    cantidad = forms.IntegerField(min_value=1, required=False, initial=1)

    def clean(self):
        datos = super().clean()
        if datos.get("repuesto") and not datos.get("cantidad"):
            self.add_error("cantidad", "Indique la cantidad usada.")
        return datos


class ObservacionForm(forms.Form):
    observacion = forms.CharField(required=False, max_length=255, label="Observación")


class ConsultaClienteForm(forms.Form):
    numero = forms.IntegerField(label="Número de orden", min_value=1)
    codigo = forms.CharField(label="Código de consulta", max_length=8, min_length=8)

    def clean_codigo(self):
        return self.cleaned_data["codigo"].strip().upper()
