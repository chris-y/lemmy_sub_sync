#!/usr/bin/python3
import sys
import json

def get_auth():
	with open("./.lemmysubauth.json") as f:
		auth = json.load(f)

	return auth
