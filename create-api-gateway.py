import boto3
import json

def create_api_gateway():
    apigateway = boto3.client('apigateway')
    lambda_client = boto3.client('lambda')
    
    # Create REST API
    api_response = apigateway.create_rest_api(
        name='FraudInvestigatorAPI',
        description='Natural language interface for fraud investigation'
    )
    
    api_id = api_response['id']
    print(f"Created API Gateway: {api_id}")
    
    # Get root resource
    resources = apigateway.get_resources(restApiId=api_id)
    root_id = resources['items'][0]['id']
    
    # Create /query resource
    resource_response = apigateway.create_resource(
        restApiId=api_id,
        parentId=root_id,
        pathPart='query'
    )
    
    resource_id = resource_response['id']
    
    # Create POST method
    apigateway.put_method(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='POST',
        authorizationType='NONE'
    )
    
    # Set up Lambda integration
    lambda_arn = 'arn:aws:lambda:us-east-1:214617963177:function:fraud-investigator'
    
    apigateway.put_integration(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='POST',
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
    )
    
    # Add Lambda permission for API Gateway
    lambda_client.add_permission(
        FunctionName='fraud-investigator',
        StatementId='api-gateway-invoke',
        Action='lambda:InvokeFunction',
        Principal='apigateway.amazonaws.com',
        SourceArn=f'arn:aws:execute-api:us-east-1:214617963177:{api_id}/*/*'
    )
    
    # Deploy API
    apigateway.create_deployment(
        restApiId=api_id,
        stageName='prod'
    )
    
    api_url = f'https://{api_id}.execute-api.us-east-1.amazonaws.com/prod/query'
    
    print(f"API Gateway URL: {api_url}")
    print("\nTest with curl:")
    print(f'curl -X POST {api_url} -H "Content-Type: application/json" -d \'{{"query": "Show me fraud summary"}}\'')
    
    return api_url

if __name__ == "__main__":
    create_api_gateway()