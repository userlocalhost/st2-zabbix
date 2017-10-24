#!/usr/bin/env python
import sys

from optparse import OptionParser
from zabbix.api import ZabbixAPI
from pyzabbix.api import ZabbixAPIException
from urllib2 import URLError

# This constant describes 'script' value of 'type' property in the MediaType,
# which is specified in the Zabbix API specification.
SCRIPT_MEDIA_TYPE = '1'

# This is a constant for the metadata of MediaType to be registered
ST2_DISPATCHER_SCRIPT = 'st2_dispatch.py'


def get_options():
    parser = OptionParser()

    parser.add_option('-z', '--zabbix-url', dest="z_url",
                      help="The URL of Zabbix Server")
    parser.add_option('-u', '--username', dest="z_userid", default='Admin',
                      help="Login username to login Zabbix Server")
    parser.add_option('-p', '--password', dest="z_passwd", default='zabbix',
                      help="Password which is associated with the username")

    (options, args) = parser.parse_args()

    if not options.z_url:
        parser.error('Zabbix Server URL is not given')

    return (options, args)

def is_already_registered(client, options):
    """
    This method checks target MediaType has already been registered, or not.
    """
    for mtype in client.mediatype.get():
        if mtype['type'] == SCRIPT_MEDIA_TYPE and mtype['exec_path'] == ST2_DISPATCHER_SCRIPT:
            return True

    return False

def register_media_type(client, options):
    """
    This method registers a MediaType which dispatches alert to the StackStorm.
    """
    mediatype_args = [
        '-- CHANGE ME : hostname or IP address of StackStorm ---',
        '-- CHANGE ME : login uername of StackStorm ---',
        '-- CHANGE ME : login password of StackStorm ---',
        '{ALERT.SENDTO}',
        '{ALERT.SUBJECT}',
        '{ALERT.MESSAGE}',
    ]

    # send request to register a new MediaType for StackStorm
    client.mediatype.create({
        'description': 'StackStorm',
        'type': SCRIPT_MEDIA_TYPE,
        'exec_path': ST2_DISPATCHER_SCRIPT,
        'exec_params': "\n".join(mediatype_args) + "\n",
    })

def main():
    (options, _) = get_options()

    try:
        client = ZabbixAPI(url=options.z_url,
                           user=options.z_userid,
                           password=options.z_passwd)
    except URLError as e:
        print('Failed to connect Zabbix server (%s)' % e)
        return 1
    except ZabbixAPIException as e:
        print('Failed to authenticate Zabbix (%s)' % e)
        return 1

    if not is_already_registered(client, options):
        register_media_type(client, options)
        print('New MediaType for StackStorm is registered successfully.')
        return 0
    else:
        print('A MediaType for StackStorm has been already registered.')
        return 1

if __name__ == '__main__':
    exit_code = main()

    sys.exit(exit_code)
