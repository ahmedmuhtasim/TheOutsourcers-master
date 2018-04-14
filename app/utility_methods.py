# pseudomethod to validate a given serial code
import random, string
from app.models import Voter, Election

def validate_serial_code(code):
        if Voter.objects.get(voter_key=code):
            voter = Voter.objects.get(pk=code)
            if voter.election:
                return voter.election
            return None
        return None
        #for i in range(len(codes)):
        #	if code == codes[i]:
	#		return True
	#return False

def gen_alphanumeric(length=16):
	return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))


