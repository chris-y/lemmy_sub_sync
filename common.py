#!/usr/bin/python3
import sys
import json
import argparse

def get_auth(auth_file):
	with open(auth_file) as f:
		auth = json.load(f)

	return auth

def get_args():
	parser = argparse.ArgumentParser(description="Fediverse sync tool",
		formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("-c", "--config-file", help="config file", default="./.fedisync_auth.json")
	parser.add_argument("-m", "--mode", help="mode - export/sync/import", default="export")
	parser.add_argument("-o", "--output-file", help="output file", default="./fedisync_export.json")
	args = parser.parse_args()
	config = vars(args)

	return(config)
