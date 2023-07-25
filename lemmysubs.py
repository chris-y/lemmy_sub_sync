#!/usr/bin/python3
import sys
from pythorhead import Lemmy
import datetime
from os.path import exists
import json
import urllib.parse
import time
import pyotp
import common

def lemmy_login(userauth):
	if userauth["type"] == "lemmy":
		lemmy = Lemmy(userauth["instance"])
		ok = lemmy.log_in(userauth["username"], userauth["password"])

		if ok is False:
			print("Retrying with TOTP code")
			totp = pyotp.TOTP(userauth["totp"], digest="SHA256")
			ok = lemmy.log_in(userauth["username"], userauth["password"], totp.now())
			if ok is False:
				print("error logging in")
				return None

		return lemmy
	return None


def sub_to_communities(auth, subs):
	for user in auth:
		lemmy = lemmy_login(auth[user])
		if lemmy is None:
			continue

		for sub in subs:
			#print(sub)
			url = urllib.parse.urlparse(sub["community"]["actor_id"])
			comm_name = sub["community"]["name"] + "@" + url.netloc
			for attempt in range(10):
				print("Finding %s..." % comm_name)
				comm = lemmy.discover_community(comm_name)
				print(comm)
				if comm:
					break;
				else:
					print("Waiting 10 secs...")
					time.sleep(10)
					continue

			for attempt in range(10):
				print("Subbing to %s..." % comm_name)
				ok = lemmy.community.follow(id = comm)

				if ok:
					break
				else:
					print("Waiting 10 secs...")
					time.sleep(10)
					continue

			if ok:
				print("done\n")
			else:
				print("FAILED\n")


			time.sleep(0.1)
			
def get_subs(auth):
	subs = []

	for user in auth:
		lemmy = lemmy_login(auth[user])
		if lemmy is None:
			continue

		print("Getting subs for user %s\n" % user)

		subpg = [ 0 ]
		pg = 1

		while subpg:
			subpg = lemmy.community.list(type_ = "Subscribed", page = pg)
			subs.extend(subpg)
			print(pg)
			pg += 1
	
	return subs
	

def subs_import(filename):
		try:
			with open(filename) as f:
				subs = json.load(f)
		except:
			print("error opening %s\n" % filename)
			return

		auth = common.get_auth()

		sub_to_communities(auth, subs)

def subs_export(filename):
	auth = common.get_auth()
	subs = get_subs(auth)

	if filename is not None:
		with open(filename, 'w') as outfile:
			json.dump(subs, outfile)
	else:
		sub_to_communities(auth, subs)

def main():
	
	mode = sys.argv[1]

	try:
		filename = sys.argv[2]
	except:
		filename = "./lemmysubs_export.json"


	if (mode == "export"):
		subs_export(filename)

	elif (mode == "sync"):
		subs_export(None)

	elif (mode == "import"):
		subs_import(filename)
		
	else:
		print("unknown mode")

#start
main()
