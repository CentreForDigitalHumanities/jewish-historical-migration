# Generated by Django 4.2.11 on 2024-05-08 11:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0008_alter_record_sex_deceased_alter_record_sex_dedicator'),
    ]

    operations = [
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='record',
            name='location_in_publication',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='record',
            name='publication',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='data.publication'),
        ),
    ]
