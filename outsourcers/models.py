from django.db import models


class Office(models.Model):
    title = models.CharField(max_length=30)
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
    SSN = models.IntegerField(max_length=9)
    federal_district = models.IntegerField(max_length=2)
    state_district = models.IntegerField(max_length=3)


class Voter(models.Model):
    # on_delete tells what to do if person is deleted - in that case, do SQL CASCADE
    # This guarantees that a Voter will have a person, it won't become null
    # Default null value for django one to one field is false, so person will never be false
    person = models.OneToOneField(Person, on_delete=models.CASCADE) 
    #ballots = models.ManyToManyField(Ballots)


class Candidacy(models.Model):
    politician = models.OneToOneField(Politician)
    PARTY = (
        ('D', 'Democrat'),
        ('R', 'Republican'),
        ('I', 'Independent'),
    )
    party_affiliation = models.CharField(max_length=3, choices=PARTY)
    office = models.OneToOneField(Office)


class Politician(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    candidacies = models.ManyToManyField(Candidacy)
