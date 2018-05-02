# Generated by Django 2.0.4 on 2018-05-01 17:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Authenticator',
            fields=[
                ('user_id', models.CharField(max_length=250)),
                ('token', models.CharField(max_length=250, primary_key=True, serialize=False)),
                ('date_created', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Candidacy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('party_affiliation', models.CharField(choices=[('D', 'Democrat'), ('R', 'Republican'), ('I', 'Independent')], max_length=3)),
                ('votes', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice_text', models.CharField(max_length=200)),
                ('votes', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Election',
            fields=[
                ('id', models.CharField(max_length=7, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('G', 'general'), ('P', 'primary')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Measure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('measure_type', models.CharField(choices=[('R', 'Referendum'), ('C', 'Candidacy')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Office',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
                ('term', models.IntegerField()),
                ('area_of_governance', models.CharField(choices=[('F', 'Federal'), ('S', 'State'), ('L', 'Local')], max_length=1)),
                ('federal_district', models.IntegerField()),
                ('state_district', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('SSN', models.CharField(max_length=250)),
                ('federal_district', models.IntegerField(null=True)),
                ('state_district', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Politician',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='politicians', to='app.Person')),
            ],
        ),
        migrations.CreateModel(
            name='Poll_Worker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.Person')),
            ],
        ),
        migrations.CreateModel(
            name='Precinct',
            fields=[
                ('name', models.CharField(max_length=250)),
                ('id', models.CharField(max_length=10, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Referendum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField(blank=True)),
                ('measure', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referendums', to='app.Measure')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=250)),
                ('first_name', models.CharField(max_length=250)),
                ('last_name', models.CharField(max_length=250)),
                ('password', models.CharField(max_length=250)),
                ('ssn', models.CharField(max_length=250)),
                ('dob', models.DateTimeField()),
                ('join_date', models.DateTimeField(auto_now=True)),
                ('role', models.CharField(choices=[('PW', 'Poll Worker'), ('SA', 'System Admin')], max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Voter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voter_status', models.CharField(max_length=100)),
                ('date_registered', models.CharField(max_length=10)),
                ('street_address', models.CharField(max_length=40)),
                ('city', models.CharField(max_length=30)),
                ('state', models.CharField(max_length=2)),
                ('zip_code', models.CharField(max_length=5, null=True)),
                ('locality', models.CharField(max_length=40)),
                ('voter_number', models.CharField(max_length=12, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VoterSerialCodes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_code', models.CharField(max_length=250)),
                ('finished', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Ballot',
            fields=[
                ('election', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='app.Election')),
            ],
        ),
        migrations.AddField(
            model_name='voterserialcodes',
            name='election',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Election'),
        ),
        migrations.AddField(
            model_name='voterserialcodes',
            name='voter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Voter'),
        ),
        migrations.AddField(
            model_name='voter',
            name='election',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Election'),
        ),
        migrations.AddField(
            model_name='voter',
            name='person',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.Person'),
        ),
        migrations.AddField(
            model_name='voter',
            name='precinct',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Precinct'),
        ),
        migrations.AddField(
            model_name='poll_worker',
            name='precinct',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.Precinct'),
        ),
        migrations.AddField(
            model_name='choice',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='app.Referendum'),
        ),
        migrations.AddField(
            model_name='candidacy',
            name='measure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='candidacies', to='app.Measure'),
        ),
        migrations.AddField(
            model_name='candidacy',
            name='office',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Office'),
        ),
        migrations.AddField(
            model_name='candidacy',
            name='politician',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Politician'),
        ),
        migrations.AddField(
            model_name='candidacy',
            name='running_mate',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='running_mate', to='app.Politician'),
        ),
        migrations.AddField(
            model_name='measure',
            name='ballot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='measures', to='app.Ballot'),
        ),
    ]
