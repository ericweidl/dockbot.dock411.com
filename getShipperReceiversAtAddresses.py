from __future__ import print_function

import requests
import urllib
import boto3
import json

print('Loading function')


def lambda_handler(event, context):
    if (event['currentIntent']['slots']['have_docks'] != '1'):
        address = event['currentIntent']['slots']['bol_address']
        url = 'http://app-api-test.dock411.com/v2/addresses?address='
        headers = {'x-api-key': '<request_an_api_key_from_dock411>'}
        myResponse = requests.get(url + urllib.quote_plus(address), headers=headers)

        if (myResponse.ok):

            jData = json.loads(myResponse.content)

            shippers = []
            shippers.append(
                'I found the following companies and their docks near that address. Please use the number to indicate which dock you are going to.')
            shipper_ids = {}

            index = 1
            for dock in jData['docks']:
                shippers.append(format(index) + ': ' + dock['shipper_receiver_name'] + ' ' + dock['name'])
                key_name = 'dock' + format(index)
                shipper_ids[key_name] = dock['id']
                index += 1

            response = {
                'sessionAttributes': shipper_ids,
                'dialogAction': {
                    'type': 'ElicitSlot',
                    'intentName': 'CheckDock',
                    'slots': {
                        'bol_address': event['currentIntent']['slots']['bol_address'],
                        'have_docks': '1',
                        'dock_index': 'null',
                        'attributes': 'null',
                    },
                    'slotToElicit': 'dock_index',
                    'message': {
                        'contentType': 'PlainText',
                        'content': "\n".join(shippers)
                    }
                }
            }

            return response
        else:
            response = {
                'dialogAction': {
                    'type': 'Close',
                    'fulfillmentState': 'Fulfilled',
                    'message': {
                        'contentType': 'PlainText',
                        'content': 'Sorry, we are having computer problems. Give me a few minutes and try again'
                    }
                }
            }

            return response
    else:
        if (event['currentIntent']['slots']['attributes'] == 'null'):
            response = {
                'dialogAction': {
                    'type': 'ElicitSlot',
                    'intentName': 'CheckDock',
                    'slots': {
                        'bol_address': event['currentIntent']['slots']['bol_address'],
                        'have_docks': '1',
                        'dock_index': event['currentIntent']['slots']['dock_index'],
                        'attributes': 'null',
                    },
                    'slotToElicit': 'attributes',
                    'message': {
                        'contentType': 'PlainText',
                        'content': 'What do you want to know about it?'
                    }
                }
            }

            return response
        else:
            dock_index = event['currentIntent']['slots']['dock_index']
            key_name = 'dock' + dock_index
            dock_id = event['sessionAttributes'][key_name]
            url = 'http://app-api-test.dock411.com/v2/docks/' + dock_id + '?fields=*'
            headers = {'x-api-key': '<request_an_api_key_from_dock411>'}
            myResponse = requests.get(url, headers=headers)

            if (myResponse.ok):

                jData = json.loads(myResponse.content)

                dock_attributes = {}

                for k, v in jData['dock_summary'].iteritems():
                    dock_attributes[k] = v

                three_state_values_dict = {'G': 'good', 'Y': 'okay', 'R': 'bad'}
                two_state_values_dict = {'Y': '', 'N': ' not'}

                if event['currentIntent']['slots']['attributes'] == 'lighting':
                    content = str(dock_attributes['lighting_percent']) + '% of drivers say the lighting is ' + \
                              three_state_values_dict[dock_attributes['lighting']]
                elif event['currentIntent']['slots']['attributes'] == 'load time':
                    content = 'Drivers say the load time averages ' + dock_attributes['load_time'] + ' minutes'
                elif event['currentIntent']['slots']['attributes'] == 'wait time':
                    content = 'Drivers say the wait time averages ' + dock_attributes['wait_time'] + ' minutes'
                elif event['currentIntent']['slots']['attributes'] == 'unload time':
                    content = 'Drivers say the unload time averages ' + dock_attributes['unload_time'] + ' minutes'
                elif event['currentIntent']['slots']['attributes'] == 'restrooms available':
                    content = str(dock_attributes['restrooms_percent']) + '% of drivers say bathrooms are ' + \
                              two_state_values_dict[dock_attributes['restrooms']] + ' available'
                elif event['currentIntent']['slots']['attributes'] == 'debug':
                    content = "\n".join(dock_attributes)
                    content = (content[:900] + '..') if len(content) > 900 else content
                else:
                    content = str(dock_attributes['lighting_percent']) + '% of drivers say the lighting is ' + \
                              three_state_values_dict[dock_attributes['lighting']] + ', '
                    content += 'the average load time is ' + dock_attributes['load_time'] + ' minutes, '
                    content += 'average wait time is ' + dock_attributes['wait_time'] + ' minutes, '
                    content += 'average unload time is ' + dock_attributes['unload_time'] + ' minutes, and '
                    content += str(dock_attributes['restrooms_percent']) + '% of drivers say bathrooms are' + \
                               two_state_values_dict[dock_attributes['restrooms']] + ' available.'

                response = {
                    'dialogAction': {
                        'type': 'ElicitSlot',
                        'intentName': 'CheckDock',
                        'slots': {
                            'bol_address': event['currentIntent']['slots']['bol_address'],
                            'have_docks': '1',
                            'dock_index': event['currentIntent']['slots']['dock_index'],
                            'attributes': 'null',
                        },
                        'slotToElicit': 'attributes',
                        'message': {
                            'contentType': 'PlainText',
                            'content': content
                        }
                    }
                }
                return response

            else:
                response = {
                    'dialogAction': {
                        'type': 'Close',
                        'fulfillmentState': 'Fulfilled',
                        'message': {
                            'contentType': 'PlainText',
                            'content': 'whooops' + '+' + myResponse.raise_for_status()
                        }
                    }
                }

                return response

