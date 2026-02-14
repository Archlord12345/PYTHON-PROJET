from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("facturation", "0007_alter_facture_mode_paiement"),
    ]

    operations = [
        migrations.AlterField(
            model_name="facture",
            name="client",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="facturation.client"),
        ),
    ]

