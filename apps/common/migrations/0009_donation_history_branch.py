# Generated by Django 4.0.2 on 2022-03-04 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0008_donation_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation_history',
            name='branch',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]