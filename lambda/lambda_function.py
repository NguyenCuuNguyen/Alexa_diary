#RESTORE THIS VERSION FOR MY EXPENSE SKILL
#Step1: Add my expense skill ID to lambda's trigger
#Step2: Add lambda's ARN to my expense skill's endpoint

# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import boto3
import json
import sys
import os #to retrieve env variables passed to Lambda, i.e DynamoDB table's name to persist user data
import ask_sdk_core.utils as ask_utils
import datetime
import time
import requests


#from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response


#from ask_sdk_core.skill_builder import StandardSkillBuilder #ERROR: DynamoDB support, Default API client, user's device basic details
import os #to retrieve env variables passed to Lambda, i.e DynamoDB table's name to persist user data
from ask_sdk_dynamodb.adapter import DynamoDbAdapter
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.dispatch_components.request_components import AbstractRequestInterceptor 
from ask_sdk_core.dispatch_components.request_components import AbstractResponseInterceptor
from jose.utils import base64url_decode
import ecdsa #Layer Structure: Zipped python/ecdsa/...
#from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


db_region = os.environ.get('us-east-1')
dynamodb = boto3.resource('dynamodb', region_name=db_region)
table = dynamodb.Table('alexa_demo_table3')
dynamodb_adapter = DynamoDbAdapter(table_name=table, create_table=False, dynamodb_resource=dynamodb)

cognito_client = boto3.client("cognito-idp", region_name="us-east-1")
# auth_data = { 'USERNAME':username , 'PASSWORD':password }


def get_user_info(access_token): #access_token comes from cookie
    #print access_token
    amazonProfileURL = 'https://api.amazon.com/user/profile?access_token=' #2br
    r = requests.get(url=amazonProfileURL+access_token)
    if r.status_code == 200:
        return r.json()
    else:
        return False

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input) #determine if the class can process the incoming request.

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # extract persistent attributes, if they exist
        # attr = handler_input.attributes_manager.persistent_attributes
        # user_name = 'Name' in attr
        
        # if user_name:
        #     name = attr["Name"]
        #     speak_output = "Welcome back to My Report, {name}!".format(name=name) #" and on a scale from 1 to 5, how are you feeling today?"
            
        # else:
        speak_output = "Welcome to My Report! What's your name?" #" and on a scale from 1 to 5, how are you feeling today?"
        reprompt="What's your name again?"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots #request_envelope NOT requestEnvelope
        global global_user_name
        global_user_name = slots["Name"].value
       
        username ={
            'ID': slots["Name"].value
        }
 
        speak_output = "Hi {name}, How are you feeling today and rank it on the scale from 1 to 5?".format(name=global_user_name)
         
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output) #without ask, Alexa won't call the next function
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can report by saying a rating and your name! Let's try that"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can report your feelings or Help for details. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"
        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."
        reprompt_text = "Please ask again"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
        )
    
    
class ReportingHandler(AbstractRequestHandler):
    """Receive user JSON input and save into DynamoDB table"""
    def can_handle(self, handler_input):
        print("yup, it's triggered")
        return ask_utils.is_intent_name("ReportIntent")(handler_input)

    
    def handle(self, handler_input):
        print("yup, it's inside handle")
        #Fetching access token and uses that token to retrieve the user's profile.
        #Access the request in the HandlerInput object passed to the handler.
        #access_token = str(handler_input.request_envelope.context.system.cognito_access_token)
        
        
        access_token2 = str(handler_input.request_envelope.session.user.access_token)
        print("handler_input.request_envelope.session: ", str(handler_input.request_envelope.session))
        
        #Fetching for access token from Alexa Skill Kit API
        endpoint = "https://sn83xpfcp4.execute-api.us-east-1.amazonaws.com/test/v2/accounts/~current/settings/Profile.email"
        api_access_token = "Bearer " + access_token2 
        headers = {"Authorization": api_access_token}
        r = requests.get(endpoint, headers=headers)
    
        user_email = r.json()
        decoded_token = base64url_decode(user_email['message'].split('.')[1].encode("UTF-8")).decode('utf-8') 
      
        
        auth_dict = json.loads(decoded_token)
        #alexa_user_id = auth_dict["privateClaims"]["userId"]
        response = cognito_client.get_user(
            AccessToken=access_token2
        )
        # print(response["UserAttributes"])
        for item in response["UserAttributes"]:
            if item['Name'] == 'email':
                user_email = item['Value'] 
        print(user_email)
        
        
        slots = handler_input.request_envelope.request.intent.slots 
        feeling = slots["Feeling"].value
        rating = int(slots["Number"].value)
        if rating <= 3:
            rating = str(rating)
            speak_output = 'I’m sorry to hear that. {rating} for {feeling} have been updated'.format(rating=rating, feeling=feeling)
        elif rating <= 5:
            rating = str(rating)
            speak_output = 'Great! I logged {rating} for {feeling}'.format(rating=rating, feeling=feeling)
        #print(feeling + " " + rating)
        reprompt_text= "Sorry I don't understand. How are you feeling on the scale of 5?"
        
        
        local_now = datetime.datetime.now()
        #time2 = local_now.strftime('date: %Y-%m-%d time: %H:%M:%S')
        time2 = local_now.strftime('%Y-%m-%d %H:%M:%S') #iso 8601 standard
        date_str=time2.split()[0] 
        time_str=time2.split()[1] 
    
        #Create info_logs:
        info_log_dict={
            "feeling": feeling,
            "rating" :rating,
            "time": time_str
        }
        
        try:
            #Query first to see if entry exists, if not, create it, else update
            user_status = table.query( #current user settings before update
                KeyConditionExpression=Key("email").eq(user_email) & Key("date").eq(date_str),
                ProjectionExpression="info_log"
            )
            print("user_status ", user_status)
            
            if user_status["Items"] == [] or user_status["Items"] == [{}]:
                print("The problem is info_log for this date is not created yet")
            #     table.put_item(
            #         Item={'email':user_email,'date':str(date_str), 'info_log': []}
            #     )
            
            table.update_item(
                    Key={
                        "email": user_email,
                        "date": str(date_str)
                    },
                    UpdateExpression= "SET info_log = list_append(if_not_exists(info_log, :empty_list), :i)",  
                    ExpressionAttributeValues={
                        ":i": [info_log_dict],
                        ":empty_list": [] 
                    },
                    ReturnValues="UPDATED_NEW"
                )
            
            
        except Exception as e:
            print(e)
            speak_output = "Unable to save the information"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
        )



class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        #logger.error(exception, exc_info=True)
        print(exception)
        speak_output = "Sorry I don't understand. What's your name?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# def lambda_handler(event, context):
#     print(event)
    #Fetching access token
    #access_token = str(handler_input.request_envelope.context.system.cognito_access_token)
    

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = CustomSkillBuilder(persistence_adapter=dynamodb_adapter)

sb.add_request_handler(LaunchRequestHandler())

sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(ReportingHandler())

sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()