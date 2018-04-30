from django import forms
from app.models import Precinct, Election
from .choices import ROLE_CHOICES, PRECINCT_CHOICES

class SignupForm(forms.Form):
	username = forms.CharField(label='username', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Username'}))

	first_name = forms.CharField(label='first name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
	last_name = forms.CharField(label='last name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
	password = forms.CharField(label='password', max_length=100, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
	confirm_password = forms.CharField(label='confirm password', max_length=100, widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))
	ssn = forms.CharField(label='ssn', max_length=100, widget=forms.PasswordInput(attrs={'placeholder': 'Social Security Number'}))
	dob = forms.DateField(label='dob',  widget=forms.TextInput(attrs={'type':'date', 'placeholder': 'Date of Birth'}))
	role = forms.ChoiceField(label='role', choices=ROLE_CHOICES)
	precinct_id = forms.ChoiceField(label='precinct', choices=PRECINCT_CHOICES)

class LoginForm(forms.Form):
	username = forms.CharField(label='username', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
	password = forms.CharField(label='password', max_length=100, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

class VoteValidationForm(forms.Form):
	serial_code = forms.CharField(label='username', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Serial Code'}))


class BallotForm(forms.Form):
	CHOICES = [
		('select1','select 1'),
      ('select2','select 2')
	]
	like = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())

class PollworkerForm(forms.Form):
	#precinct_ID = forms.CharField(label='precinct ID', max_length=10, widget=forms.TextInput(attrs={'placeholder': 'Precinct ID'}))
	#election_ID = forms.CharField(label='election ID', max_length=7, widget=forms.TextInput(attrs={'placeholder': 'Election ID'}))
	precinct = forms.ModelChoiceField(queryset = Precinct.objects.all())
	election = forms.ModelChoiceField(queryset = Election.objects.all())
