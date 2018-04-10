from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from .models import *
from .forms import LoginForm, SignupForm, VoteValidationForm, BallotForm
from datetime import date
from django.views.decorators.csrf import csrf_exempt
from .utility_methods import validate_serial_code
from rest_framework.generics import *
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .serializers import *
from rest_framework import viewsets, status
from rest_framework.renderers import JSONRenderer
# Create your views here.
import json
import urllib

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
	elif request.method == "POST":
		data = SignupForm(request.POST)
		form = SignupForm

		if (data.password != data.confirm_password):
			return render(request, 'app/signup.html', {
			"form": form,
			})
		else:
			return signup_confirmation.html

def page_elections(request):
	if request.method == "GET":
		election_data = {}
		req = urllib.request.Request('http://localhost:8000/api/elections/')
		resp_json = urllib.request.urlopen(req).read().decode('utf-8')
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

		return render(request, 'app/elections.html', {
			"election_data": election_data
		})

def results(request):
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
		return render(request, 'app/results.html', {
			"election_data": "election_data",
		})

def election_result(request, pk):
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
		return render(request, 'app/election_result.html', {
			'election': elections[pk],
			"pk": pk,
		})

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


class BallotViewSet(ModelViewSet):
    serializer_class = BallotSerializer
    queryset = Ballot.objects.all()

class VoterViewSet(viewsets.ModelViewSet):
   renderer_classes = (JSONRenderer, )
   queryset = Voter.objects.all()
   serializer_class = VoterSerializer
   model = Voter

   def delete(self, request, format=None, pk=None):
      if pk is None:
         return Response({'status': '400 - Bad Request', 'result': 'Please specify ID to delete an entry'}, status=status.HTTP_400_BAD_REQUEST)
      else:
         try:
            result = self.model.objects.get(pk=pk)
            result.delete()
         except self.model.DoesNotExist:
            return Response({'status': '404 - Not Found', 'result': 'User with given id does not exist'}, status=status.HTTP_404_NOT_FOUND)
         except IntegrityError:
            return Response({'status': '400 - Bad Request', 'result': 'User is a foreign key to other models and thus cannot be deleted'}, status=status.HTTP_409_CONFLICT)
         return Response({'status': '204 - No Content', 'response': "Successfully deleted user"})

   def get(self, request, format=None, pk=None):
      is_many = True
      if pk is None:
         result = self.model.objects.all()
      else:
         try:
            result = self.model.objects.get(pk=pk)
            is_many = False
         except self.model.DoesNotExist:
            return Response({'status': '404', 'result': 'User with given id does not exist'}, status=status.HTTP_404_NOT_FOUND)

      serializer = self.serializer_class(result, many=is_many)
      return Response({'status': '200 - OK', 'result': serializer.data}, status=status.HTTP_200_OK)

   def post(self, request, format=None, pk=None):
      if pk is None:
         serializer = self.serializer_class(data=request.data)
         if serializer.is_valid():
            serializer.save()
            return Response({'status': '201 - Created', 'result': serializer.data}, status=status.HTTP_201_CREATED)
         return Response({'status': '400 - Bad Request', 'missing data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
      else:
         return Response({'status': '400 - Bad Request', 'result': 'Cannot POST data to an already created id'}, status=status.HTTP_400_BAD_REQUEST)

   def put(self, request, format=None, pk=None):
      if pk is None:
         return Response({'status': '400 - Bad Request', 'result': 'Please specify ID to update an entry'}, status=status.HTTP_400_BAD_REQUEST)
      else:
         try:
            result = self.model.objects.get(pk=pk)
         except self.model.DoesNotExist:
            return Response({'status': '404 - Not Found', 'result': 'User with given id does not exist'}, status=status.HTTP_404_NOT_FOUND)

         serializer = self.serializer_class(result, data=request.data)
         if serializer.is_valid():
            serializer.save()
            return Response({'status': '200 - OK', 'result': serializer.data}, status=status.HTTP_200_OK)
         return Response({'status': '400 - Bad Request', 'missing data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ElectionViewSet(viewsets.ModelViewSet):
   renderer_classes = (JSONRenderer, )
   queryset = Election.objects.all()
   serializer_class = ElectionSerializer
   model = Election

   def delete(self, request, format=None, pk=None):
      if pk is None:
         return Response({'status': '400 - Bad Request', 'result': 'Please specify ID to delete an entry'}, status=status.HTTP_400_BAD_REQUEST)
      else:
         try:
            result = self.model.objects.get(pk=pk)
            result.delete()
         except self.model.DoesNotExist:
            return Response({'status': '404 - Not Found', 'result': 'User with given id does not exist'}, status=status.HTTP_404_NOT_FOUND)
         except IntegrityError:
            return Response({'status': '400 - Bad Request', 'result': 'User is a foreign key to other models and thus cannot be deleted'}, status=status.HTTP_409_CONFLICT)
         return Response({'status': '204 - No Content', 'response': "Successfully deleted user"})

   def get(self, request, format=None, pk=None):
      is_many = True
      if pk is None:
         result = self.model.objects.all()
      else:
         try:
            result = self.model.objects.get(pk=pk)
            is_many = False
         except self.model.DoesNotExist:
            return Response({'status': '404', 'result': 'User with given id does not exist'}, status=status.HTTP_404_NOT_FOUND)

      serializer = self.serializer_class(result, many=is_many)
      return Response({'status': '200 - OK', 'result': serializer.data}, status=status.HTTP_200_OK)

   def post(self, request, format=None, pk=None):
      if pk is None:
         serializer = self.serializer_class(data=request.data)
         if serializer.is_valid():
            serializer.save()
            return Response({'status': '201 - Created', 'result': serializer.data}, status=status.HTTP_201_CREATED)
         return Response({'status': '400 - Bad Request', 'missing data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
      else:
         return Response({'status': '400 - Bad Request', 'result': 'Cannot POST data to an already created id'}, status=status.HTTP_400_BAD_REQUEST)

   def put(self, request, format=None, pk=None):
      if pk is None:
         return Response({'status': '400 - Bad Request', 'result': 'Please specify ID to update an entry'}, status=status.HTTP_400_BAD_REQUEST)
      else:
         try:
            result = self.model.objects.get(pk=pk)
         except self.model.DoesNotExist:
            return Response({'status': '404 - Not Found', 'result': 'User with given id does not exist'}, status=status.HTTP_404_NOT_FOUND)

         serializer = self.serializer_class(result, data=request.data)
         if serializer.is_valid():
            serializer.save()
            return Response({'status': '200 - OK', 'result': serializer.data}, status=status.HTTP_200_OK)
         return Response({'status': '400 - Bad Request', 'missing data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
