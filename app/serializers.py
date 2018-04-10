from rest_framework import serializers
from .models import *


class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = "__all__"

class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = "__all__"

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = "__all__"

class PoliticianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Politician
        fields = "__all__"

class BallotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ballot
        fields = "__all__"

class MeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measure
        fields = "__all__"

class CandidacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidacy
        fields = "__all__"

class ReferendumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referendum
        fields = "__all__"

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = "__all__"

class PrecinctSerializer(serializers.ModelSerializer):
    class Meta:
        model = Precinct
        fields = "__all__"

class Poll_WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll_Worker
        fields = "__all__"

class VoterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voter
        fields = "__all__"