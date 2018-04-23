# pseudomethod to validate a given serial code
import random, string
from app.models import Voter, Election, VoterSerialCodes, Authenticator

def validate_serial_code(code):
	try:
		code = VoterSerialCodes.objects.filter(serial_code=code)
		if len(code) > 0:
			code = code[0]
			if code.election and not code.finished:
				return code
		return None
	except:
		return None

def gen_alphanumeric(length=16):
	return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))

def gen_numeric(length=16):
	return ''.join(random.choice(string.digits) for _ in range(length))

def is_logged_on(request):
	
	auth = request.COOKIES.get("auth")
	results = Authenticator.objects.filter(token=auth)
	
	return len(results) > 0

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

PRINT_PORT = "5000"


# UPDATE FOR DEPLOYMENT
IN_PRODUCTION = True

def get_website_url(in_production):
	URL_BASE = 'http://localhost:8000/'
	if in_production:
		URL_BASE = 'https://theoutsourcers.herokuapp.com/'
	return URL_BASE

WEBSITE_URL = get_website_url(IN_PRODUCTION)