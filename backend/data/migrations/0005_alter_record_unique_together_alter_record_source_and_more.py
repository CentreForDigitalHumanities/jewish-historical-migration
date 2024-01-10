# Generated by Django 4.2.2 on 2023-12-12 09:30

from django.db import migrations, models


def make_source_unique(apps, schema_editor):
    Record = apps.get_model("data", "Record")
    previous_source = None
    for record in Record.objects.order_by("source"):
        source = record.source
        previous_source = record.source
        if source == previous_source:
            record.source = record.source + "_" + str(record.pk)
            record.save()


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0004_century_language_primarycategory_script_and_more'),
    ]

    operations = [
        migrations.RunPython(make_source_unique),
        migrations.AlterUniqueTogether(
            name='record',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='record',
            name='source',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.RemoveField(
            model_name='record',
            name='identifier',
        ),
    ]
