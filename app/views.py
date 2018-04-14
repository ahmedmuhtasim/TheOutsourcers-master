from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from .models import *
from .forms import LoginForm, SignupForm, VoteValidationForm, BallotForm
from datetime import date
from django.views.decorators.csrf import csrf_exempt
from .utility_methods import validate_serial_code, gen_alphanumeric, is_logged_on
from rest_framework.generics import *
from .serializers import *
import json
from django.urls import reverse
import urllib
import hmac
from django.contrib.auth.hashers import make_password, check_password

# Pages
def home(request):
	""" GET DATA FROM API & FORMAT
	req = urllib.request.Request("http://exp-api:8000/exp/home")
	resp_json = urllib.request.urlopen(req).read().decode("utf-8")
	response = json.loads(resp_json)
	"""

	logged_on = is_logged_on(request)
	
	return render(request, "app/home.html", {
		"logged_on": logged_on
	})

def results(request):
	logged_on = is_logged_on(request)
	
	if request.method == "GET":
		election_data = {}
		election_data = {
			"open": [
				{
					"name": "Equifax new President",
					"id": "equifax-2018",
					"total_votes": 651,
					"type": "general",
					"state": "open"
				}
			],
			"closed": [
				{
					"name": "Presidential Race 2012",
					"id": "pres-2012",
					"total_votes": 22347000,
					"type": "general",
					"state": "closed",
					"winner": {
						"name": "Barack Obama",
						"id": "bho"
					}
				}
			],
		}
		return render(request, "app/results.html", {
			"election_data": "election_data",
			"logged_on": logged_on
		})

def election_result(request, pk):
	logged_on = is_logged_on(request)
	
	if request.method == "GET":
		elections = {
			"pres-2012": {
				"name": "Presidential Race 2012",
				"id": "pres-2012",
				"total_votes": 22347000,
				"type": "general",
				"state": "closed"
			}
		}
		return render(request, "app/election_result.html", {
			"election": elections[pk],
			"pk": pk,
			"logged_on": logged_on
		})

def page_elections(request):
	logged_on = is_logged_on(request)
	
	if request.method == "GET":
		election_data = {}
		req = urllib.request.Request("http://localhost:8000/api/elections/")
		resp_json = urllib.request.urlopen(req).read().decode("utf-8")
		election_data["body"] = json.loads(resp_json)
		election_data = {
			"open": [
				{
					"name": "Equifax new President",
					"id": "equifax-2018",
					"total_votes": 651,
					"type": "general",
					"state": "open"
				}
			],
			"closed": [
				{
					"name": "Presidential Race 2012",
					"id": "pres-2012",
					"total_votes": 22347000,
					"type": "general",
					"state": "closed"
				}
			],
			"future": [
				{
					"name": "Midterm 2018",
					"id": "midterm-2018",
					"total_votes": 0,
					"type": "general",
					"state": "not-yet-open"
				},
			]
		}

		return render(request, "app/elections.html", {
			"election_data": election_data,
			"logged_on": logged_on
		})

# Signup/Login Flow
@csrf_exempt
def login(request):
	logged_on = is_logged_on(request)
	
	# If the authenticator cookie wasn't set...
	if logged_on:
		# Handle user not logged in while trying to create a listing
		return HttpResponseRedirect(reverse('home'))

	form = LoginForm
	if request.method == "GET":
		return render(request, "app/login.html", {
			"form": form,
		})

	elif request.method == "POST":
		f = LoginForm(request.POST)

		# Check if the form instance is invalid
		if not f.is_valid():
			# Form was bad -- send them back to login page and show them an error
			return render(request, 'app/login.html', {
				"form": form,
				"logged_on": logged_on,
				"errorMessage": "Form input invalid",
			})

		# Sanitize username and password fields
		username = f.cleaned_data['username']
		password = f.cleaned_data['password']

		user_results = User.objects.filter(username=username)

		if len(user_results) != 1:
			return render(request, 'app/login.html', {
				"form": form,
				"logged_on": logged_on,
				"errorMessage": "Username or Password Incorrect"
			})

		user = user_results[0]

		# check password
		if check_password(password, user.password):
			return render(request, 'app/login.html', {
				"form": form,
				"logged_on": logged_on,
				"errorMessage": "Username or Password Incorrect"
			})

		""" If we made it here, we can log them in. """
		# Set their login cookie and redirect to back to wherever they came from
		authenticator = gen_alphanumeric(30)
		
		auth = Authenticator(
			token=authenticator,
			user_id=user.pk
		)
		auth.save()
		
		message = "okie dokie"
		response = HttpResponseRedirect(reverse('home'))
		response.set_cookie("auth", authenticator)
		response.set_cookie("responseMessage", message)

		return response
		
@csrf_exempt
def signup(request):
	logged_on = is_logged_on(request)
	# If the authenticator cookie wasn't set...
	if logged_on:
		# Handle user not logged in while trying to create a listing
		return HttpResponseRedirect(reverse('home'))

	form = SignupForm

	if request.method == "GET":
		
		return render(request, "app/signup.html", {
			"form": form,
			"logged_on": logged_on
		})
	elif request.method == "POST":
		f = SignupForm(request.POST)

		# Check if the form instance is invalid
		if not f.is_valid():
			# Form was bad -- send them back to login page and show them an error
			return render(request, 'app/signup.html', {
				"form": form,
				"logged_on": logged_on,
				"errorMessage": "Form input invalid",
			})

		# Sanitize username and password fields
		username = f.cleaned_data['username']
		first_name = f.cleaned_data['first_name']
		last_name = f.cleaned_data['last_name']
		password = f.cleaned_data['password']
		confirm_password = f.cleaned_data['confirm_password']
		ssn = f.cleaned_data['ssn']
		role = f.cleaned_data['role']
		dob = f.cleaned_data['dob']
		
		user_results = User.objects.filter(username=username)

		if len(user_results) > 0:
			return render(request, 'app/signup.html', {
				"form": form,
				"logged_on": logged_on,
				"errorMessage": "Username Already Taken"
			})

		# check password
		if confirm_password != password:
			return render(request, 'app/signup.html', {
				"form": form,
				"logged_on": logged_on,
				"errorMessage": "Passwords Don't Match"
			})

		""" If we made it here, we can log them in. """
		# Set their login cookie and redirect to back to wherever they came from
		
		user = User(
			username = username,
			first_name = first_name,
			last_name = last_name,
			password = make_password(password),
			ssn = make_password(ssn),
			dob = dob,
			role = role
		)

		user.save()
		
		authenticator = gen_alphanumeric(30)
		
		auth = Authenticator(
			token=authenticator,
			user_id=user.pk
		)
		auth.save()
		
		message = "okie dokie"
		response = HttpResponseRedirect(reverse('signup_confirmation'))
		response.set_cookie("auth", authenticator)
		response.set_cookie("responseMessage", message)

		return response

def signup_confirmation(request):
	logged_on = is_logged_on(request)
	
	return render(request, "app/signup_confirmation.html", {
		"logged_on": logged_on
	})

def signout(request):
	logged_on = is_logged_on(request)
	# If we received a GET request instead of a POST request
	response = HttpResponseRedirect(reverse('home'))
	response.delete_cookie('auth')

	return response

# Vote/Ballot Flow
@csrf_exempt
def vote(request):
	logged_on = is_logged_on(request)
	
	form = VoteValidationForm
	if request.method == "GET":
		is_day_of = False
		day_of = date(2018, 4, 14)
		today = date.today()
		is_day_of = today == day_of
		return render(request, "app/vote.html", {
			"form": form,
			"is_day_of": is_day_of
		})
	elif request.method == "POST":
		form = VoteValidationForm(request.POST)
		if form.is_valid():
			voter = validate_serial_code(form.cleaned_data["serial_code"])
			election = voter.election
			ballot = election.ballot
			if election:
					election_data = [
			{
			"name": "Presidential Contest",
			"type": "main",
			"id": "pres-2012",
			"candidates": [
				{
					"id": 0,
					"candidate": "Barack Obama",
					"running_mate": "Joe Biden",
					"party": "Democrat"
				},
				{
					"id": 1,
					"candidate": "Mitt Romney",
					"running_mate": "Paul Ryan",
					"party": "Republican"
				},
				{
					"id": 2,
					"candidate": "Gary Johnson",
					"running_mate": "James P. Gray",
					"party": "Libertarian"
				},
			]
		},
		{
			"name": "House of Reps. District 5",
			"type": "",
			"id": "dist-5",
			"candidates": [
				{
					"id": 0,
					"candidate": "Elisabeth Motsinger",
					"party": "Democrat"
				},
				{
					"id": 1,
					"candidate": "Virginia Foxx",
					"party": "Republican"
				},
			]
		}
	]
					person = {
		"name": "Luke Masters",
		"id": "awh4Rtxu12"
	}
					return render(request, "app/ballot.html", {
		"form": BallotForm,
		"election_data": ballot,
		"person": person,
		"logged_on": logged_on
	})

	return JsonResponse({
		"message": "Invalid Request"
	})

@csrf_exempt
def submit_vote(request):
	data = request.POST
	for key in data.keys():
		measure = Measure.objects.get(pk=key)
		if measure.measure_type == 'C':
			candidacy = Candidacy.objects.get(pk=data[key])
			candidacy.votes += 1
			candidacy.save()
		else:
			choice = Choice.objects.get(pk=data[key])
			choice.votes += 1
			choice.save()

	return HttpResponse("Vote Submitted!")

def results(request):
	logged_on = is_logged_on(request)
	
	if request.method == "GET":
		return render(request, "app/results.html", {
			"logged_on": logged_on
		})

def signout(request):
	logged_on = is_logged_on(request)
	# If we received a GET request instead of a POST request
	response = HttpResponseRedirect(reverse('home'))
	response.delete_cookie('auth')

	return response

class VoterViewSet(viewsets.ModelViewSet):
	renderer_classes = (JSONRenderer, )
	queryset = Voter.objects.all()
	serializer_class = VoterSerializer
	model = Voter

	def delete(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to delete an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
				result.delete()
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)
			except IntegrityError:
				return Response({"status": "400 - Bad Request", "result": str(self.model) + " is a foreign key to other models and thus cannot be deleted"}, status=status.HTTP_409_CONFLICT)
			return Response({"status": "204 - No Content", "response": "Successfully deleted " + str(self.model)})

	def get(self, request, format=None, pk=None):
		is_many = True
		if pk is None:
			result = self.model.objects.all()
		else:
			try:
				result = self.model.objects.get(pk=pk)
				is_many = False
			except self.model.DoesNotExist:
				return Response({"status": "404", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

		serializer = self.serializer_class(result, many=is_many)
		return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)

	def post(self, request, format=None, pk=None):
		if pk is None:
			serializer = self.serializer_class(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "201 - Created", "result": serializer.data}, status=status.HTTP_201_CREATED)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({"status": "400 - Bad Request", "result": "Cannot POST data to an already created id"}, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to update an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result":  str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

			serializer = self.serializer_class(result, data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ElectionViewSet(viewsets.ModelViewSet):
	renderer_classes = (JSONRenderer, )
	queryset = Election.objects.all()
	serializer_class = ElectionSerializer
	model = Election

	def delete(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to delete an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
				result.delete()
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)
			except IntegrityError:
				return Response({"status": "400 - Bad Request", "result": str(self.model) + " is a foreign key to other models and thus cannot be deleted"}, status=status.HTTP_409_CONFLICT)
			return Response({"status": "204 - No Content", "response": "Successfully deleted " + str(self.model)})

	def get(self, request, format=None, pk=None):
		is_many = True
		if pk is None:
			result = self.model.objects.all()
		else:
			try:
				result = self.model.objects.get(pk=pk)
				is_many = False
			except self.model.DoesNotExist:
				return Response({"status": "404", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

		serializer = self.serializer_class(result, many=is_many)
		return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)

	def post(self, request, format=None, pk=None):
		if pk is None:
			serializer = self.serializer_class(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "201 - Created", "result": serializer.data}, status=status.HTTP_201_CREATED)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({"status": "400 - Bad Request", "result": "Cannot POST data to an already created id"}, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to update an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result":  str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

			serializer = self.serializer_class(result, data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class BallotViewSet(viewsets.ModelViewSet):
	renderer_classes = (JSONRenderer, )
	queryset = Ballot.objects.all()
	serializer_class = BallotSerializer
	model = Ballot

	def delete(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to delete an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
				result.delete()
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)
			except IntegrityError:
				return Response({"status": "400 - Bad Request", "result": str(self.model) + " is a foreign key to other models and thus cannot be deleted"}, status=status.HTTP_409_CONFLICT)
			return Response({"status": "204 - No Content", "response": "Successfully deleted " + str(self.model)})

	def get(self, request, format=None, pk=None):
		is_many = True
		if pk is None:
			result = self.model.objects.all()
		else:
			try:
				result = self.model.objects.get(pk=pk)
				is_many = False
			except self.model.DoesNotExist:
				return Response({"status": "404", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

		serializer = self.serializer_class(result, many=is_many)
		return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)

	def post(self, request, format=None, pk=None):
		if pk is None:
			serializer = self.serializer_class(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "201 - Created", "result": serializer.data}, status=status.HTTP_201_CREATED)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({"status": "400 - Bad Request", "result": "Cannot POST data to an already created id"}, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to update an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result":  str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

			serializer = self.serializer_class(result, data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class PersonViewSet(viewsets.ModelViewSet):
	renderer_classes = (JSONRenderer, )
	queryset = Person.objects.all()
	serializer_class = PersonSerializer
	model = Person

	def delete(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to delete an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
				result.delete()
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)
			except IntegrityError:
				return Response({"status": "400 - Bad Request", "result": str(self.model) + " is a foreign key to other models and thus cannot be deleted"}, status=status.HTTP_409_CONFLICT)
			return Response({"status": "204 - No Content", "response": "Successfully deleted " + str(self.model)})

	def get(self, request, format=None, pk=None):
		is_many = True
		if pk is None:
			result = self.model.objects.all()
		else:
			try:
				result = self.model.objects.get(pk=pk)
				is_many = False
			except self.model.DoesNotExist:
				return Response({"status": "404", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

		serializer = self.serializer_class(result, many=is_many)
		return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)

	def post(self, request, format=None, pk=None):
		if pk is None:
			serializer = self.serializer_class(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "201 - Created", "result": serializer.data}, status=status.HTTP_201_CREATED)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({"status": "400 - Bad Request", "result": "Cannot POST data to an already created id"}, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to update an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result":  str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

			serializer = self.serializer_class(result, data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class PrecinctViewSet(viewsets.ModelViewSet):
	renderer_classes = (JSONRenderer, )
	queryset = Precinct.objects.all()
	serializer_class = PrecinctSerializer
	model = Precinct

	def delete(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to delete an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
				result.delete()
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)
			except IntegrityError:
				return Response({"status": "400 - Bad Request", "result": str(self.model) + " is a foreign key to other models and thus cannot be deleted"}, status=status.HTTP_409_CONFLICT)
			return Response({"status": "204 - No Content", "response": "Successfully deleted " + str(self.model)})

	def get(self, request, format=None, pk=None):
		is_many = True
		if pk is None:
			result = self.model.objects.all()
		else:
			try:
				result = self.model.objects.get(pk=pk)
				is_many = False
			except self.model.DoesNotExist:
				return Response({"status": "404", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

		serializer = self.serializer_class(result, many=is_many)
		return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)

	def post(self, request, format=None, pk=None):
		if pk is None:
			serializer = self.serializer_class(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "201 - Created", "result": serializer.data}, status=status.HTTP_201_CREATED)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({"status": "400 - Bad Request", "result": "Cannot POST data to an already created id"}, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to update an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result":  str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

			serializer = self.serializer_class(result, data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class MeasureViewSet(viewsets.ModelViewSet):
	renderer_classes = (JSONRenderer, )
	queryset = Measure.objects.all()
	serializer_class = MeasureSerializer
	model = Measure

	def delete(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to delete an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
				result.delete()
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)
			except IntegrityError:
				return Response({"status": "400 - Bad Request", "result": str(self.model) + " is a foreign key to other models and thus cannot be deleted"}, status=status.HTTP_409_CONFLICT)
			return Response({"status": "204 - No Content", "response": "Successfully deleted " + str(self.model)})

	def get(self, request, format=None, pk=None):
		is_many = True
		if pk is None:
			result = self.model.objects.all()
		else:
			try:
				result = self.model.objects.get(pk=pk)
				is_many = False
			except self.model.DoesNotExist:
				return Response({"status": "404", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

		serializer = self.serializer_class(result, many=is_many)
		return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)

	def post(self, request, format=None, pk=None):
		if pk is None:
			serializer = self.serializer_class(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "201 - Created", "result": serializer.data}, status=status.HTTP_201_CREATED)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({"status": "400 - Bad Request", "result": "Cannot POST data to an already created id"}, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to update an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result":  str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

			serializer = self.serializer_class(result, data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class PrecinctViewSet(viewsets.ModelViewSet):
	renderer_classes = (JSONRenderer, )
	queryset = Precinct.objects.all()
	serializer_class = PrecinctSerializer
	model = Precinct

	def delete(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to delete an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
				result.delete()
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)
			except IntegrityError:
				return Response({"status": "400 - Bad Request", "result": str(self.model) + " is a foreign key to other models and thus cannot be deleted"}, status=status.HTTP_409_CONFLICT)
			return Response({"status": "204 - No Content", "response": "Successfully deleted " + str(self.model)})

	def get(self, request, format=None, pk=None):
		is_many = True
		if pk is None:
			result = self.model.objects.all()
		else:
			try:
				result = self.model.objects.get(pk=pk)
				is_many = False
			except self.model.DoesNotExist:
				return Response({"status": "404", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

		serializer = self.serializer_class(result, many=is_many)
		return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)

	def post(self, request, format=None, pk=None):
		if pk is None:
			serializer = self.serializer_class(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "201 - Created", "result": serializer.data}, status=status.HTTP_201_CREATED)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({"status": "400 - Bad Request", "result": "Cannot POST data to an already created id"}, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to update an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result":  str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

			serializer = self.serializer_class(result, data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class PoliticianViewSet(viewsets.ModelViewSet):
	renderer_classes = (JSONRenderer, )
	queryset = Politician.objects.all()
	serializer_class = PoliticianSerializer
	model = Politician

	def delete(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to delete an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
				result.delete()
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)
			except IntegrityError:
				return Response({"status": "400 - Bad Request", "result": str(self.model) + " is a foreign key to other models and thus cannot be deleted"}, status=status.HTTP_409_CONFLICT)
			return Response({"status": "204 - No Content", "response": "Successfully deleted " + str(self.model)})

	def get(self, request, format=None, pk=None):
		is_many = True
		if pk is None:
			result = self.model.objects.all()
		else:
			try:
				result = self.model.objects.get(pk=pk)
				is_many = False
			except self.model.DoesNotExist:
				return Response({"status": "404", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

		serializer = self.serializer_class(result, many=is_many)
		return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)

	def post(self, request, format=None, pk=None):
		if pk is None:
			serializer = self.serializer_class(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "201 - Created", "result": serializer.data}, status=status.HTTP_201_CREATED)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({"status": "400 - Bad Request", "result": "Cannot POST data to an already created id"}, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to update an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result":  str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

			serializer = self.serializer_class(result, data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class OfficeViewSet(viewsets.ModelViewSet):
	renderer_classes = (JSONRenderer, )
	queryset = Office.objects.all()
	serializer_class = OfficeSerializer
	model = Office

	def delete(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to delete an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
				result.delete()
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)
			except IntegrityError:
				return Response({"status": "400 - Bad Request", "result": str(self.model) + " is a foreign key to other models and thus cannot be deleted"}, status=status.HTTP_409_CONFLICT)
			return Response({"status": "204 - No Content", "response": "Successfully deleted " + str(self.model)})

	def get(self, request, format=None, pk=None):
		is_many = True
		if pk is None:
			result = self.model.objects.all()
		else:
			try:
				result = self.model.objects.get(pk=pk)
				is_many = False
			except self.model.DoesNotExist:
				return Response({"status": "404", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

		serializer = self.serializer_class(result, many=is_many)
		return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)

	def post(self, request, format=None, pk=None):
		if pk is None:
			serializer = self.serializer_class(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "201 - Created", "result": serializer.data}, status=status.HTTP_201_CREATED)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({"status": "400 - Bad Request", "result": "Cannot POST data to an already created id"}, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to update an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result":  str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

			serializer = self.serializer_class(result, data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ReferendumViewSet(viewsets.ModelViewSet):
	renderer_classes = (JSONRenderer, )
	queryset = Referendum.objects.all()
	serializer_class = ReferendumSerializer
	model = Referendum

	def delete(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to delete an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
				result.delete()
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)
			except IntegrityError:
				return Response({"status": "400 - Bad Request", "result": str(self.model) + " is a foreign key to other models and thus cannot be deleted"}, status=status.HTTP_409_CONFLICT)
			return Response({"status": "204 - No Content", "response": "Successfully deleted " + str(self.model)})

	def get(self, request, format=None, pk=None):
		is_many = True
		if pk is None:
			result = self.model.objects.all()
		else:
			try:
				result = self.model.objects.get(pk=pk)
				is_many = False
			except self.model.DoesNotExist:
				return Response({"status": "404", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

		serializer = self.serializer_class(result, many=is_many)
		return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)

	def post(self, request, format=None, pk=None):
		if pk is None:
			serializer = self.serializer_class(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "201 - Created", "result": serializer.data}, status=status.HTTP_201_CREATED)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({"status": "400 - Bad Request", "result": "Cannot POST data to an already created id"}, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to update an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result":  str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

			serializer = self.serializer_class(result, data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class CandidacyViewSet(viewsets.ModelViewSet):
	renderer_classes = (JSONRenderer, )
	queryset = Candidacy.objects.all()
	serializer_class = CandidacySerializer
	model = Candidacy

	def delete(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to delete an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
				result.delete()
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)
			except IntegrityError:
				return Response({"status": "400 - Bad Request", "result": str(self.model) + " is a foreign key to other models and thus cannot be deleted"}, status=status.HTTP_409_CONFLICT)
			return Response({"status": "204 - No Content", "response": "Successfully deleted " + str(self.model)})

	def get(self, request, format=None, pk=None):
		is_many = True
		if pk is None:
			result = self.model.objects.all()
		else:
			try:
				result = self.model.objects.get(pk=pk)
				is_many = False
			except self.model.DoesNotExist:
				return Response({"status": "404", "result": str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

		serializer = self.serializer_class(result, many=is_many)
		return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)

	def post(self, request, format=None, pk=None):
		if pk is None:
			serializer = self.serializer_class(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "201 - Created", "result": serializer.data}, status=status.HTTP_201_CREATED)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({"status": "400 - Bad Request", "result": "Cannot POST data to an already created id"}, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, format=None, pk=None):
		if pk is None:
			return Response({"status": "400 - Bad Request", "result": "Please specify ID to update an entry"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			try:
				result = self.model.objects.get(pk=pk)
			except self.model.DoesNotExist:
				return Response({"status": "404 - Not Found", "result":  str(self.model) + " with given id does not exist"}, status=status.HTTP_404_NOT_FOUND)

			serializer = self.serializer_class(result, data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response({"status": "200 - OK", "result": serializer.data}, status=status.HTTP_200_OK)
			return Response({"status": "400 - Bad Request", "missing data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
