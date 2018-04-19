import requests
r = requests.post("http://172.27.98.73:5000/ballot", data={'voter': 'bar'})
# And done.
print(r.text) # displays the result body.
