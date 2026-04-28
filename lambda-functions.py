import boto3
import os
import requests

# Initialize boto3 client for Lambda
lambda_client = boto3.client('lambda')

# Function to get all Lambda function names
def get_lambda_functions():
    functions = []
    paginator = lambda_client.get_paginator('list_functions')
    for page in paginator.paginate():
        for function in page['Functions']:
            functions.append(function['FunctionName'])
    return functions

# Function to download the Lambda function's code as a ZIP file
def download_lambda_code(function_name, download_dir='lambda_exports_virginia'):
    try:
        # Get the function's code
        response = lambda_client.get_function(FunctionName=function_name)
        code_url = response['Code']['Location']
        
        # Prepare the directory for storing the ZIP files
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        
        # Define the local filename
        local_file = os.path.join(download_dir, f"{function_name}.zip")
        
        # Use the requests library to download the ZIP file from the code URL
        zip_response = requests.get(code_url)
        zip_response.raise_for_status()  # Ensure the request was successful
        
        # Write the content to a local file
        with open(local_file, 'wb') as f:
            f.write(zip_response.content)
        
        print(f"Downloaded {function_name} to {local_file}")
    except Exception as e:
        print(f"Error downloading {function_name}: {e}")

# Main function to export all Lambda functions
def export_all_lambda_functions():
    functions = get_lambda_functions()
    if not functions:
        print("No Lambda functions found!")
        return
    
    print(f"Found {len(functions)} Lambda functions. Exporting...")
    
    for function_name in functions:
        download_lambda_code(function_name)

# Run the script
if __name__ == '__main__':
    export_all_lambda_functions()
