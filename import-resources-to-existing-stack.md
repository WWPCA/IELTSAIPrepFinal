# Import Existing Resources to CloudFormation Stack

## Import Strategy for aws-sam-cli-managed-default Stack

### Current Resources to Import
Based on your existing infrastructure:

1. **Lambda Function**: Your IELTS GenAI Prep Lambda function
2. **API Gateway**: REST API with ID `n0cpf1rmvc`
3. **API Gateway Deployment & Stage**: prod stage
4. **IAM Roles**: Lambda execution role with required permissions

### Import Process via AWS Console

#### Step 1: Prepare CloudFormation Template for Import
Create a simplified template that matches your existing resources:

```yaml
# Simplified template for importing existing resources
Resources:
  ExistingLambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: [Your actual Lambda function name]
      
  ExistingApiGateway:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: [Your actual API name]
      
  ExistingApiDeployment:
    Type: AWS::ApiGateway::Deployment
    Properties:
      RestApiId: !Ref ExistingApiGateway
      
  ExistingApiStage:
    Type: AWS::ApiGateway::Stage
    Properties:
      RestApiId: !Ref ExistingApiGateway
      DeploymentId: !Ref ExistingApiDeployment
      StageName: prod
```

#### Step 2: Update Stack with Resource Import
1. In CloudFormation console, click "Update stack"
2. Choose "Replace current template"
3. Upload the import template
4. Select "Import resources into stack"
5. Specify the resource identifiers for each resource

#### Step 3: Add Route 53 and SSL Certificate
After importing existing resources, add new resources:
- Route 53 hosted zone
- SSL certificate with DNS validation
- Custom domain configuration
- Health checks

### Benefits of This Approach
- Keeps existing working infrastructure
- Centralizes management in CloudFormation
- Enables infrastructure as code going forward
- Simplifies future updates and scaling

### Resource Identifiers Needed
To import resources, we need:
- Lambda function ARN
- API Gateway REST API ID (n0cpf1rmvc)
- IAM role ARN
- Any other existing resource identifiers