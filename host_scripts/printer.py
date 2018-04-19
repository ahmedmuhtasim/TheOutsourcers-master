from flask import Flask, request
from escpos.printer import Usb
import os

app = Flask(__name__)
#p = Usb(0x416, 0x5011)
p = Usb(0x456, 0x0808, 0, 0x81, 0x03)

@app.route('/voternumber', methods=['POST'])
def result():
	p.qr(request.form['voter'], size=10)
	p.text(request.form['voter'])
	p.cut()
	print(request.form['voter'])
	return 'Received!' # response to your request.

@app.route('/ballot', methods=['POST'])
def votedfor():
	for key in request.form.keys():
		for value in request.form.getlist(key):
			print(key, ":", value)
			p.text(' ' + key + ": " + value + '\n')

	p.image("voted.jpg")
	p.cut()
	return 'Received a ballot!' # response to your request.


app.run(host='0.0.0.0', port=5000)
