# Generated by Django 5.1.7 on 2025-04-18 19:12

import NumerosPseudoaleatorios.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CongruencialMultiplicativo',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('tipo', models.CharField(choices=[('CM', 'Congruencial Multiplicativo'), ('VN', 'Von Neumann')], max_length=2)),
                ('semilla', models.PositiveIntegerField()),
                ('cantidad', models.PositiveIntegerField(validators=[NumerosPseudoaleatorios.models.validar_cantidad])),
                ('numeros', models.JSONField(default=list, validators=[NumerosPseudoaleatorios.models.validar_numeros])),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('t', models.PositiveIntegerField()),
                ('p', models.PositiveIntegerField()),
                ('modulo', models.PositiveIntegerField()),
                ('multiplicador', models.BigIntegerField(editable=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VonNeumann',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('tipo', models.CharField(choices=[('CM', 'Congruencial Multiplicativo'), ('VN', 'Von Neumann')], max_length=2)),
                ('semilla', models.PositiveIntegerField()),
                ('cantidad', models.PositiveIntegerField(validators=[NumerosPseudoaleatorios.models.validar_cantidad])),
                ('numeros', models.JSONField(default=list, validators=[NumerosPseudoaleatorios.models.validar_numeros])),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
