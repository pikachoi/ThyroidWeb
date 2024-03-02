# Generated by Django 4.2.1 on 2024-02-23 11:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Question",
            fields=[
                ("idx", models.AutoField(primary_key=True, serialize=False)),
                ("question", models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name="Doctor",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "username",
                    models.CharField(max_length=128, primary_key=True, serialize=False),
                ),
                (
                    "last_login",
                    models.DateTimeField(auto_now=True, verbose_name="last login"),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_superuser", models.BooleanField(default=False)),
            ],
            options={
                "abstract": False,
            },
            managers=[
                ("object", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="Doctor_profile",
            fields=[
                (
                    "doctor_username",
                    models.OneToOneField(
                        db_column="doctor_username",
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("license", models.CharField(max_length=128, unique=True)),
                ("real_name", models.CharField(default="홍길동", max_length=32)),
                ("email", models.EmailField(max_length=128)),
                ("phone", models.CharField(default="010-0000-0000", max_length=13)),
                ("belong", models.CharField(max_length=128)),
                ("position", models.CharField(max_length=128)),
                ("medical_subject", models.CharField(max_length=128)),
                ("question_answer", models.CharField(max_length=128)),
                (
                    "question",
                    models.ForeignKey(
                        db_column="question",
                        default=1,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Accounts.question",
                    ),
                ),
            ],
        ),
    ]
