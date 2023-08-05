#!/usr/bin/python3
import sys
from mastodon import Mastodon
import datetime
from os.path import exists
import json
import time
import common

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

def follows_import(filename, config):
	try:
		with open(filename) as f:
			follows = json.load(f)
	except:
		print("error opening %s\n" % filename)
		return

	auth = common.auth(config["config_file"])
	follow_users(auth, follows)
	
def follows_export(filename, config):
	auth = common.get_auth(config["config_file"])
	follows = get_follows(auth)

	if filename is not None:
		with open(filename, 'w') as outfile:
			json.dump(follows, outfile, default=str)

	else:
		follow_users(auth, follows)


def main():
	
	config = common.get_args()
	mode = config["mode"]

	if (mode == "export"):
		follows_export(config["output_file"], config)

	elif (mode == "sync"):
		follows_export(None, config)

	elif (mode == "import"):
		follows_import(config["output_file"], config)

	else:
		print("unknown mode")


#start
main()
