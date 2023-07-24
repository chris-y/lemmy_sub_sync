#!/usr/bin/python3
import sys
from mastodon import Mastodon
import datetime
from os.path import exists
import json
import urllib.parse
import time
import pyotp

def mast_login(userauth):

	if userauth["type"] == "mastodon":
		mastodon = Mastodon(
			access_token = userauth["token"],
			api_base_url = userauth["instance"]
		)

		return mastodon
	else:
		return None


def follow_users(auth, follows):
	for user in auth:
		mastodon = mast_login(auth[user])
		if mastodon is None:
			continue

		me = mastodon.me()

		for user in follows:
			print("Following %s" % user["acct"])

			search = mastodon.account_search(user["acct"])
			for result in search:
				# ensure it matches
				if(result["acct"] == user["acct"]):
					ok = mastodon.account_follow(result["id"])

			if ok:
				print("done\n")
			else:
				print("FAILED\n")


			time.sleep(0.1)
			
def get_follows(auth):
	follows = []

	for user in auth:
		mastodon = mast_login(auth[user])
		if mastodon is None:
			continue

		print("Getting follows for user %s\n" % user)

		me = mastodon.me()
		
		accfollows = mastodon.account_following(me["id"])
		follows.extend(accfollows)
	
	return follows
	
	
def main():
	
	mode = sys.argv[1]

	with open("./.lemmysubauth.json") as f:
		auth = json.load(f)

	try:
		filename = sys.argv[2]
	except:
		filename = "./mastusers_export.json"


	if (mode == "export") or (mode == "sync"):

		follows = get_follows(auth)

		if mode == "export":
		
			with open(filename, 'w') as outfile:
				json.dump(follows, outfile, default=str)

		elif mode == "sync":
			follow_users(auth, follows)

	elif (mode == "import"):
		try:
			with open(file) as f:
				follows = json.load(f)
		except:
			print("error opening %s\n" % file)
			return

		follow_users(auth, follows)

#start
main()
