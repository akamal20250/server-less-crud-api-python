import json
from custom_encoder import CustomEncoder
import boto3
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define DynamoDB table and resource using boto3.
dynamobdTableName = 'product-inventory'
dyanmo =  boto3.resource('dynamodb')
table =  dyanmo.Table(dynamobdTableName) 

# HTTP Methods and API paths used in the API. 
getMethod = 'GET'
postMethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'
healthPath = '/health'
productPath = '/product'
productsPath = '/products'


# ====================================================================
# Lambda Handler Function
# ====================================================================
# Entry point for Lambda. It parses the API Gateway event and routes the 
# request to the appropriate function based on HTTP method and resource path.
def lambda_handler(event, context):
    logger.info(event)
    htttpMethod = event['httpMethod']
    path = event['path']
    if htttpMethod == getMethod and path == healthPath:
        response = buildResponse(200)
    elif htttpMethod == getMethod and path == productPath:
        response = getProduct(event['queryStringParameters']['productId'])    
    elif htttpMethod == getMethod and path == productsPath:
        response = getProducts()
    elif htttpMethod == postMethod and path == productPath:
        response = saveProduct(json.loads(event['body'])) 
    elif htttpMethod == patchMethod and path == productPath:
        requestBody = json.loads(event['body'])
        response = modifyProduct(requestBody['productId'], requestBody['updateKey'], requestBody['updateValue']) 
    elif htttpMethod == deleteMethod and path == productPath:
        requestBody = json.loads(event['body'])
        response = deleteProduct(requestBody['productId'])
    else:
        response = buildResponse(404, 'Not Found')
    return response



# ====================================================================
# Function: getProduct
# ====================================================================
# Retrieves a single product from DynamoDB based on the provided productId.
def getProduct(productId):
    try:
        response = table.get_item(
            Key={
                'productId': productId
            }
        )
        if 'Item' in response:
            return buildResponse(200, response['Item'])
        else:
            return buildResponse(404, {'Message': 'ProductId %s not found' % productId})
    except:
        logger.exception('Error while getting product')


# ====================================================================
# Function: getProducts
# ====================================================================
# Scans the entire DynamoDB table to retrieve all products. Handles pagination
# if the dataset exceeds a single scan limit.
def getProducts():
    try:
        response = table.scan()
        result = response['Items']

        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            result.extend(response['Items'])

        body = {
            'products': result
        }
        return buildResponse(200, body)
    except:
        logger.exception('Error while getting products')


# ====================================================================
# Function: saveProduct
# ====================================================================
# Saves a new product item to the DynamoDB table using data provided in the request body.
def saveProduct(requestBody):
    try:
        table.put_item(Item=requestBody)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return buildResponse(200, body)
    except:
        logger.exception('Error while saving product')  



# ====================================================================
# Function: modifyProduct
# ====================================================================
# Updates an existing product item in the DynamoDB table based on productId.
# It updates a specified key with a new value provided in the request body.
def modifyProduct(productId, updateKey, updateValue):
    try:
        response = table.update_item(  
            Key={
                'productId': productId
            },
            UpdateExpression='set %s = :value' % updateKey,
            ExpressionAttributeValues={
                ':value': updateValue
            },
            ReturnValues='UPDATED_NEW'
        )
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdatedAttributes': response
        }
        return buildResponse(200, body)
    except:
        logger.exception('Error while updating product')



# ====================================================================
# Function: deleteProduct
# ====================================================================
# Deletes a product from the DynamoDB table based on the provided productId.
def deleteProduct(productId):
    try:
        response = table.delete_item(
            Key={
                'productId': productId
            },
            ReturnValues='ALL_OLD'
        )
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem': response
        }
        return buildResponse(200, body)
    except:
        logger.exception('Error while deleting product')




# ====================================================================
# Function: buildResponse
# ====================================================================
# Constructs and returns a formatted HTTP response with appropriate headers,
# status code, and JSON-encoded body.
def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls = CustomEncoder)
    return response