import boto3

def fix_cors_api():
    apigateway = boto3.client('apigateway')
    api_id = 'cn4yjqa6ni'  # Your API Gateway ID
    
    # Get resources
    resources = apigateway.get_resources(restApiId=api_id)
    
    # Find the /query resource
    query_resource_id = None
    for resource in resources['items']:
        if resource.get('pathPart') == 'query':
            query_resource_id = resource['id']
            break
    
    if not query_resource_id:
        print("Query resource not found")
        return
    
    # Add OPTIONS method for CORS preflight
    try:
        apigateway.put_method(
            restApiId=api_id,
            resourceId=query_resource_id,
            httpMethod='OPTIONS',
            authorizationType='NONE'
        )
        print("Added OPTIONS method")
    except:
        print("OPTIONS method already exists")
    
    # Add OPTIONS integration
    apigateway.put_integration(
        restApiId=api_id,
        resourceId=query_resource_id,
        httpMethod='OPTIONS',
        type='MOCK',
        requestTemplates={
            'application/json': '{"statusCode": 200}'
        }
    )
    
    # Add OPTIONS method response
    apigateway.put_method_response(
        restApiId=api_id,
        resourceId=query_resource_id,
        httpMethod='OPTIONS',
        statusCode='200',
        responseParameters={
            'method.response.header.Access-Control-Allow-Headers': False,
            'method.response.header.Access-Control-Allow-Methods': False,
            'method.response.header.Access-Control-Allow-Origin': False
        }
    )
    
    # Add OPTIONS integration response
    apigateway.put_integration_response(
        restApiId=api_id,
        resourceId=query_resource_id,
        httpMethod='OPTIONS',
        statusCode='200',
        responseParameters={
            'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
            'method.response.header.Access-Control-Allow-Methods': "'GET,POST,OPTIONS'",
            'method.response.header.Access-Control-Allow-Origin': "'*'"
        }
    )
    
    # Update POST method response to include CORS headers
    try:
        apigateway.put_method_response(
            restApiId=api_id,
            resourceId=query_resource_id,
            httpMethod='POST',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Origin': False
            }
        )
    except:
        pass
    
    # Update POST integration response
    try:
        apigateway.put_integration_response(
            restApiId=api_id,
            resourceId=query_resource_id,
            httpMethod='POST',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Origin': "'*'"
            }
        )
    except:
        pass
    
    # Deploy the changes
    apigateway.create_deployment(
        restApiId=api_id,
        stageName='prod'
    )
    
    print("CORS configuration updated and deployed!")
    print("API should now work with web browsers")

if __name__ == "__main__":
    fix_cors_api()