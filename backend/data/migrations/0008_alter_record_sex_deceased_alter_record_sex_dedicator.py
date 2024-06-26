from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0007_alter_record_sex_deceased_alter_record_sex_dedicator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='sex_deceased',
            field=models.CharField(blank=True, choices=[('', '-'), ('female', 'Female'), ('male', 'Male'), ('female-child', 'Female (child)'), ('male-child', 'Male (child)'), ('child', 'Child')], default='', max_length=255, verbose_name='sex deceased'),
        ),
        migrations.AlterField(
            model_name='record',
            name='sex_dedicator',
            field=models.CharField(blank=True, choices=[('', '-'), ('female', 'Female'), ('male', 'Male'), ('female-child', 'Female (child)'), ('male-child', 'Male (child)'), ('child', 'Child')], default='', max_length=255, verbose_name='sex dedicator'),
        ),
    ]
