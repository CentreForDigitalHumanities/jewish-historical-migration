# Generated by Django 4.2.2 on 2023-10-24 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_adjust_record_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='centuries',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Estimated century/ies'),
        ),
        migrations.AlterField(
            model_name='record',
            name='inscription_type',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='record',
            name='language',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AlterField(
            model_name='record',
            name='mentioned_placenames',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='record',
            name='period',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Historical period'),
        ),
        migrations.AlterField(
            model_name='record',
            name='religious_profession',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='record',
            name='script',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='record',
            name='sex_deceased',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='record',
            name='sex_dedicator',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='record',
            name='site_type',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='record',
            name='symbol',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Religious symbol'),
        ),
    ]
