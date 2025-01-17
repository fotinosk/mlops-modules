# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from typing import Any, cast

import aws_cdk as cdk
import cdk_ecr_deployment as ecr_deployment
import cdk_nag
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecr_assets as ecr_assets
from constructs import Construct, IConstruct


class MlflowImagePublishingStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        app_prefix: str,
        ecr_repo_name: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        cdk.Tags.of(scope=cast(IConstruct, self)).add(key="Deployment", value=app_prefix[:64])

        repo = ecr.Repository.from_repository_name(self, "ECR", repository_name=ecr_repo_name)

        local_image = ecr_assets.DockerImageAsset(
            self,
            "ImageAsset",
            directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"),
        )

        self.image_uri = f"{repo.repository_uri}:latest"
        ecr_deployment.ECRDeployment(
            self,
            "ECRDeployment",
            src=ecr_deployment.DockerImageName(local_image.image_uri),
            dest=ecr_deployment.DockerImageName(self.image_uri),
        )

        # Add CDK nag solutions checks
        cdk.Aspects.of(self).add(cdk_nag.AwsSolutionsChecks(log_ignores=True))

        cdk_nag.NagSuppressions.add_stack_suppressions(
            self,
            apply_to_nested_stacks=True,
            suppressions=[
                cdk_nag.NagPackSuppression(
                    id="AwsSolutions-IAM4",
                    reason="Managed Policies are for src account roles only",
                ),
                cdk_nag.NagPackSuppression(
                    id="AwsSolutions-IAM5",
                    reason="Resource access restricted to resources",
                ),
            ],
        )
