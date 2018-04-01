from django import forms

class SignupForm(forms.Form):
	username = forms.CharField(label='username', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
	first_name = forms.CharField(label='first name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
	last_name = forms.CharField(label='last name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
	email = forms.EmailField(label='email', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Email'}))
	password = forms.CharField(label='password', max_length=100, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
	confirm_password = forms.CharField(label='confirm password', max_length=100, widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

class LoginForm(forms.Form):
	username = forms.CharField(label='username', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
	password = forms.CharField(label='password', max_length=100, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

class VoteValidationForm(forms.Form):
	serial_code = forms.CharField(label='username', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Serial Code'}))


class BallotForm(forms.Form):
	CHOICES=[('select1','select 1'),
         ('select2','select 2')]

	like = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())