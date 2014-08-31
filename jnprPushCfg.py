#!/usr/bin/env python

from __future__ import print_function
from getpass import *
import argparse, sys

try:
	from jnpr.junos import Device
	from jnpr.junos.utils.config import Config
	from jnpr.junos.exception import *
except:
	print('ERROR: junos-eznc module not found!')
	exit()

#Default settings
defaults = {
	'port': '830',
	'devices': [],
	'config_file': '',
	'user': '',
	'password': '',
	'ssh_key': ''
}

def parse_arguments(arguments):
    parser = argparse.ArgumentParser(description="Utility to push configurations to Junos devices")
    parser.add_argument("-d", "--device", help="Device to apply configuration to")
    parser.add_argument("config", help="Config file to apply")
    parser.add_argument("-l", "--device-list", help="File containing list of devices to apply configuration to")
    parser.add_argument("-u", "--user", help="Username to login to device")
    parser.add_argument("-p", "--password", action='store_true', help="Prompt for password to login to device")
    parser.add_argument("-c", "--confirm", action='store_true', help="Auto confirm configuration changes (No diff review)")
    parser.add_argument("-P", "--port", help="Netconf port to connect on")
    args = parser.parse_args()
    return args

def get_device_list(file):
	try:
		devices = [line.strip() for line in open(file, 'r')]
		return devices
	except IOError:
		print("ERROR: Unable to read devices from file")
		exit()

#Process command line arguments
args = parse_arguments(sys.argv)

#Set Netconf port to connect on
if args.port:
	port = args.port
elif defaults['port'] != '':
	port = defaults['port']
else:
	port = '830'

#Set user to connect as
if args.user is True:
	user = args.user
elif defaults['user'] != '':
	user = defaults['user']
else:
	user = getuser()

#Set password for connecting
if args.password is True:
	password = getpass('Password for %s: ' % user)
elif defaults['password'] != '':
	password = defaults['password']
else:
	password = ''

#Generate device list
if args.device:
	devices = [args.device]
elif args.device_list:
	devices = get_device_list(args.device_list)
elif defaults['devices'] != []:
	devices = defaults['devices']
else:
	print("ERROR: No device(s) specified")
	exit()

#Process devices
for device in devices:
	print('*** Processing %s ***' % device)
	
	# Create device instance and connect to device prepped for config
	dev = Device(device, user=user, password=password, port=port, ssh_private_key_file=defaults['ssh_key'])
	# dev = Device(device)
	
	#Make connection to device
	try:
		dev.open()
	except ConnectError:
		print("ERROR: Unable to connect")
		continue

	#Bind config utility instance to device
	dev.bind(cfg=Config)

	#Lock device's config
	print("Locking configuration")
	try:
		dev.cfg.lock()
	except LockError:
		print('ERROR: Failed to lock configuration')
		continue

	#Apply config
	print("Pushing configuration")
	try:
		dev.cfg.load(path=args.config, format='text')
	except RpcError:
		print("ERROR: Failed to push configuration")
		continue

	#Verify config (commit check)
	print("Verifying configuration")
	commit_check = dev.cfg.commit_check()

	#If check is successful, prmompt user to commit or auto-commit based on CLI parameters
	if commit_check is True:
		if args.confirm is True:
			print("Confirmation bypassed")
			print("Rolling back")
			dev.cfg.rollback()
			dev.close()
		else:
			print('The following changes will be applied:')
			diff = dev.cfg.pdiff()
			commit_config = ''
			while commit_config != 'YES' and commit_config != 'NO':
				commit_config = raw_input('Apply configuration (YES/NO): ')
				if commit_config == 'YES':
					print("Committing")
					rsp = dev.cfg.commit()
					if rsp is True:
						print("Commit successfull")
						dev.close()
					else:
						print("Commit failed")
						dev.close()
				elif commit_config == 'NO':
					print("Rolling back")
					dev.cfg.rollback()
					dev.close()
	else:
		print("ERROR: Config verification failed")
		dev.close()
