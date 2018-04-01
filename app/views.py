from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from .forms import LoginForm, SignupForm, VoteValidationForm, BallotForm
from datetime import date
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

def home(request):

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

def elections(request):
	if request.method == "GET":
		return render(request, 'app/elections.html', {})


# pseudomethod to validate a given serial code
def validate_serial_code(code):
	codes = ["12345", "helloworld", "wololo"]
	for i in range(len(codes)):
		if code == codes[i]:
			return True
	return False

@csrf_exempt
def vote(request):
	form = VoteValidationForm
	if request.method == "GET":
		is_day_of = False
		day_of = date(2018, 4, 1)
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