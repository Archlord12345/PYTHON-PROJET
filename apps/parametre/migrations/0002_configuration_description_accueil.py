from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parametre", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="configuration",
            name="description_accueil",
            field=models.CharField(
                blank=True,
                default="L'intelligence au service de votre point de vente.",
                max_length=255,
                null=True,
            ),
        ),
    ]

