from aws_cdk import (
    core,
    aws_apigateway as apigateway,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_sns as sns,
    aws_events as events,
    aws_events_targets as targets,
    aws_s3 as s3,
    aws_logs as logs
)

import os, json
import subprocess

def subprocess_cmd(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    proc_stdout=process.communicate()[0].strip()
    print(proc_stdout.decode("utf-8"))

class ImpressionsStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here

        region = os.environ['CDK_DEFAULT_REGION']
        awsaccountnumber = os.environ['CDK_DEFAULT_ACCOUNT']


        dynamodbtable = dynamodb.Table(self, 
                                    "dynamotable"+id,
                                    table_name='impressions',
                                    partition_key=dynamodb.Attribute(name='id', type=dynamodb.AttributeType.STRING)
                                    )
        
        lambda_role = iam.Role(self, 
                                "lambda"+id,
                                assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                                managed_policies=[
                                    iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
                                ],
                                role_name = "impressions-lambda-role"
                                )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=['dynamodb:Query',
                        'dynamodb:GetItem',
                        'dynamodb:PutItem',
                        'dynamodb:UpdateItem'
                        ],
                resources=[
                        f"arn:aws:dynamodb:{region}:{awsaccountnumber}:table/{dynamodbtable.table_name}",
                        f"arn:aws:dynamodb:{region}:{awsaccountnumber}:table/{dynamodbtable.table_name}/*"
                ],
                sid='AllowDynamoDBPolicy'
            )
        )

        layerdirectory = './layer_fastapi_requirements'
        if not os.path.isdir(layerdirectory):
            subprocess_cmd("Echo 'Building python layers'; ./build_python_requirements.sh")
        layerpython = lambda_.LayerVersion(self,
                                            "layerfastapipython"+id,
                                            code=lambda_.Code.from_asset(layerdirectory),
                                            compatible_runtimes=[lambda_.Runtime.PYTHON_3_8],
                                            description='Layer consisting of fastapi, magnum, etc'
                                            )
            
        environmentvar = dict()
        environmentvar['LOGGERLEVEL'] = '10'
        environmentvar['DYNAMODB_TABLE'] = dynamodbtable.table_name

        impressions_lambda = lambda_.Function(self,
                                                "impressionslambda"+id,
                                                code=lambda_.InlineCode(code=' ').from_asset('./src/'),
                                                description="Lambda to insert records and get records",
                                                handler='lambda_function.handler',
                                                role=lambda_role,
                                                environment=environmentvar,
                                                memory_size=128,
                                                timeout=core.Duration.seconds(120),
                                                runtime=lambda_.Runtime.PYTHON_3_8,
                                                retry_attempts=0,
                                                layers=[layerpython],
                                                log_retention=logs.RetentionDays.ONE_WEEK,
                                                tracing=lambda_.Tracing.ACTIVE
                                                )
        
        api_version = 'v1'

        impressionsgw = apigateway.LambdaRestApi(self,
                                                    "impressionsgw"+id,
                                                    handler=impressions_lambda,
                                                    description="API to insert records and get records",
                                                    deploy=True,
                                                    deploy_options=apigateway.StageOptions(
                                                        stage_name = api_version,
                                                        tracing_enabled=True
                                                        )
                                                    )
        
        self.impressionsgw = f'https://{impressionsgw.rest_api_id}.execute-api.us-east-1.amazonaws.com/{api_version}'

        core.CfnOutput(
            self,
            "WebhookURL"+id,
            description='Endpoint to access the app',
            value=self.impressionsgw
        )

        self.api_id = impressionsgw.rest_api_id
        self.impressionsgw = impressionsgw