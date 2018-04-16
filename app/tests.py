from django.test import TestCase
from django.models import *
from .forms import SignupForm
from .forms import LoginForm

class GeneralTests(TestCase):
	def language_is_english(self):
		self.client.cookies.load({settings.LANGUAGE_COOKIE_NAME: 'en'})
		response = self.client.get('/')
		self.assertEqual(response.content, b"Hello, welcome to Housing.")
		
class FixtureTests(TestCase):
	fixtures = ['sulavfixture.json']
	
	def test_log_in_preexisting_user(self):
		user = authenticate(username="NaughtyDog", password="iamlegend")
		self.assertTrue(user.is_active)
		
	def test_log_in_preexisting_user_wrong_password(self):
		user = authenticate(username="NaughtyDog", password="wrongpassword")
		self.assertFalse(user)

	def test_nonexisting_user(self):
		user = authenticate(username="notauser", password="wrongpassword")
		self.assertFalse(user)

	def test_signup_creates_db_entry(self):
		form = SignupForm({
			'first_name': "Firstname",
			'last_name': "Lastname",
			'email': "myemail@email.com",
			'username': "testuser",
		    'password1': "testPass",
		    'password2': "testPass",
		})

		form.save(commit=False);
		user = authenticate(username="root", password="outsourcers")
		self.assertTrue(user.is_active)

	def test_signup_preexisting_user(self):
		form = SignupForm({
			'first_name': "Firstname",
			'last_name': "Lastname",
			'email': "myemail@email.com",
			'username': "newuser",
		    'password1': "outsourcers",
		    'password2': "outsourcers",
		})
		self.assertFalse(form.is_valid())

class LoggingTests(TestCase):

	def test_not_authenticated_not_loggedin(self):
		user = auth.get_user(self.client)
		assert not user.is_authenticated()

	def test_log_in(self):
		form = LoginForm({
			'username': "newuser",
			'password': "newpassword",
		})
		self.assertTrue(form.is_valid())
		
	def test_log_in_without_username(self):
		form = LoginForm({
			'username': "",
			'password': "newpassword",
		})
		self.assertFalse(form.is_valid())

	def test_log_in_without_password(self):
		form = LoginForm({
			'username': "newpassword",
			'password': "",
		})
		self.assertFalse(form.is_valid())

class ViewTests(TestCase):

    def test_index_view(self):
        response = self.client.get(reverse('mapapp:ballot'))
        self.assertEqual(response.status_code, 200)

    def test_login_view(self):
        response = self.client.get(reverse('mapapp:election_result'))
        self.assertEqual(response.status_code, 200)

    def test_signup_view(self):
        response = self.client.get(reverse('mapapp:elections'))
        self.assertEqual(response.status_code, 200)

    def test_usermap_view(self):
        response = self.client.get(reverse('mapapp:home'))
        self.assertEqual(response.status_code, 200)

    def test_about_view(self):
        response = self.client.get(reverse('mapapp:login'))
        self.assertEqual(response.status_code, 200)

    def test_userprofile_not_authenticated_view(self):
        response = self.client.get(reverse('mapapp:results'))
        self.assertEqual(response.status_code, 302)

    def test_home_view(self):
        response = self.client.get(reverse('mapapp:signup'))
        self.assertEqual(response.status_code, 200)

    def test_basicmap_view(self):
        response = self.client.get(reverse('mapapp:vote'))
        self.assertEqual(response.status_code, 200)