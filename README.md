# AWS-Web-Connect

Python based bunch of scripts to get programmatic access to AWS through Boto3.

In summary - The webflow component logs an SSO user to an Azure AD SSO link going over to AWS dashboard. As part of this, this component records the SAML Assertion exchanged. 
The aws-connect component uses the SAML assertion to connect to AWS using boto3, assume a role and run tasks.

To run, download the latest chromedriver aligning to your browswer from https://chromedriver.chromium.org/downloads and place it at the project root. Rename the file called "rename-me-to-config.txt" to "config.txt" and fill in values. Run aws-connect.py

Note - project dependencies managed through pipenv (specifically - boto3[crt], requests and selenium-wire)
