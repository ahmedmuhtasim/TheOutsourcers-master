# pseudomethod to validate a given serial code
import random, string

def validate_serial_code(code):
	codes = ["12345", "helloworld", "wololo"]
	for i in range(len(codes)):
		if code == codes[i]:
			return True
	return False

def gen_alphanumeric(length=16):
	return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))


