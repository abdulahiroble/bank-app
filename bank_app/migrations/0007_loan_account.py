# Generated by Django 4.2.1 on 2023-06-03 19:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0006_remove_loan_account_loan_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='account',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='bank_app.account'),
        ),
    ]
