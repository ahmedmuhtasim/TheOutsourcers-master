from django.db import models


class Office(models.Model):
    title = models.CharField(max_length=30)
    term = models.IntegerField()
    AOG = (
        ('F', 'Federal'),
        ('S', 'State'),
        ('L', 'Local'),
    )
    area_of_governance = models.CharField(max_length=1, choices=AOG)
    federal_district = models.IntegerField()
    state_district = models.IntegerField()


class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    SSN = models.CharField(max_length=9)
    federal_district = models.IntegerField()
    state_district = models.IntegerField()


class Voter(models.Model):
    # on_delete tells what to do if person is deleted - in that case, do SQL CASCADE
    # This guarantees that a Voter will have a person, it won't become null
    # Default null value for django one to one field is false, so person will never be false
    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    voter_number = models.IntegerField()
    STATUS_TYPES = (
        ('A', 'Active'),
        ('I', 'Inactive')
    )
    voter_status = models.CharField(max_length=1,
    choices = STATUS_TYPES)
    date_registered = models.CharField(max_length=10)
    street_address = models.CharField(max_length=40)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=2)
    zip = models.IntegerField(max_length=5)
    locality = models.CharField(max_length=40)

    voting_eligible = models.BooleanField(default=True)


class Politician(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE)


class Measure(models.Model):
    MEASURE_TYPES = (
            ('R', 'Referendum'),
            ('C', 'Candidacy')
    )
    measure_type = models.CharField(max_length=1, choices=MEASURE_TYPES)


class Candidacy(models.Model):
    measure = models.OneToOneField(Measure, on_delete=models.CASCADE)
    politician = models.OneToOneField(Politician, on_delete=models.CASCADE)
    PARTY = (
        ('D', 'Democrat'),
        ('R', 'Republican'),
        ('I', 'Independent'),
    )
    party_affiliation = models.CharField(max_length=3, choices=PARTY)
    office = models.OneToOneField(Office, on_delete=models.CASCADE)
    # Votes are tallied in this model for ease of tallying and lack of tracking
    votes = models.IntegerField(default=0)


class Referendum(models.Model):
    measure = models.OneToOneField(Measure, on_delete=models.CASCADE)
    question = models.TextField(blank=True)
    # Choices are linked in the Choice model


class Choice(models.Model):
    question = models.ForeignKey(Referendum, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    # Votes are tallied in this model for ease of tallying and lack of tracking
    votes = models.IntegerField(default=0)


class Ballot(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    # Votes are NOT stored in ballot - thinking they are read then a choice is updated
    # This avoids being able to trace the ballot - the ballot simply puts many candidacies
    # and referendums in a single place and assigns a voter to this ballet
    # It might also work with many to many, many voters per ballot and many ballots per voter

class Precinct(models.Model):
    name = models.CharField()
    id = models.IntegerField(max_length=4)


class Poll_Worker(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    precinct = models.OneToOneField(Precinct, on_delete=models.CASCADE)

class Election(models.Model):
    id = models.CharField(max_length=7)
    ELECTION_TYPES = (
            ('G', 'General'),
            ('P', 'Primary')
    )
    type = models.CharField(max_length=1, choices=ELECTION_TYPES)
ballot = models.OneToOneField(Ballot, on_delete=models.CASCADE)