from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from .models import *
from rest_framework import viewsets, status
from rest_framework.renderers import JSONRenderer
from .serializers import *
from rest_framework.response import Response
import urllib
import json

from .utility_methods import WEBSITE_URL, multikeysort

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
				c_json["running_mate"] = candidacy.running_mate.__str__()
				c_json["party"] = candidacy.get_party_affiliation_display()
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

import datetime

def elections_full(request):
	elections = Election.objects.all()
	open = []
	closed = []
	future = []
	for election in elections:
		# check if opened, closed, or current
		today = datetime.date.today()
		election_date = datetime.datetime.strptime(election.id, '%Y-%m').date()
		# set status
		status = ""
		if election_date < today:
			status = "closed"
		elif election_date == today:
			status = "open"
		else:
			status = "future"
		# get type
		election_type = election.get_type_display()
		# get vote counts through voter serial codes
		participant_count = len(VoterSerialCodes.objects.filter(election=election))
		# format title
		title = election.markup_str()
		measures = []
		# pull measures
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
					c_json["running_mate"] = candidacy.running_mate.__str__()
					c_json["party"] = candidacy.get_party_affiliation_display()
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
		json = { election.id : {
					"name" : title,
					"status": status,
					"type": election_type,
					"total_participants": participant_count,
					"measures": measures,
					}}
		if election_date < today:
			closed.append(json)
		elif election_date == today:
			open.append(json)
		else:
			future.append(json)
		return JsonResponse({"open": open,
							"closed": closed,
							"future": future
							})

def election_full(request, pk):
	election = Election.objects.get(pk=pk)
	# check if opened, closed, or current
	today = datetime.date.today()
	election_date = datetime.datetime.strptime(election.id, '%Y-%m').date()
	# set status
	status = ""
	if election_date < today:
		status = "closed"
	elif election_date == today:
		status = "open"
	else:
		status = "future"
	# get type
	election_type = election.get_type_display()
	# get vote counts through voter serial codes
	participant_count = len(VoterSerialCodes.objects.filter(election=election))
	# format title
	title = election.markup_str()
	measures = []
	# pull measures
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
				c_json["running_mate"] = candidacy.running_mate.__str__()
				c_json["party"] = candidacy.get_party_affiliation_display()
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
	return JsonResponse({ election.id : {
				"name" : title,
				"status": status,
				"type": election_type,
				"total_participants": participant_count,
				"measures": measures,}
				})

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
		"precinctId": "",
	}
	for key in request.GET:
		args[key] = request.GET[key]


	if len(args["precinctId"]) > 0:
		URL = 'http://cs3240votingproject.org/pollingsite/'+ str(args["precinctId"]) + '/?key=outsourcers'
	else: 
		URL = 'http://cs3240votingproject.org/voters/?key=outsourcers'
	
	req = urllib.request.Request(URL)

	resp_json = urllib.request.urlopen(req).read().decode('utf-8')
	response = json.loads(resp_json)
	
	voters = response["voters"]

	matching_voters = []
	for voter in voters:
		voter_first_name = voter["first_name"]
		voter_last_name = voter["last_name"]
		voter_voter_number = voter["voter_number"]

		voter_query = Voter.objects.filter(voter_number=voter_voter_number)
		precinct_query = Precinct.objects.filter(id=voter["precinct_id"])



		voter_in_database = len(voter_query) > 0
		precinct_in_database = len(precinct_query) > 0
		if not precinct_in_database:
			insert_precinct = Precinct(
				name=voter["precinct"],
				id=voter["precinct_id"]
			)
			insert_precinct.save()
			
		if not voter_in_database:
			insert_person = Person(
				first_name=voter["first_name"],
				last_name=voter["last_name"],
				SSN=str(''),
				federal_district=1,
				state_district=2,
				precinct=Precinct.objects.get(id=voter["precinct_id"]),
			)
			insert_person.save()

			insert_voter = Voter(
				person=Person.objects.get(pk=insert_person.pk),
				voter_status=voter["voter_status"],
				date_registered=voter["date_registered"],
				street_address=voter["street_address"],
				city=voter["city"],
				state=voter["state"],
				zip_code=voter["zip"],
				locality=voter["locality"],
				precinct=Precinct.objects.get(id=voter["precinct_id"]),
				voter_number=voter["voter_number"],
			)
			insert_voter.save()

		# first name, last, etc not provided so we have to query
		fn = True
		ln = True
		vn = True
		if len(args["firstName"]) > 0:
			fn = voter["first_name"] == args["firstName"]
		if len(args["lastName"]) > 0:
			ln = voter["last_name"] == args["lastName"]
		if len(args["voterNumber"]) > 0:
			ln = voter["voter_number"] == args["voterNumber"]

		if fn and ln and vn:
			matching_voter = {}
			matching_voter["first_name"] = voter["first_name"]
			matching_voter["last_name"] = voter["last_name"]
			matching_voter["voter_number"] = voter["voter_number"]
			matching_voters.append(matching_voter)
	if len(matching_voters) < 500: # don't want to spend too long sorting, establish maximum size where it's still okay to sort
		matching_voters = multikeysort(matching_voters, ['first_name', 'last_name'])
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
