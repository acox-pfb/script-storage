#!/usr/bin/python
"""
API call to next time teh ISS is over Houston
"""
import requests
parameters = {"lat": 29.76, "lon": -95.37} # Houston

# Make a get request with the parameters.
response = requests.get("http://api.open-notify.org/iss-pass.json", params=parameters)

# Print the content of the response (the data the server returned)
print(response.content)

# This gets the same data as the command above
#response = requests.get("http://api.open-notify.org/iss-pass.json?lat=40.71&lon=-74")
#print(response.content)
