import requests
r = requests.post("http://172.27.98.179:5000/ballot", data={'foo': 'bar'})
# And done.
print(r.text) # displays the result body.
