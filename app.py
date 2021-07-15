#!/usr/bin/env python3

from aws_cdk import core

from impressions.impressions_stack import ImpressionsStack


app = core.App()
ImpressionsStack(app, "impressions")

app.synth()
