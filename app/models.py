from django.db import models
from .choices import ROLE_CHOICES

class User(models.Model):
	username = models.CharField(max_length=250)
	first_name = models.CharField(max_length=250)
	last_name = models.CharField(max_length=250)
	password = models.CharField(max_length=250) # hash stored
	ssn = models.CharField(max_length=250) # hash stored
	dob = models.DateTimeField()
	join_date = models.DateTimeField(auto_now=True)
	
	role = models.CharField(
		max_length=2,
		choices = ROLE_CHOICES
	)

	def __str__(self):
		return self.username

class Authenticator(models.Model):
	user_id = models.CharField(max_length=250)
	token = models.CharField(max_length=250, primary_key=True)
	date_created = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.token

class Election(models.Model):
	id = models.CharField(max_length=7, primary_key=True)
	ELECTION_TYPES = (
				('G', 'general'),
				('P', 'primary')
	)
	type = models.CharField(max_length=1, choices=ELECTION_TYPES)

	def __str__(self):
		return self.id

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
	def __str__(self):
		return str(self.title)

class Person(models.Model):
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)
	SSN = models.CharField(max_length=9)
	federal_district = models.IntegerField()
	state_district = models.IntegerField()

	def __str__(self):
		return self.first_name + " " + self.last_name
		
class Politician(models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='politicians')
	
	def __str__(self):
		return self.person.__str__()
		
class Ballot(models.Model):
	election = models.OneToOneField(Election, on_delete=models.CASCADE, primary_key=True)
	def __str__(self):
		return str(self.pk)

	# Votes are NOT stored in ballot - thinking they are read then a choice is updated
	# This avoids being able to trace the ballot - the ballot simply puts many candidacies
	# and referendums in a single place and assigns a voter to this ballet
	# It might also work with many to many, many voters per ballot and many ballots per voter

class Measure(models.Model):
	MEASURE_TYPES = (
				('R', 'Referendum'),
				('C', 'Candidacy')
	)
	measure_type = models.CharField(max_length=1, choices=MEASURE_TYPES)
	ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE, related_name='measures')
	def __str__(self):
		#if self.measure_type == "C":
		#    return "Candidates"
		#else:
		#    return "Referendums"
                try:
                    return self.candidacies.filter()[:1].get().office.title if self.measure_type == 'C' else self.referendums.filter()[:1].get().question
                except:
                    return "Nothing!"
				
class Candidacy(models.Model):
	measure = models.ForeignKey(Measure, on_delete=models.CASCADE, related_name='candidacies')
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
	measure = models.ForeignKey(Measure, on_delete=models.CASCADE, related_name='referendums')
	question = models.TextField(blank=True)
	# Choices are linked in the Choice model
	def __str__(self):
		return str(self.question)

class Choice(models.Model):
	question = models.ForeignKey(Referendum, on_delete=models.CASCADE, related_name='choices')
	choice_text = models.CharField(max_length=200)
	# Votes are tallied in this model for ease of tallying and lack of tracking
	votes = models.IntegerField(default=0)
	def __str__(self):
		return str(self.choice_text)

class Precinct(models.Model):
	name = models.CharField(max_length=250)
	id = models.CharField(max_length=4, primary_key=True)

class Poll_Worker(models.Model):
	person = models.OneToOneField(Person, on_delete=models.CASCADE)
	precinct = models.OneToOneField(Precinct, on_delete=models.CASCADE)

class Voter(models.Model):
	# on_delete tells what to do if person is deleted - in that case, do SQL CASCADE
	# This guarantees that a Voter will have a person, it won't become null
	# Default null value for django one to one field is false, so person will never be false
	person = models.OneToOneField(Person, on_delete=models.CASCADE)
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
	zip_code = models.CharField(max_length=5, null=True)
	locality = models.CharField(max_length=40)
	precinct = models.ForeignKey(Precinct, on_delete=models.SET_NULL, null=True)
	# Can they vote? The voter must check in - once they check in, voting_eligible will become True
	# When they cannot vote - so they have not checked in/election over, should be False
	# voting_eligible should be made false with a ballot submission
	voter_number = models.CharField(max_length=12, null=True)
	election = models.OneToOneField(Election, on_delete=models.SET_NULL, null=True, blank=True)
	def __str__(self):
		return self.person.__str__()
