import configparser

import boto3
from botocore.config import Config
import webflow

parser = configparser.ConfigParser()
parser.read("config.txt")

saml_assertion = webflow.extract_saml_assertion()
print(f"Going with SAML Assertion as {saml_assertion}")

sts_client = boto3.client("sts", region_name=parser.get("aws", "region_name"))

assumed_role_object = sts_client.assume_role_with_saml(
    RoleArn=parser.get("aws", "role_arn"),
    PrincipalArn=parser.get("aws", "principal_arn"),
    SAMLAssertion=saml_assertion
)

print(assumed_role_object)

credentials = assumed_role_object["Credentials"]

glacier_resource = boto3.resource(
    "glacier",
    aws_access_key_id=credentials["AccessKeyId"],
    aws_secret_access_key=credentials["SecretAccessKey"],
    aws_session_token=credentials["SessionToken"],
    region_name=parser.get("aws", "region_name")
)
vaults = glacier_resource.vaults.all()
for vault in vaults:
    print(vault)
