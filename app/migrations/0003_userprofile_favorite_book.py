# Generated by Django 5.0.1 on 2024-01-11 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='favorite_book',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
