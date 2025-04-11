# Serverless CRUD API with AWS Lambda, API Gateway, and DynamoDB

## Overview
This project is a serverless CRUD (Create, Read, Update, Delete) API developed using AWS Lambda, API Gateway, and DynamoDB. The API allows you to manage a simple product inventory. It supports:
- **GET**: Retrieve product details or a list of products.
- **POST**: Add a new product to the inventory.
- **PATCH**: Update an existing product.
- **DELETE**: Remove a product from the inventory.
- **/health**: A simple health-check endpoint.

## Architecture
The architecture consists of:
- **AWS Lambda**: Hosts the Python-based CRUD operations.
- **API Gateway**: Provides RESTful endpoints with Lambda proxy integration.
- **DynamoDB**: A NoSQL database used for storing product information.
- **IAM Role**: Grants the necessary permissions to Lambda to interact with DynamoDB and CloudWatch.

A detailed architectural diagram is available in the [`docs/crud-api-architectural-diagram.png`](docs/crud-api-architectural-diagram.png) file.

## Technologies Used
- **AWS Lambda**: for serverless function execution.
- **AWS API Gateway**: for exposing REST endpoints.
- **AWS DynamoDB**: for data persistence.
- **Python 3.13**: for writing the Lambda function.
- **Boto3**: AWS SDK for Python.
- **CloudWatch**: for logging and monitoring.


## Project Structure
<pre>
```plaintext
serverless-crud-api-python/
├── README.md              # Project overview & instructions
├── lambda_function.py     # Main Lambda function implementing CRUD operations
├── custom_encoder.py      # Custom JSON encoder for DynamoDB Decimal types
├── docs/
│   ├── crud-api-architectural-diagram.png      # AWS architecture diagram
│   ├── crud-api-architectural-diagram.pdf      # AWS architecture diagram
│   └── serverless-api-prod-oas30-postman.yaml  # API Gateway OpenAPI export
└── config/
    └── deployment_instructions.txt         # Additional deployment notes
```
</pre>



## How It Works
1. **Lambda Function Code**  
   - The function uses **boto3** to connect to the DynamoDB table `product-inventory`.  
   - HTTP methods and resource paths are mapped to specific Python functions:
      - **/health (GET):** Returns a basic 200 response.
      - **/product (GET, POST, PATCH, DELETE):** Handles individual product operations.
      - **/products (GET):** Scans and returns all products (handles pagination).
   - **Custom JSON Encoder:**  
     The `CustomEncoder` class converts DynamoDB Decimal types to float for JSON serialization.
   

   # Lambda handler function that routes incoming requests based on HTTP method and path.
   <pre>
```plaintext
   def lambda_handler(event, context):
       logger.info(event)
       htttpMethod = event['httpMethod']
       path = event['path']
       # Health check endpoint
       if htttpMethod == getMethod and path == healthPath:
           response = buildResponse(200)
       # Retrieve a single product by productId via GET /product?productId=...
       elif htttpMethod == getMethod and path == productPath:
           response = getProduct(event['queryStringParameters']['productId'])    
       # Retrieve all products with GET /products
       elif htttpMethod == getMethod and path == productsPath:
           response = getProducts()
       # Save new product via POST /product with JSON body
       elif htttpMethod == postMethod and path == productPath:
           response = saveProduct(json.loads(event['body'])) 
       # Update product using PATCH /product with JSON body containing productId, updateKey, updateValue
       elif htttpMethod == patchMethod and path == productPath:
           requestBody = json.loads(event['body'])
           response = modifyProduct(requestBody['productId'], requestBody['updateKey'], requestBody['updateValue']) 
       # Delete product using DELETE /product with JSON body containing productId
       elif htttpMethod == deleteMethod and path == productPath:
           requestBody = json.loads(event['body'])
           response = deleteProduct(requestBody['productId'])
       else:
           response = buildResponse(404, 'Not Found')
       return response
```
</pre>






