# pseudomethod to validate a given serial code
import random, string
from app.models import Voter, Election

def validate_serial_code(code):
	try:
		'''
		serial code:
			- voter object
			- code
			- election
		'''
		v = SerialCode.objects.get(serial_code=code)
		voter = Voter.objects.get(voter_number=code)
		if voter.election:
			return voter
		return None
	except:
		return None

def gen_alphanumeric(length=16):
	return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))

def is_logged_on(request):
	auth = request.COOKIES.get("auth")
	return auth