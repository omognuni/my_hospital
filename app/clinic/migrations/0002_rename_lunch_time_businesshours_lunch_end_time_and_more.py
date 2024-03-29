# Generated by Django 5.0 on 2024-03-10 03:39

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clinic", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="businesshours",
            old_name="lunch_time",
            new_name="lunch_end_time",
        ),
        migrations.AddField(
            model_name="businesshours",
            name="lunch_start_time",
            field=models.TimeField(null=True),
        ),
        migrations.AddField(
            model_name="treatmentrequest",
            name="created_datetime",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="businesshours",
            name="day",
            field=models.IntegerField(
                choices=[
                    (0, "monday"),
                    (1, "tuesday"),
                    (2, "wednesday"),
                    (3, "thursday"),
                    (4, "friday"),
                    (5, "saturday"),
                    (6, "sunday"),
                ]
            ),
        ),
        migrations.AlterUniqueTogether(
            name="businesshours",
            unique_together={("doctor", "day")},
        ),
    ]
