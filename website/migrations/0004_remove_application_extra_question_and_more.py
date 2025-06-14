# Generated by Django 5.2.3 on 2025-06-12 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_application_extra_question_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='application',
            name='extra_question',
        ),
        migrations.RemoveField(
            model_name='application',
            name='extra_question_title',
        ),
        migrations.RemoveField(
            model_name='application',
            name='resume',
        ),
        migrations.AddField(
            model_name='application',
            name='answers',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='application',
            name='cover_letter',
            field=models.TextField(blank=True, verbose_name='Xat'),
        ),
        migrations.AlterField(
            model_name='application',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Ism'),
        ),
        migrations.AlterField(
            model_name='application',
            name='phone',
            field=models.CharField(max_length=20, verbose_name='Telefon'),
        ),
    ]
