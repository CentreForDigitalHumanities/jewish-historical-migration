# Generated by Django 4.2.2 on 2023-12-19 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0005_alter_record_unique_together_alter_record_source_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='century',
            options={'ordering': ['century_number'], 'verbose_name_plural': 'centuries'},
        ),
        migrations.AlterModelOptions(
            name='language',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='place',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='primarycategory',
            options={'ordering': ['name'], 'verbose_name_plural': 'primary categories'},
        ),
        migrations.AlterModelOptions(
            name='script',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='secondarycategory',
            options={'ordering': ['name'], 'verbose_name_plural': 'secondary categories'},
        ),
        migrations.AddField(
            model_name='century',
            name='century_number',
            field=models.IntegerField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='record',
            name='area',
            field=models.CharField(editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='record',
            name='region',
            field=models.CharField(editable=False, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='category1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='data.primarycategory', verbose_name='primary category'),
        ),
        migrations.AlterField(
            model_name='record',
            name='category2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='data.secondarycategory', verbose_name='secondary category'),
        ),
        migrations.AlterField(
            model_name='record',
            name='estimated_centuries',
            field=models.ManyToManyField(to='data.century', verbose_name='estimated centuries'),
        ),
        migrations.AlterField(
            model_name='record',
            name='period',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='historical period'),
        ),
        migrations.AlterField(
            model_name='record',
            name='place',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='records', to='data.place'),
        ),
        migrations.AlterField(
            model_name='record',
            name='symbol',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='religious symbol'),
        ),
    ]
