# Generated by Django 5.0 on 2024-03-13 12:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("clinic", "0002_rename_lunch_time_businesshours_lunch_end_time_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="BusinessHours",
            new_name="BusinessHour",
        ),
    ]