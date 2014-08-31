jnprPushCfg
===========

Utility to push configuration files to Junos devices using Netconf


## FEATURES
* Update configuration on remote Junos devices using text configs (curly brace format)
* View diff (show|compare) before committing changes or override confirmation from command line
* Input list of devices to update from file or python list
* SSH private key and password authentication

## REQUIREMENTS
* Tested on python2.7
* junos-pyez library (https://github.com/Juniper/py-junos-eznc)

## USAGE

````
usage: jnprPushCfg.py [-h] [-d DEVICE] [-l DEVICE_LIST] [-u USER] [-p] [-c]
                      [-P PORT]
                      config

Utility to push configurations to Junos devices

positional arguments:
  config                Config file to apply

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
                        Device to apply configuration to
  -l DEVICE_LIST, --device-list DEVICE_LIST
                        File containing list of devices to apply configuration
                        to
  -u USER, --user USER  Username to login to device
  -p, --password        Prompt for password to login to device
  -c, --confirm         Auto confirm configuration changes (No diff review)
  -P PORT, --port PORT  Netconf port to connect on
````
