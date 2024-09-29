# Generated by Django 4.0 on 2024-09-29 11:02

from django.db import migrations, models
import django.db.models.deletion
import django_mysql.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Backtesting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strategy', django_mysql.models.EnumField(choices=[('MOMENTUM_V1', 'MOMENTUM_V1')])),
                ('config', models.TextField(max_length=10000)),
                ('purpose', models.TextField(max_length=10000, null=True)),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('time_taken', models.DecimalField(decimal_places=2, max_digits=10)),
                ('success_rate', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'db_table': 'backtesting',
            },
        ),
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('entry_time', models.TimeField()),
                ('entry_point', models.DecimalField(decimal_places=2, max_digits=10)),
                ('entry_conditions', models.TextField(max_length=10000)),
                ('exit_time', models.TimeField()),
                ('exit_point', models.DecimalField(decimal_places=2, max_digits=10)),
                ('exit_conditions', models.TextField(max_length=10000)),
                ('gain', models.DecimalField(decimal_places=2, max_digits=10)),
                ('backtesting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trades', related_query_name='trade', to='backtesting.backtesting')),
            ],
            options={
                'db_table': 'trade',
            },
        ),
    ]