# Generated by Django 5.2.3 on 2025-07-20 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='cats',
            field=models.ManyToManyField(blank=True, to='core.cats'),
        ),
    ]
