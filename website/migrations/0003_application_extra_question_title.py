# Generated by Django 5.2.3 on 2025-06-12 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_application_extra_question'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='extra_question_title',
            field=models.CharField(blank=True, max_length=255, verbose_name='Extra Question Title'),
        ),
    ]
