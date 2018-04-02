# pseudomethod to validate a given serial code
def validate_serial_code(code):
	codes = ["12345", "helloworld", "wololo"]
	for i in range(len(codes)):
		if code == codes[i]:
			return True
	return False
