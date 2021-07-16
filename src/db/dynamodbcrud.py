import logging
import os
import boto3

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ParamValidationError, ClientError
from boto3.dynamodb.conditions import Attr


DYNAMODB = boto3.resource('dynamodb')

def put_item(tablename, item):
    TABLE = DYNAMODB.Table(tablename)
    if item == None:
        raise Exception
    response = TABLE.put_item(Item=item)
    insertresponse = dict()
    if response.get('ResponseMetadata'):
        insertresponse.update(response['ResponseMetadata'])
    else:
        insertresponse.update(response)
    insertresponse['dynamodblibstatus'] = 'inserted'
    return insertresponse

def get_item(tablename, item):
    try:
        TABLE = DYNAMODB.Table(tablename)
        response = TABLE.get_item(Key=item)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response['Item']