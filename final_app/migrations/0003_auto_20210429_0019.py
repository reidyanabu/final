# Generated by Django 2.2.4 on 2021-04-29 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('final_app', '0002_video_videorating'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='city',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='state',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='zip',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
