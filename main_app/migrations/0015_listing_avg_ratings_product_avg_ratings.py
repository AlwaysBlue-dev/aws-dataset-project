# Generated by Django 4.2.1 on 2024-03-18 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0014_listing_total_ratings_product_total_ratings'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='avg_ratings',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='avg_ratings',
            field=models.FloatField(default=0),
        ),
    ]
