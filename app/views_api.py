from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from .models import *
from rest_framework import viewsets, status
from rest_framework.renderers import JSONRenderer
from .serializers import *
from rest_framework.response import Response
import urllib
import json

from .utility_methods import WEBSITE_URL

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
		total_votes = 0
		if measure.measure_type == "C":
			candidates = []
			m_json = {}
			m_json["type"] = measure.get_measure_type_display()
			m_json["office"] = measure.__str__()
			for candidacy in measure.candidacies.all():
				c_json = {}
				c_json["candidate"] = candidacy.politician.__str__()
				c_json["votes"] = candidacy.votes
				total_votes += candidacy.votes
				candidates.append(c_json)
			m_json["total_votes"] = total_votes
			m_json["candidates"] = candidates
			measures.append(m_json)
		else:
			choices = []
			m_json = {}
			m_json["type"] = measure.get_measure_type_display()
			m_json["question_text"] = measure.__str__()
			for referendum in measure.referendums.all():
				for choice in referendum.choices.all():
					c_json = {}
					c_json["choice_text"] = choice.__str__()
					c_json["votes"] = choice.votes
					total_votes += choice.votes
					choices.append(c_json)
			m_json["total_votes"] = total_votes
			m_json["choices"] = choices
			measures.append(m_json)
	return JsonResponse({ election.id : measures})

def election_results(request):
    args = {}
    elections = []
    open_elections = []
    closed_elections = []
    future_elections = []
    all_ballots = Ballot.objects.all()
    for ballot in all_ballots:
        total_votes = 0
        election = ballot.election
        measures = ballot.measures.all()
        for measure in measures:
            if measure.measure_type == "C":
                candidacies = measure.candidacies.all()
                for candidate in candidacies:
                    total_votes += candidate.votes
        json = {}
        json["name"] = measure.__str__()
        json["id"] = election.id
        json["total_votes"] = total_votes
        json["type"] = election.get_type_display()
        json["state"] = "open"
        if json["state"] == "open":
            open_elections.append(json)
        elif json["state"] == "closed":
            closed_elections.append(json)
        else:
            future_elections.append(json)
    return JsonResponse({"open": open_elections, "closed": closed_elections, "future": future_elections})
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

def search_voters(request):
	args = {
		"firstName": "",
		"lastName": "",
		"voterNumber": "",
	}
	for key in request.GET:
		args[key] = request.GET[key]

	voters = [
		{
				"voter_number" : "020342357",
				"voter_status" : "active",
				"date_registered" : "2007-08-20",
				"last_name" : "Garcia",
				"first_name" : "Juan",
				"street_address" : "123 Main Street",
				"city" : "Charlottesville",
				"state" : "VA",
				"zip" : "22902",
				"locality" : "ALBEMARLE COUNTY",
				"precinct" : "405-CALE",
				"precinct_id" : "0405"
		},
		{
				"voter_number" : "12345",
				"voter_status" : "active",
				"date_registered" : "2007-08-20",
				"last_name" : "Doe",
				"first_name" : "John",
				"street_address" : "123 Main Street",
				"city" : "Charlottesville",
				"state" : "VA",
				"zip" : "22902",
				"locality" : "ALBEMARLE COUNTY",
				"precinct" : "405-CALE",
				"precinct_id" : "0405"
		},
		{
				"voter_number" : "1",
				"voter_status" : "active",
				"date_registered" : "2007-08-20",
				"last_name" : "Chan",
				"first_name" : "Jackie",
				"street_address" : "123 Main Street",
				"city" : "Charlottesville",
				"state" : "VA",
				"zip" : "22902",
				"locality" : "ALBEMARLE COUNTY",
				"precinct" : "405-CALE",
				"precinct_id" : "0405"
		},
		{
				"voter_number" : "1",
				"voter_status" : "active",
				"date_registered" : "2007-08-20",
				"last_name" : "Baratheon",
				"first_name" : "Joffrey",
				"street_address" : "123 Main Street",
				"city" : "Charlottesville",
				"state" : "VA",
				"zip" : "22902",
				"locality" : "ALBEMARLE COUNTY",
				"precinct" : "405-CALE",
				"precinct_id" : "0405"
		},
	]

	req = urllib.request.Request(WEBSITE_URL + 'api/voters/')
	resp_json = urllib.request.urlopen(req).read().decode('utf-8')
	response = json.loads(resp_json)

	voters = response["result"]

	matching_voters = []
	for voter in voters:
		# first name, last, etc not provided so we have to query

		person = Person.objects.get(pk=voter["person"])

		fn = person.first_name == args["firstName"]
		ln = person.last_name == args["lastName"]
		vn = voter["voter_number"] == args["voterNumber"]

		if fn and ln and vn:
			voter["first_name"] = person.first_name
			voter["last_name"] = person.last_name
			matching_voters.append(voter)
	return JsonResponse({
		'voters': matching_voters,
		'status': '200 - OK',
		'args': args,
	})


def seed_voters(request):
	fn = ["John", "Sam", "Anakin", "Clark", "Tony", "Spittony", "Toni"]
	ln = ["Smith", "Jacobsson", "Newsom", "Mangum", "Garcia"]
	i = 0
	precinct = Precinct(
		name="405-CALE",
		id="0405"
	)
	precinct.save()
	for f in fn:
		for l in ln:
			p = Person(
				first_name=f,
				last_name=l,
				SSN=str(i),
				federal_district=1,
				state_district=2
			)
			
			p.save()

			voter = {
				"voter_number" : str(i),
				"voter_status" : "active",
				"date_registered" : "2007-08-20",
				"last_name" : ln,
				"first_name" : fn,
				"street_address" : "123 Main Street",
				"city" : "Charlottesville",
				"state" : "VA",
				"zip" : "22902",
				"locality" : "ALBEMARLE COUNTY",
				"precinct" : "405-CALE",
				"precinct_id" : "0405"
			}

			

			v = Voter(
				person=Person.objects.get(pk=p.pk),
				voter_status="A",
				date_registered=voter["date_registered"],
				street_address=voter["street_address"],
				city=voter["city"],
				state=voter["state"],
				zip_code=voter["zip"],
				locality=voter["locality"],
				precinct=Precinct.objects.get(id=voter["precinct_id"]),
				voter_number=voter["voter_number"],
			
			)
			
			v.save()

			i += 1




	'''
	voters = [
		{
				"voter_number" : "020342357",
				"voter_status" : "active",
				"date_registered" : "2007-08-20",
				"last_name" : "Garcia",
				"first_name" : "Juan",
				"street_address" : "123 Main Street",
				"city" : "Charlottesville",
				"state" : "VA",
				"zip" : "22902",
				"locality" : "ALBEMARLE COUNTY",
				"precinct" : "405-CALE",
				"precinct_id" : "0405"
		},
		{
				"voter_number" : "12345",
				"voter_status" : "active",
				"date_registered" : "2007-08-20",
				"last_name" : "Doe",
				"first_name" : "John",
				"street_address" : "123 Main Street",
				"city" : "Charlottesville",
				"state" : "VA",
				"zip" : "22902",
				"locality" : "ALBEMARLE COUNTY",
				"precinct" : "405-CALE",
				"precinct_id" : "0405"
		},
		{
				"voter_number" : "1",
				"voter_status" : "active",
				"date_registered" : "2007-08-20",
				"last_name" : "Chan",
				"first_name" : "Jackie",
				"street_address" : "123 Main Street",
				"city" : "Charlottesville",
				"state" : "VA",
				"zip" : "22902",
				"locality" : "ALBEMARLE COUNTY",
				"precinct" : "405-CALE",
				"precinct_id" : "0405"
		},
		{
				"voter_number" : "1",
				"voter_status" : "active",
				"date_registered" : "2007-08-20",
				"last_name" : "Baratheon",
				"first_name" : "Joffrey",
				"street_address" : "123 Main Street",
				"city" : "Charlottesville",
				"state" : "VA",
				"zip" : "22902",
				"locality" : "ALBEMARLE COUNTY",
				"precinct" : "405-CALE",
				"precinct_id" : "0405"
		},
	]
	'''





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
