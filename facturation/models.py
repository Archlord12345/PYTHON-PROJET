from django.db import models

class Client(models.Model):
    nom = models.CharField(max_length=100)
    type = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nom


class Utilisateur(models.Model):
    login = models.CharField(max_length=50, unique=True)
    mot_de_passe = models.CharField(max_length=255)
    role = models.CharField(max_length=50)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.login


class Article(models.Model):
    code_barres = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=100)
    prix_HT = models.DecimalField(max_digits=10, decimal_places=2)
    prix_TTC = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actuel = models.PositiveIntegerField(default=0)
    stock_minimum = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom


class Facture(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    caissier = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Facture {self.id} - {self.client.nom}"


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
