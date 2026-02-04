from django.db import models

class Client(models.Model):
    TYPE_CHOICES = [
        ("enregistre", "Enregistré"),
        ("anonyme", "Anonyme"),
    ]

    nom = models.CharField(max_length=100, blank=True, null=True)
    prenom = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        full_name = " ".join(part for part in [self.prenom, self.nom] if part)
        return full_name or "Client"


class Utilisateur(models.Model):
    ROLE_CHOICES = [
        ("Administrateur", "Administrateur"),
        ("Gestionnaire", "Gestionnaire"),
        ("Caissier", "Caissier"),
        ("Comptable", "Comptable"),
    ]

    login = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    mot_de_passe = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.login


class Article(models.Model):
    code_barres = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    prix_HT = models.DecimalField(max_digits=10, decimal_places=2)
    prix_TTC = models.DecimalField(max_digits=10, decimal_places=2)
    taux_TVA = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        default=0,
        help_text="Taux en décimal (ex: 0.18 pour 18%)",
    )
    categorie = models.CharField(max_length=100, blank=True, null=True)
    unite_mesure = models.CharField(max_length=50, blank=True, null=True)
    stock_actuel = models.PositiveIntegerField(default=0)
    stock_minimum = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom


class Facture(models.Model):
    MODE_PAIEMENT_CHOICES = [
        ("especes", "Espèces"),
        ("carte", "Carte"),
        ("cheque", "Chèque"),
        ("virement", "Virement"),
        ("ticket_resto", "Ticket resto"),
        ("mixte", "Mixte"),
    ]
    STATUT_CHOICES = [
        ("payee", "Payée"),
        ("annulee", "Annulée"),
        ("remboursee", "Remboursée"),
    ]

    date_facture = models.DateTimeField(auto_now_add=True)
    montant_HT = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    montant_TVA = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    montant_TTC = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES, blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="payee")
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    caissier = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Facture {self.id} - {self.client}"


class DetailFacture(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name="details")
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_ligne = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.article.nom} x {self.quantite}"


class Retour(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    quantite_retournee = models.PositiveIntegerField()
    raison = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=50)

    def __str__(self):
        return f"Retour {self.id} - {self.article.nom}"


class Audit(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    type_action = models.CharField(max_length=50)
    date_action = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.type_action} par {self.utilisateur.login}"
