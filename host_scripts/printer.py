from flask import Flask, request
from escpos.printer import Usb
app = Flask(__name__)
p = Usb(0x416, 0x5011)

def encode(location, time, id):							#method to send relevant data to the printer
														#we need to set sizes for each of the 3 parts (sum of 3 must be 12 digits). Current configuration: loc: 3, tim: 3, id: 6
		list = []										#array of size	13

		list.append((location//100)%10)				   #keep doing as many times as needed
		list.append((location//10)%10)
		list.append(location%10)
		
		list.append((time//100)%10)		
		list.append((time//10)%10)
		list.append(time%10)
		
		list.append((id//100000)%10)	
		list.append((id//10000)%10)
		list.append((id//1000)%10)
		list.append((id//100)%10)		
		list.append((id//10)%10)
		list.append(id%10)

		sum = 0											#keep track of sum
		
		for i in range(1, 12, 2):
				sum += list[i]
				
		sum *= 3
		
		for i in range(0, 11, 2):
				sum += list[i]	
				
						
		list.append(((((sum//10)+1)*10)-sum)%10)	   #append parity bit

		string = ''									   #string to return
		
		for i in range(0, len(list)):
				string += str(list[i])

		return string

def decode(string):									   #method to extract info from scanned barcode
		num = int(string)
		num //= 10									   #get rid of parity
		
		id = num%1000000
		time = (num//1000000)%1000
		location = (num//1000000000)%1000


		return location, time, id
@app.route('/voternumber', methods=['POST'])
def result():
	p.text(' ' + request.form['voter'])
	p.cut()
	print(request.form['voter'])
	return 'Received!' # response to your request.

@app.route('/ballot', methods=['POST'])
def votedfor():
	for key in request.form.keys():
		for value in request.form.getlist(key):
			print(key, ":", value)
			p.text(' ' + key + ": " + value + '\n')

	p.cut()
	return 'Received a ballot!' # response to your request.

app.run(host='172.27.98.179', port=5000)
