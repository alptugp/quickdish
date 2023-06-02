# Generated by Django 4.2.1 on 2023-06-01 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DietaryRestriction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vegan', models.BooleanField(default=False)),
                ('vegetarian', models.BooleanField(default=False)),
                ('gluten_free', models.BooleanField(default=False)),
            ],
        ),
    ]