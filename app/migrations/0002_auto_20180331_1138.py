# Generated by Django 2.0.3 on 2018-03-31 11:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ballot',
            name='voter',
        ),
        migrations.RemoveField(
            model_name='voter',
            name='zip',
        ),
        migrations.AddField(
            model_name='measure',
            name='ballot',
            field=models.ManyToManyField(to='app.Ballot'),
        ),
        migrations.AddField(
            model_name='voter',
            name='precinct',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Precinct'),
        ),
        migrations.AddField(
            model_name='voter',
            name='zip_code',
            field=models.CharField(max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='precinct',
            name='id',
            field=models.CharField(max_length=4, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='voter',
            name='voting_eligible',
            field=models.BooleanField(default=False),
        ),
    ]
