from django.db import models


class Office(models.Model):
    title = models.charField(max_length=30)
    term = models.IntegerField(max_length=2)
    AOG = (
        ('F', 'Federal'),
        ('S', 'State'),
        ('L', 'Local'),
    )
    area_of_governance = models.CharField(max_length=1, choices=AOG)
    federal_district = models.IntegerField(max_length=2)
    state_district = models.IntegerField(max_length=3)


class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    SSN = models.IntegerField(min_length=9)
    federal_district = models.IntegerField(max_length=2)
    state_district = models.IntegerField(max_length=3)


class Voter(models.Model):
    person = models.OneToOneField(Person)
    ballots = models.ManyToManyField(Ballots)


class Politician(models.Model):
    person = models.OneToOneField(Person)
    candidacies = models.ManyToManyField(Candidacy)


class Candidacy(mdoels.Model):
    politician = models.OneToOneField(Politician)
    PARTY = (
        ('D', 'Democrat'),
        ('R', 'Republican'),
        ('I', 'Independent'),
    )
    party_affiliation = models.CharField(max_length=1, choices=PARTY)
    office = models.OneToOneField(Office)

