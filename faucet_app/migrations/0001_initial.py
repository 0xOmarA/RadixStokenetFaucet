# Generated by Django 4.0.1 on 2022-01-14 20:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FaucetRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Requested At')),
                ('wallet_address', models.CharField(max_length=128, verbose_name='Wallet Address')),
                ('xrd_amount_requested', models.FloatField(verbose_name='XRD Amount Requested')),
                ('cooldown_period_in_hours', models.FloatField(verbose_name='Cooldown Period in Hours')),
                ('tweet_id', models.IntegerField(verbose_name='Tweet ID')),
                ('tweet_link', models.TextField(verbose_name='Tweet Link')),
                ('twitter_author_id', models.IntegerField(verbose_name='ID of Twitter Author')),
            ],
        ),
    ]
