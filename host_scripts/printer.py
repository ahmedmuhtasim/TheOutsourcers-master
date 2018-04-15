from flask import Flask, request
from escpos.printer import Usb
app = Flask(__name__)
p = Usb(0x416, 0x5011)
@app.route('/voternumber', methods=['POST'])
def result():
    p.text(' ' + request.form['voter'])
    p.cut()
    return 'Received!' # response to your request.

@app.route('/ballot', methods=['POST'])
def votedfor():
    p.text(' ' + request.form['ballot'])
    p.cut()
    return 'Received a ballot!' # response to your request.

app.run(host='172.27.98.179', port=5000)
