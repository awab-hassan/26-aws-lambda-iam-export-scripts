import boto3
import json
import os

# Initialize boto3 client for IAM
iam_client = boto3.client('iam')

# Function to get all IAM roles
def get_iam_roles():
    roles = []
    paginator = iam_client.get_paginator('list_roles')
    for page in paginator.paginate():
        roles.extend(page['Roles'])
    return roles

# Function to retrieve role details, including attached policies
def get_role_details(role_name):
    try:
        # Get the role details (AssumeRolePolicyDocument)
        role_info = iam_client.get_role(RoleName=role_name)
        role = role_info['Role']

        # Get the attached policies
        attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']

        # Get the inline policies
        inline_policies = iam_client.list_role_policies(RoleName=role_name)['PolicyNames']

        # Collect role data
        role_data = {
            'RoleName': role['RoleName'],
            'Arn': role['Arn'],
            'AssumeRolePolicyDocument': role['AssumeRolePolicyDocument'],
            'AttachedPolicies': attached_policies,
            'InlinePolicies': inline_policies,
        }
        return role_data
    except Exception as e:
        print(f"Error retrieving details for {role_name}: {e}")
        return None

# Function to export all IAM role details to a JSON file
def export_iam_roles_to_json(file_name='iam_roles_export.json'):
    roles = get_iam_roles()
    if not roles:
        print("No IAM roles found!")
        return
    
    roles_data = []
    for role in roles:
        role_name = role['RoleName']
        role_details = get_role_details(role_name)
        if role_details:
            roles_data.append(role_details)
    
    # Save roles data to a JSON file
    with open(file_name, 'w') as f:
        json.dump(roles_data, f, indent=4)
    
    print(f"Exported {len(roles_data)} IAM roles to {file_name}")

# Main function to export IAM roles
if __name__ == '__main__':
    export_iam_roles_to_json()
