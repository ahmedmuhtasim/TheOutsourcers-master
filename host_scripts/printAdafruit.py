from escpos.printer import Usb
from Adafruit_IO import MQTTClient
import ast
import time
import json

p = Usb(0x456, 0x0808, 0, 0x81, 0x03)

secrets = open("../.env").readlines()
ADAFRUIT_IO_KEY = secrets[0][secrets[0].find('=')+1:-1]
ADAFRUIT_IO_USERNAME = secrets[1][secrets[1].find('=')+1:-1]

voter_feed = "voter"
vote_feed = "vote"

def vote_connected(client):
    print('Listening to vote...')
    client.subscribe(vote_feed)

def voter_connected(client):
    print('Listening to voter...')
    client.subscribe(voter_feed)

def disconnected(client):
    client.connect()
    print('Disconnected from Adafruit IO!')

def vote_message(client, feed_id, payload):
    d = ast.literal_eval(payload)
    for key in d.keys():
        print(key, ":", d[key])
        p.text(' ' + str(key) + ': ' + str(d[key]) + '\n')
    p.image("voted.jpg")
    p.cut()


def voter_message(client, feed_id, payload):
    p.qr(payload, size=10)
    p.text("Hi there!\n")
    p.text("Thanks for choosing The \n")
    p.text("Outsourcers, your primary\n")
    p.text("voting experience!\n")
    p.text("Take me to the booth\n")
    p.text("and select either general,\n")
    p.text("if voting in a general\n")
    p.text("or the party whose primary\n")
    p.text("you are voting for.\n")
    p.text("Then, scan the QR code into\n")
    p.text("the box.  Thanks!\n")
    p.text("If that doesn't work,\n")
    p.text("try typing this manually:\n")
    p.text(payload)
    p.cut()
    print(payload)

vote_client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
vote_client.on_connect    = vote_connected
vote_client.on_disconnect = disconnected
vote_client.on_message = vote_message
vote_client.connect()
vote_client.loop_background()

voter_client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
voter_client.on_connect    = voter_connected
voter_client.on_disconnect = disconnected
voter_client.on_message = voter_message
voter_client.connect()
voter_client.loop_background()

while True:
    pass
