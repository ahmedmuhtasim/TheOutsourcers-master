from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from .models import *
from .forms import LoginForm, SignupForm, VoteValidationForm, BallotForm
from datetime import date
from django.views.decorators.csrf import csrf_exempt
from .utility_methods import validate_serial_code
# Create your views here.
from rest_framework import viewsets, status
from rest_framework.renderers import JSONRenderer
from .serializers import *
from rest_framework.response import Response
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
