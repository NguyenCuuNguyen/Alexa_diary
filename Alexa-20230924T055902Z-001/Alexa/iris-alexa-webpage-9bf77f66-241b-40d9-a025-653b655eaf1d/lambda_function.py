import boto3
import json
import logging #use logger to traceback error, include aws_request_id for Insight query
import sys
from boto3.dynamodb.conditions import Key, Attr #To add conditions to scanning and querying the table
from jose.utils import base64url_decode
import ecdsa #Layer Structure: Zipped python/ecdsa/...
import re
import itertools

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('alexa_demo_table3')

def lambda_handler(event, context):
    #Extract user email from token
    token=str(event['headers']['Authorization'])
    decoded_token = base64url_decode(token.split('.')[1].encode("UTF-8")).decode('utf-8')  
  
    auth_str = decoded_token.lstrip('\'{').rstrip('\'}').split(',')
    auth_str = '[%s]'%', '.join(map(str, auth_str)) #remove str single quotes around pairs
    auth_str = auth_str.replace("[", "{").replace("]", "}")
    auth_dict = json.loads(auth_str) #convert to dict
    user_email = str(auth_dict["email"])

    response = ""
    user_date = str(event['body']['Date'])
    print(user_date)
    
    date_list = user_date.split(" - ")
    start_date = date_list[0].split("/")
    end_date = date_list[1].split("/")
    
    #reformat date into iso
    iso_start_date = "{}-{}-{}".format(start_date[2], start_date[0], start_date[1])
    iso_end_date = "{}-{}-{}".format(end_date[2], end_date[0], end_date[1])
    
    matched_id = table.query( #current user settings before update
            KeyConditionExpression=Key("email").eq(user_email) & Key('date').between(iso_start_date, iso_end_date),
            # ProjectionExpression="info_log, date"
    )
    
    response_list = []
    if not matched_id['Items']:
        response="User does not have any recorded entry. Please report via Alexa-enabled devices!"
        print(response)
    else:
        for item in matched_id['Items']:
            if len(item) != 2:
                info_log_dict = item['info_log']
                for i in info_log_dict:
                    i["date"] = item["date"] #inject date into each daily_log's dict
                response_list.append(info_log_dict)

        final = list(itertools.chain.from_iterable(response_list))
        response = final

    return {
        "statusCode": 200,
        'body': response
    }
 