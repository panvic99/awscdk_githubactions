#!/usr/bin/env python3
import os
import json

import aws_cdk as cdk

from my_cdk_project.my_cdk_project_stack import MyCdkAppStack
app = cdk.App()
# Get environment from context (defaults to 'dev')
env_name = app.node.try_get_context("environment") or "dev"
with open(f"config/{env_name}.json") as f:
    config = json.load(f)


MyCdkAppStack(app, "MyCdkAppStack",
    env=cdk.Environment(account=config["account"], region=config["region"]),
)

app.synth()
