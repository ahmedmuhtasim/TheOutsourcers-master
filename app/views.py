from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from .models import *
from .forms import LoginForm, SignupForm, VoteValidationForm, BallotForm
from datetime import date
from django.views.decorators.csrf import csrf_exempt
from .utility_methods import validate_serial_code, gen_numeric, gen_alphanumeric, is_logged_on, PRINT_PORT,  get_client_ip, WEBSITE_URL, IN_PRODUCTION
from rest_framework.generics import *
from .serializers import *
import json
from django.urls import reverse
import urllib
import hmac
from django.contrib.auth.hashers import make_password, check_password


# Public Pages
def home(request):
	""" GET DATA FROM API & FORMAT
	req = urllib.request.Request("http://exp-api:8000/exp/home")
	resp_json = urllib.request.urlopen(req).read().decode("utf-8")
	response = json.loads(resp_json)
	"""

	logged_on = is_logged_on(request)
	
	return render(request, "app/home.html", {
		"logged_on": logged_on,
		"website_url": WEBSITE_URL,
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
			"logged_on": logged_on,
			"website_url": WEBSITE_URL,
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
			"logged_on": logged_on,
			"website_url": WEBSITE_URL,
		})

import datetime

def election_brief(request):
	open = []
	closed = []
	future = []
	elections = Election.objects.all()
	for election in elections:
		# get id
		election_id = election.id
		# get type
		election_type = election.get_type_display()
		# get vote counts through voter serial codes
		participant_count = len(VoterSerialCodes.objects.filter(election=election))
		# format title
		title = election.markup_str()
		# check if opened, closed, or current
		today = date.today()
		election_date = datetime.datetime.strptime(election.id, '%Y-%m').date()
		json = {
			"name": title,
			"id": election_id,
			"total_participants": participant_count,
			"type" : election_type
		}
		# append to relevant list
		if election_date < today:
			closed.append(json)
		elif election_date == today:
			open.append(json)
		else:
			future.append(json)
		
	results = {
		"open": open,
		"closed": closed,
		"future": future,
	}
	return JsonResponse(results)

	'''
	#       election_data = {
	#           "open": [
	#               {
	#                   "name": "General Election : 2012-09",
	#                   "id": "2012-09",
	#                   "total_participants": 651,
	#                   "type": "general",
	#               }
	#           ],
	#           "closed": [
	#               {
	#                   "name": "General Election : 2012-09",
	#                   "id": "2012-09",
	#                   "total_participants": 651,
	#                   "type": "general",
	#               }
	#           ],
	#           "future": [
	#               {
	#                   "name": "General Election : 2012-09",
	#                   "id": "2012-09",
	#                   "total_participants": 651,
	#                   "type": "general",
	#               },
	#           ]
	#       }

	'''

def page_elections(request):
    logged_on = is_logged_on(request)
    
    if request.method == "GET":
        election_data = {}
        req = urllib.request.Request("http://localhost:8000/api/election_brief/")
        resp_json = urllib.request.urlopen(req).read().decode("utf-8")
        election_data = json.loads(resp_json)
	#       return JsonResponse(election_data)
	#       election_data = {
	#           "open": [
	#               {
	#                   "name": "Equifax new President",
	#                   "id": "equifax-2018",
	#                   "total_votes": 651,
	#                   "type": "general",
	#                   "state": "open"
	#               }
	#           ],
	#           "closed": [
	#               {
	#                   "name": "Presidential Race 2012",
	#                   "id": "pres-2012",
	#                   "total_votes": 22347000,
	#                   "type": "general",
	#                   "state": "closed"
	#               }
	#           ],
	#           "future": [
	#               {
	#                   "name": "Midterm 2018",
	#                   "id": "midterm-2018",
	#                   "total_votes": 0,
	#                   "type": "general",
	#                   "state": "not-yet-open"
	#               },
	#           ]
	#       }

        return render(request, "app/elections.html", {
            "election_data": election_data,
            "logged_on": logged_on,
				"website_url": WEBSITE_URL,
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
			"website_url": WEBSITE_URL,
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
				"website_url": WEBSITE_URL,
			})

		# Sanitize username and password fields
		username = f.cleaned_data['username']
		password = f.cleaned_data['password']

		user_results = User.objects.filter(username=username)

		if len(user_results) != 1:
			return render(request, 'app/login.html', {
				"form": form,
				"logged_on": logged_on,
				"errorMessage": "Username or Password Incorrect",
				"website_url": WEBSITE_URL,
			})

		user = user_results[0]

		# check password
		if not check_password(password, user.password):
			return render(request, 'app/login.html', {
				"form": form,
				"logged_on": logged_on,
				"errorMessage": "Password Incorrect",
				"website_url": WEBSITE_URL,
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
			"logged_on": logged_on,
			"website_url": WEBSITE_URL,
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
				"website_url": WEBSITE_URL,
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
				"errorMessage": "Username Already Taken",
				"website_url": WEBSITE_URL,
			})

		# check password
		if confirm_password != password:
			return render(request, 'app/signup.html', {
				"form": form,
				"logged_on": logged_on,
				"errorMessage": "Passwords Don't Match",
				"website_url": WEBSITE_URL,
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
		"logged_on": logged_on,
		"website_url": WEBSITE_URL,
	})

def signout(request):
	logged_on = is_logged_on(request)
	# If we received a GET request instead of a POST request
	response = HttpResponseRedirect(reverse('home'))
	response.delete_cookie('auth')

	return response

# START PROTECTED PAGES

# Start Vote/Ballot Flow
@csrf_exempt
def vote(request):
	logged_on = is_logged_on(request)
	
	form = VoteValidationForm
	if request.method == "GET":
		is_day_of = False
		day_of = date(2018, 4, 14)
		today = date.today()
		is_day_of = True
		return render(request, "app/vote.html", {
			"form": form,
			"logged_on": logged_on,
			"is_day_of": is_day_of,
			"website_url": WEBSITE_URL,
		})
	elif request.method == "POST":
		form = VoteValidationForm(request.POST)

		if form.is_valid():
			
			voter = validate_serial_code(serial_code)
			
			if str(type(voter)) == "<class 'NoneType'>" : # <-- shitty fix later
				return render(request, "app/vote.html", {
					"errorMessage": "Serial Code Invalid",
					"logged_on": logged_on,
					"form": form,
					"is_day_of": True,
					"website_url": WEBSITE_URL,
				})

			if voter.election:
				election = voter.election
				ballot = election.ballot

			return render(request, "app/ballot.html", {
				"form": BallotForm,
				"election_data": ballot,
				"serial_code": voter.serial_code,
				"logged_on": logged_on,
				"primary": "R",			# R is republican, D democrat, G general
				"website_url": WEBSITE_URL,
			})

	return JsonResponse({
		"message": "Invalid Request"
	})

@csrf_exempt
def submit_vote(request):
	data = request.POST

	serial_code = data['serial_code']
	s = VoterSerialCodes.objects.get(serial_code=serial_code)
	if s.finished:
		return render(request, "app/submitVote.html", {
			"errorMessage": "Cannot submit vote twice - vote not counted!",
			"website_url": WEBSITE_URL,
		})

	s.finished = True
	v = s.voter
	v.election = None
	v.save()
	s.save()

	print_data = {}
	# Printing the serial code will change eventually - it's to ensure receipts look different
	print_data['serial_code'] = serial_code 
	for key in data.keys():
		if key != "serial_code":
			measure = Measure.objects.get(pk=key)
			if measure.measure_type == 'C':
				candidacy = Candidacy.objects.get(pk=data[key])
				print_data[measure.__str__()] = candidacy.__str__()
				candidacy.votes += 1
				candidacy.save()
			else:
				choice = Choice.objects.get(pk=data[key])
				print_data[measure.__str__()] = choice.__str__()
				choice.votes += 1
				choice.save()

	ip = get_client_ip(request)
	PRINT_URL = "http://" + ip + ":" + PRINT_PORT + "/ballot"

	values = print_data

	encoded_values = urllib.parse.urlencode(values).encode('ascii')
	req = urllib.request.Request(PRINT_URL, encoded_values)
	
	with urllib.request.urlopen(req) as response:
		response.read()

	return render(request, "app/submitVote.html", {
		"website_url": WEBSITE_URL,
	})

def pollworker_dashboard(request):
	
	logged_on = is_logged_on(request)
	# If the authenticator cookie wasn't set...
	if not logged_on:
		return HttpResponseRedirect(reverse('login'))
	
	auth = Authenticator.objects.get(token=request.COOKIES.get("auth"))
	user = User.objects.get(pk=auth.user_id)

	# even if the user is logged in, they need to be a pollworker to access this page
	if user.role != "PW":
		return HttpResponseRedirect(reverse('login'))

	return render(request, "app/pollworker_dashboard.html", {
		"auth": auth,
		"role": user.role,
		"logged_on": logged_on,
		"website_url": WEBSITE_URL,
	})
	
@csrf_exempt
def get_voter_serial_code(request):
	'''
		1) update Voter's election field to the currently administered election
		2) generate new alphanumeric serialCode
		3) hit evan's api endpoint and send it the new serialCode
	'''
	args = {}
	for key in request.GET:
		args[key] = request.GET[key]

	if "voter_number" not in args or "election_id" not in args:
		return JsonResponse({
			"status": "400 - BAD REQUEST",
			"message": "Please provide both voter_number and election_id",
			"serial_code": "None generated"
		})
	
	# initialize reused vars
	serial_code = gen_alphanumeric(12)
	the_voter = Voter.objects.get(voter_number=args["voter_number"])
	the_election = Election.objects.get(id=args["election_id"])

	# check if serial code already generated for voter for this election
	matching_serial_codes = VoterSerialCodes.objects.filter(
		voter=the_voter
	).filter(
		election=the_election
	)

	if len(matching_serial_codes) > 0:
		return JsonResponse({
			"status": "400 - BAD REQUEST",
			"message": "Voter has already voted in this election",
			"serial_code": "None generated"
		})

	# 1)
	the_voter.election = the_election
	the_voter.save(update_fields=['election'])

	# 2) 
	new_serial = VoterSerialCodes(
		voter = the_voter,
		election = the_election,
		serial_code = serial_code,
		finished=False
	)
	new_serial.save()

	final_response = {
		"status": "200 - OK",
		"message": "Voter ok! Created serial code!",
		"serial_code": serial_code
	}

	ip = get_client_ip(request)
	PRINT_URL = "http://" + ip + ":" + PRINT_PORT + "/voternumber"
	values = {
		'voter' : serial_code,
	}
	try:
		encoded_values = urllib.parse.urlencode(values).encode('ascii')
		req = urllib.request.Request(PRINT_URL, encoded_values)
		
		with urllib.request.urlopen(req) as response:
			response.read()
	except:
		final_response["error"] = "Couldn't find printer server."

	# Once everything's done, just redirect back to the dashboard
	return JsonResponse(final_response)

# End Vote/Ballot Flow
# END PROTECTED PAGES
