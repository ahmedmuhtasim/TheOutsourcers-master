from django.test import TestCase


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
			'email': "myemail@test.com",
			'username': "user1234",
		    'password1': "testPass9",
		    'password2': "testPass9",
		})

		form.save(commit=False);
		user = authenticate(username="user1234", password="testPass9")
		self.assertTrue(user.is_active)

	def test_signup_preexisting_user(self):
		form = SignupForm({
			'first_name': "Firstname",
			'last_name': "Lastname",
			'email': "myemail@test.com",
			'username': "willsmith",
		    'password1': "testPass9",
		    'password2': "testPass9",
		})
		self.assertFalse(form.is_valid())

class LoggingTests(TestCase):

	def test_not_authenticated_not_loggedin(self):
		user = auth.get_user(self.client)
		assert not user.is_authenticated()

	def test_log_in(self):
		form = LoginForm({
			'username': "username123",
			'password': "testPass123",
		})
		self.assertTrue(form.is_valid())
		
	def test_log_in_without_username(self):
		form = LoginForm({
			'username': "",
			'password': "testPass123",
		})
		self.assertFalse(form.is_valid())

	def test_log_in_without_password(self):
		form = LoginForm({
			'username': "username123",
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

