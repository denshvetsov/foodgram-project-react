# Generated by Django 4.0 on 2022-07-09 19:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_alter_ingredient_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(max_length=150, validators=[django.core.validators.MinLengthValidator(3, 'введите более 3 символов'), django.core.validators.RegexValidator('^[a-zA-Zа-яА-Я]+$')], verbose_name='Название блюда'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='text',
            field=models.TextField(max_length=3000, verbose_name='Описание блюда'),
        ),
    ]
