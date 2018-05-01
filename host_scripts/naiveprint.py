from escpos.printer import Usb
from Adafruit_IO import MQTTClient
import time
import json

#p = Usb(0x456, 0x0808, 0, 0x81, 0x03)

def vote_connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print('Connected to Adafruit IO!  Listening for DemoFeed changes...')
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe('vote')

def voter_connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print('Connected to Adafruit IO!  Listening for DemoFeed changes...')
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe('vote')

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print(payload)
    #p.text(payload)
    #p.cut()


ADAFRUIT_IO_KEY      = '8341795c01774027901eae1c9f822f2d'
ADAFRUIT_IO_USERNAME = 'ogreatfox'

voter_feed = "voter"
vote_feed = "vote"

client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
client.on_connect    = vote_connected
client.on_disconnect = disconnected
client.on_message = message
client.connect()
client.loop_background()


while True:
    #client.publish('vote', "WOOF")
    pass
