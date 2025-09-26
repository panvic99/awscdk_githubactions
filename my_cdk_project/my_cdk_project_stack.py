from aws_cdk import (
   Stack,
   aws_s3 as s3,RemovalPolicy, aws_dynamodb, aws_lambda, aws_s3_notifications
)
from constructs import Construct
import json

class MyCdkAppStack(Stack):
    def __init__(self, scope: Construct, id: str,config: dict, **kwargs):
        super().__init__(scope, id, **kwargs)

        env_name = config["environment"]

        
        with open(f"config/general.json") as f:
            config = json.load(f)


        # Create S3 bucket
        bucket = s3.Bucket(
            self, "MyBucket",
            bucket_name=config["bucket1"]+env_name,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,  # change to DESTROY for auto-cleanup
            auto_delete_objects=True
        )

        dest_bucket = s3.Bucket(
            self, "destBucket",
            bucket_name=config["bucket2"]+env_name,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,  # change to DESTROY for auto-cleanup
            auto_delete_objects=True
        )
         

       # DynamoDB Table
        table = aws_dynamodb.Table(
            self, "MyTable",
            table_name=config["DynamoTable"]+env_name,
            partition_key=aws_dynamodb.Attribute(name="id", type=aws_dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        lambda_fn_dest = aws_lambda.Function(
            self, "MyLambda_dest",
            runtime=aws_lambda .Runtime.PYTHON_3_9,
            handler="handler.handler",
            code=aws_lambda.Code.from_asset("lambda_dest"),
            environment={
                "TABLE_NAME": table.table_name,
                "BUCKET_NAME": bucket.bucket_name,
                "DEST_BUCKET_NAME": dest_bucket.bucket_name
            }
        )

        dest_func_url = lambda_fn_dest.add_function_url(
            auth_type=aws_lambda.FunctionUrlAuthType.NONE,
            cors=aws_lambda.FunctionUrlCorsOptions(
                allowed_origins=["*"],
                allowed_methods=[aws_lambda.HttpMethod.ALL]
            )
        )

        lambda1_layer = aws_lambda.LayerVersion(
            self, "Lambda1Layer",
            code=aws_lambda.Code.from_asset("layers/lambda-layer"),
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_9],
            description="Lambda1 dependencies: requests"
        )

        lambda_fn = aws_lambda.Function(
            self, "MyLambda",
            runtime=aws_lambda .Runtime.PYTHON_3_9,
            handler="handler.handler",
            code=aws_lambda.Code.from_asset("lambda"),
            layers=[lambda1_layer],
            environment={
                "TABLE_NAME": table.table_name,
                "BUCKET_NAME": bucket.bucket_name,
                "DEST_LAMBDA": dest_func_url.url
            }
        )

        # Add S3 trigger
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            aws_s3_notifications.LambdaDestination(lambda_fn)
        )

        table.grant_read_write_data(lambda_fn)
        bucket.grant_read(lambda_fn)
        dest_bucket.grant_read_write(lambda_fn_dest)

        # Add Function URL for internet access
        function_url = lambda_fn.add_function_url(
            auth_type=aws_lambda.FunctionUrlAuthType.NONE,
            cors=aws_lambda.FunctionUrlCorsOptions(
                allowed_origins=["*"],
                allowed_methods=[aws_lambda.HttpMethod.ALL]
            )
        )



        

        
            
