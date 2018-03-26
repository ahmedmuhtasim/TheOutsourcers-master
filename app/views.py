from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
# from .forms import SearchForm

# Create your views here.

def home(request):

	''' GET DATA FROM API & FORMAT
	req = urllib.request.Request('http://exp-api:8000/exp/home')
	resp_json = urllib.request.urlopen(req).read().decode('utf-8')
	response = json.loads(resp_json)
	'''
	return render(request, 'app/home.html', {})