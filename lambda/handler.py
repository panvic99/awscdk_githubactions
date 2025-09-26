import boto3
import uuid
import os
import json
import requests

dynamo = None
table = None
dest_lambda_url = None

def handler(event, context):
    global dynamo, table, dest_lambda_url
    try:
        if dynamo is None:
            dynamo = boto3.resource('dynamodb')
        if table is None:
            table = dynamo.Table(os.environ['TABLE_NAME'])
        if dest_lambda_url is None:
            dest_lambda_url = os.environ['DEST_LAMBDA']
        # dynamo = boto3.resource('dynamodb')
        # table = dynamo.Table(os.environ['TABLE_NAME'])
        # dest_lambda_url = os.environ['DEST_LAMBDA']
        if 'Records' in event:
            # S3 trigger
            for record in event['Records']:
                bucket_name = record['s3']['bucket']['name']
                object_key = record['s3']['object']['key']
                
                item = {
                    'id': str(uuid.uuid4()),
                    'trigger': 'S3',
                    'bucket': bucket_name,
                    'file': object_key
                }
                try:
                    response = table.put_item(Item=item)
                except:
                    print(f'Error writing to DynamoDB: {item}')
            
            return {'statusCode': 200, 'body': 'S3 upload processed and event:{event}'}
    
    
        else:
            params = event.get('queryStringParameters', {})
            name = params.get('name', 'Unknown')
            age = params.get('age', '0')
            dest_lambda = params.get('lambda', '0')
            
            if dest_lambda == '0':
                id = str(uuid.uuid4())
                
                item = {
                    'trigger': 'HTTP',
                    'id': id,
                    'name': name,
                    'age': age
                }

                table.put_item(Item=item)
                response = table.get_item(Key={'id': id})

                return {'statusCode': 200, 'body': f'Hello from Lambda! name : {name} data from db {json.dumps(response["Item"])}  '}
            else:
                try:
                    response = requests.get(
                        dest_lambda_url,
                        # params={
                        #     'name': name,
                        #     'age': age,
                        #     'source': 'lambda1'
                        # },
                        # timeout=30
                    )
                    
                    return {
                        'statusCode': 200,
                        'body': f'Lambda1 called Lambda2. Response: {response.text}'
                    }
                    
                except requests.exceptions.RequestException as e:
                    return {
                        'statusCode': 500,
                        'body': f'Error calling Lambda2: {str(e)}'
                    }
            
    except Exception as e:
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}
