#!/usr/bin/env python3
import os

import aws_cdk as cdk

from my_cdk_project.my_cdk_project_stack import MyCdkAppStack


app = cdk.App()
MyCdkAppStack(app, "MyCdkAppStack",
    env=cdk.Environment(account='529166310744', region='ap-south-1'),
)

app.synth()
