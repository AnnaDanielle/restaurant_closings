"""
Module to perform post and get functions on Yelp API.
"""

from urllib import urlencode
from db_creds import fusion_creds, v_2_creds
import requests

def obtain_bearer_token():
	"""
	Provide the bearer token through an API post request.

	"""
	url = 'https://api.yelp.com/oauth2/token'
	data = urlencode({'client_id': fusion_creds['app_id'],
					  'client_secret': fusion_creds['app_secret'],
                  	  'grant_type': 'client_credentials'})
	headers = {'content-type': 'application/x-www-form-urlencoded'}

	response = requests.post(url, data, headers)

	bearer_token = response.json()['access_token'].encode('ascii')

	if response.status_code == 200:
		return bearer_token

def make_req():
	"""
	Make a post request to Yelp API.

	Parameters:
	-----------
	url : provide the domain of the host API and the path of 
	the API after the domain

    	data : dictionary object containing client id, client
    	secret, and grant type (which is 'client_credentials')

	"""	
