# pseudomethod to validate a given serial code
import random, string
from app.models import Voter, Election

def validate_serial_code(code):
        try:
            voter = Voter.objects.get(voter_number=code)
            if voter.election:
                return voter
            return None
        except:
            return None
        #for i in range(len(codes)):
        #	if code == codes[i]:
	#		return True
	#return False

def gen_alphanumeric(length=16):
	return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))

def is_logged_on(request):
	auth = request.COOKIES.get("auth")
	return auth

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