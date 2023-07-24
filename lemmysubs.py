#!/usr/bin/python3
import sys
from pythorhead import Lemmy
import datetime
from os.path import exists
import json
import urllib.parse
import time
import pyotp

def lemmy_login(userauth):
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


def sub_to_communities(auth, subs):
	for user in auth:
		lemmy = lemmy_login(auth[user])
		if lemmy is None:
			return

		for sub in subs:
			#print(sub)
			url = urllib.parse.urlparse(sub["community"]["actor_id"])
			comm_name = sub["community"]["name"] + "@" + url.netloc
			for attempt in range(10):
				print("Finding %s..." % comm_name)
				comm = lemmy.discover_community(comm_name)

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
			

def main():
	
	mode = sys.argv[1]

	with open("./.lemmysubauth.json") as f:
		auth = json.load(f)

	try:
		file = sys.argv[2]
	except:
		file = "./lemmysubs_export.json"


	if (mode == "export") or (mode == "sync"):

		subs = []

		for user in auth:
			print("Getting subs for user %s\n" % user)

			lemmy = lemmy_login(auth[user])
			if lemmy is None:
				return

			subpg = [ 0 ]
			pg = 1

			while subpg:
				subpg = lemmy.community.list(type_ = "Subscribed", page = pg)
				subs.extend(subpg)
				print(pg)
				pg += 1

		if mode == "export":
			with open(file, 'w') as outfile:
				json.dump(subs, outfile)

		elif mode == "sync":
			sub_to_communities(auth, subs)

	elif (mode == "import"):
		try:
			with open(file) as f:
				subs = json.load(f)
		except:
			print("error opening %s\n" % file)
			return

		sub_to_communities(auth, subs)

#start
main()
