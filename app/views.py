from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from .models import *
# from .forms import SearchForm

# Create your views here.

def home(request):

	''' GET DATA FROM API & FORMAT
	req = urllib.request.Request('http://exp-api:8000/exp/home')
	resp_json = urllib.request.urlopen(req).read().decode('utf-8')
	response = json.loads(resp_json)
	'''
	return render(request, 'app/home.html', {})

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

def election(request):
	election_id = ""
	for letter in request.path[11:]:
		if letter != '/':
			election_id += letter
		else:
			break
	election = Election.objects.get(pk=election_id)
	json = {}
	json["id"] = election.id
	json["type"] = election.type

#	json["ballot"] = election.ballot
	return JsonResponse({ election.id : election.type})

