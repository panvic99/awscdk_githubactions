import boto3
import uuid
import os
import json
                
def handler(event, context):
    
    return {'statusCode': 200, 'body': f'Hello from Lambda! name : {event} '}