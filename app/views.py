from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from .models import *
from .forms import LoginForm, SignupForm, VoteValidationForm, BallotForm
from datetime import date
from django.views.decorators.csrf import csrf_exempt
from utility_methods import validate_serial_code
# Create your views here.

# API
def elections(request):
	args = {}
	elections = []
	all_elections = Election.objects.all()
	for election in all_elections:
		json = {}
		json["id"] = election.id
		json["type"] = election.get_type_display()
		elections.append(json)
	return JsonResponse({"elections": elections})

def election(request, pk):
	election = Election.objects.get(pk=pk)
	measures = []
	for measure in election.ballot.measures.all():
		json = {}
		json["measure_type"] = measure.get_measure_type_display()
		measures.append(json)
	return JsonResponse({ election.id : measures})

def voters(request):
	args = {}
	voters =[]
	for key in request.GET:
		args[key] = request.GET[key]
	if "pk" in args:
		all_voters = Voter.objects.get(pk=args["pk"])
		all_voters = [all_voters]
	else:
		all_voters = Voter.objects.all()
	for voter in all_voters:
		voter_info = {}
		json = {}
		json["first_name"] = voter.person.first_name
		json["last_name"] = voter.person.last_name
		json["SSN"] = voter.person.SSN
		json["federal_district"] = voter.person.federal_district
		json["state_district"] = voter.person.federal_district
		voter_info["voter_number"] = voter.voter_number
		voter_info["voter_status"] = voter.get_voter_status_display()
		voter_info["date_registered"] = voter.date_registered
		voter_info["street_address"] = voter.street_address
		voter_info["city"] = voter.city
		voter_info["state"] = voter.state
		voter_info["zip_code"] = voter.zip_code
		voter_info["locality"] = voter.locality
		voter_info["precinct"] = voter.precinct
		voter_info["voting_eligible"] = voter.voting_eligible
		json["voter_info"] = [voter_info]
		voters.append(json)
	return JsonResponse({"voters": voters})
	#return render(request, 'app/home.html', {})

#PAGES
def home(request):
	''' GET DATA FROM API & FORMAT
	req = urllib.request.Request('http://exp-api:8000/exp/home')
	resp_json = urllib.request.urlopen(req).read().decode('utf-8')
	response = json.loads(resp_json)
	'''
	return render(request, 'app/home.html', {})

def login(request):
	if request.method == "GET":
		form = LoginForm
		return render(request, 'app/login.html', {
			"form": form,
		})

def signup(request):
	if request.method == "GET":
		form = SignupForm
		return render(request, 'app/signup.html', {
			"form": form,
		})

def page_elections(request):
	if request.method == "GET":
		return render(request, 'app/elections.html', {})

@csrf_exempt
def vote(request):
	form = VoteValidationForm
	if request.method == "GET":
		is_day_of = False
		day_of = date(2018, 4, 2)
		today = date.today()
		is_day_of = today == day_of
		return render(request, 'app/vote.html', {
			'form': form,
			'is_day_of': is_day_of
		})
	elif request.method == "POST":
		form = VoteValidationForm(request.POST)
		if form.is_valid():
			if validate_serial_code(form.cleaned_data['serial_code']):
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
					'name': 'Luke Masters',
					'id': 'awh4Rtxu12'
				}
				return render(request, 'app/ballot.html', {
					'form': BallotForm,
					'election_data': election_data,
					'person': person,
				})

	return JsonResponse({
		"message": "Invalid Request"
	})

@csrf_exempt
def submit_vote(request):
	data = request.POST
	return JsonResponse(data)

def results(request):
	if request.method == "GET":
		return render(request, 'app/results.html', {})
