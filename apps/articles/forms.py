from decimal import Decimal

from django import forms

from facturation.models import Article

FIELD_CLASS = (
    "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-zinc-700 "
    "bg-white dark:bg-zinc-900 text-slate-900 dark:text-zinc-100 "
    "placeholder:text-slate-400 dark:placeholder:text-zinc-500 "
    "focus:outline-none focus:ring-2 focus:ring-blue-500/40"
)

TEXTAREA_CLASS = FIELD_CLASS + " resize-y"


class TvaPercentMixin:
    """Expose la TVA en pourcentage dans le formulaire (ex: 5.5)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and getattr(self.instance, "pk", None):
            self.initial["taux_TVA"] = self._display_tva_percent(self.instance.taux_TVA)

    @staticmethod
    def _display_tva_percent(decimal_value):
        return str(round(float(decimal_value) * 100, 1)).rstrip("0").rstrip(".")

    def clean_taux_TVA(self):
        value = self.cleaned_data["taux_TVA"]
        return Decimal(value) / Decimal("100")


class ArticleFormCreate(TvaPercentMixin, forms.ModelForm):
    """Formulaire pour la création d'articles."""

    taux_TVA = forms.DecimalField(
        min_value=0,
        max_value=100,
        decimal_places=1,
        initial=5.5,
        widget=forms.NumberInput(
            attrs={
                "class": FIELD_CLASS,
                "placeholder": "Ex: 5.5",
                "step": "0.1",
                "min": "0",
                "max": "100",
            }
        ),
    )

    class Meta:
        model = Article
        fields = [
            "code_barres",
            "nom",
            "description",
            "prix_HT",
            "taux_TVA",
            "prix_TTC",
            "categorie",
            "unite_mesure",
            "stock_actuel",
            "stock_minimum",
            "actif",
        ]
        widgets = {
            "code_barres": forms.TextInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "Code-barres (EAN13)",
                    "maxlength": "13",
                }
            ),
            "nom": forms.TextInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "Nom du produit",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "placeholder": "Description du produit",
                    "rows": 3,
                }
            ),
            "prix_HT": forms.NumberInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "0.00",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "prix_TTC": forms.HiddenInput(),
            "categorie": forms.Select(
                attrs={
                    "class": FIELD_CLASS,
                }
            ),
            "unite_mesure": forms.TextInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "ex: kg, L, pcs",
                }
            ),
            "stock_actuel": forms.NumberInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "0",
                    "min": "0",
                }
            ),
            "stock_minimum": forms.NumberInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "0",
                    "min": "0",
                }
            ),
            "actif": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 rounded border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-blue-600 focus:ring-blue-500",
                }
            ),
        }


class ArticleFormEdit(TvaPercentMixin, forms.ModelForm):
    """Formulaire pour l'edition d'articles (sans code-barres)."""

    taux_TVA = forms.DecimalField(
        min_value=0,
        max_value=100,
        decimal_places=1,
        widget=forms.NumberInput(
            attrs={
                "class": FIELD_CLASS,
                "placeholder": "Ex: 5.5",
                "step": "0.1",
                "min": "0",
                "max": "100",
            }
        ),
    )

    class Meta:
        model = Article
        fields = [
            "nom",
            "description",
            "prix_HT",
            "taux_TVA",
            "prix_TTC",
            "categorie",
            "unite_mesure",
            "stock_actuel",
            "stock_minimum",
            "actif",
        ]
        widgets = ArticleFormCreate.Meta.widgets.copy()
        widgets.pop("code_barres", None)

    def clean(self):
        cleaned_data = super().clean()
        prix_ht = cleaned_data.get("prix_HT")
        taux_tva = cleaned_data.get("taux_TVA")

        if prix_ht is not None and taux_tva is not None:
            # Calcul automatique du prix TTC
            prix_ttc = prix_ht * (Decimal("1") + taux_tva)
            cleaned_data["prix_TTC"] = prix_ttc.quantize(Decimal("0.01"))

        return cleaned_data


# Alias pour compatibilite.
ArticleForm = ArticleFormCreate
