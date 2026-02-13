from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

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
    adresse = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        full_name = " ".join(part for part in [self.prenom, self.nom] if part)
        return full_name or "Client"


class UtilisateurManager(BaseUserManager):
    def create_user(self, login, password=None, **extra_fields):
        if not login:
            raise ValueError("L'identifiant (login) est obligatoire")
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'Administrateur')
        return self.create_user(login, password, **extra_fields)

class Utilisateur(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("Administrateur", "Administrateur"),
        ("Gestionnaire", "Gestionnaire"),
        ("Caissier", "Caissier"),
        ("Comptable", "Comptable"),
    ]

    login = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UtilisateurManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['nom', 'role']

    def __str__(self):
        return self.login


class Article(models.Model):
    CATEGORIE_CHOICES = [
        ("boulangerie", "Boulangerie"),
        ("produits_laitiers", "Produits laitiers"),
        ("fruits_legumes", "Fruits et legumes"),
        ("viande", "Viande"),
        ("epicerie", "Epicerie"),
        ("boissons", "Boissons"),
        ("alimentaire", "Alimentaire"),
        ("hygiene", "Hygiene"),
    ]
    UNITE_MESURE_CHOICES = [
        ("unite", "Unite"),
        ("kg", "Kg"),
        ("litre", "Litre"),
        ("piece", "Piece"),
        ("sachet", "Sachet"),
        ("bouteille", "Bouteille"),
        ("sac", "Sac"),
    ]

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
    categorie = models.CharField(
        max_length=100,
        choices=CATEGORIE_CHOICES,
        default="epicerie",
        blank=True,
        null=True,
    )
    unite_mesure = models.CharField(
        max_length=50,
        choices=UNITE_MESURE_CHOICES,
        default="unite",
        blank=True,
        null=True,
    )
    stock_actuel = models.PositiveIntegerField(default=0)
    stock_minimum = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

    @property
    def prix_ht(self):
        return self.prix_HT

    @prix_ht.setter
    def prix_ht(self, value):
        self.prix_HT = value

    @property
    def prix_ttc(self):
        return self.prix_TTC

    @prix_ttc.setter
    def prix_ttc(self, value):
        self.prix_TTC = value

    @property
    def taux_tva(self):
        # Compatibilite module articles: expose en pourcentage.
        return float(self.taux_TVA) * 100

    @taux_tva.setter
    def taux_tva(self, value):
        self.taux_TVA = float(value) / 100

    def is_low_stock(self):
        return self.stock_actuel <= self.stock_minimum

    def is_out_of_stock(self):
        return self.stock_actuel == 0

    def get_stock_status(self):
        if self.stock_actuel == 0:
            return "rupture"
        if self.stock_actuel <= self.stock_minimum:
            return "faible"
        return "ok"


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
