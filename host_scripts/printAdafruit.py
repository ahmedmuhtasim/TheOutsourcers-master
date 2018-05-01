from escpos.printer import Usb
from Adafruit_IO import MQTTClient
import ast
import time
import json

#p = Usb(0x456, 0x0808, 0, 0x81, 0x03)

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
    #print(payload)
    d = ast.literal_eval(payload)
    for key in d.keys():
        print(key, ":", d[key])
        #p.text(' ' + key + ': ' + value + '\n')
    #p.image("voted.jpg")
    #p.cut()


def voter_message(client, feed_id, payload):
    print(payload)
    #p.text(payload)
    #p.qr(payload)
    #p.cut()




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
