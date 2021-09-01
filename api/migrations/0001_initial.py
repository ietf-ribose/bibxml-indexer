# Generated by Django 3.2.7

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BibData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bib_id', models.CharField(max_length=64)),
                ('bib_type', models.CharField(max_length=16)),
                ('body', models.JSONField(verbose_name='body')),
            ],
            options={
                'db_table': 'api_bib_data',
            },
        ),
        migrations.AddConstraint(
            model_name='bibdata',
            constraint=models.UniqueConstraint(fields=('bib_id', 'bib_type'), name='unique_bib_id'),
        ),
    ]
