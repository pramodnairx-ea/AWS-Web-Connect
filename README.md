# AWS-Web-Connect

Python based bunch of scripts to get programmatic access to AWS through Boto3.

In summary - The webflow component logs an SSO user to an Azure AD SSO link going over to AWS dashboard. As part of this, this component records the SAML Assertion exchanged. 
The aws-connect component uses the SAML assertion to connect to AWS using boto3, assume a role and run tasks.
