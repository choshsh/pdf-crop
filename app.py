import json
import os

import boto3
from botocore.exceptions import ClientError
from pdfCropMargins import crop

s3 = boto3.client('s3')
""" :type : pyboto3.s3 """


def handler(event, context):
    try:
        params_dict = json.loads(event['body'])
    except:
        return {'statusCode': 400, 'errorMessage': 'Invalid parameter.'}

    if not validate_parameter(params_dict):
        return {'statusCode': 400, 'errorMessage': 'Invalid parameter.'}

    # Set variable
    bucket_name = params_dict['bucket_name']
    pdf_origin_key = str(params_dict['object_key'])
    pdf_origin_local = f'/tmp/{pdf_origin_key.split("/")[-1]}'
    pdf_output_key = pdf_origin_key.replace('.pdf', '_cropped.pdf')
    pdf_output_local = f'/tmp/{pdf_output_key.split("/")[-1]}'

    # Download file from s3
    try:
        s3.download_file(Bucket=bucket_name, Key=pdf_origin_key, Filename=pdf_origin_local)
    except ClientError as e:
        return {'statusCode': 400, 'errorMessage': e.response['Error']['Message']}
    except:
        return {'statusCode': 500, 'errorMessage': 'Unknown error.'}

    # Crop pdf
    try:
        # -s : 모든 페이지를 같은 크기로 변경
        # -u : 각 페이지를 같은 크기로 crop
        # -cm: Force the use of MuPDF (faster)
        crop_config = ['-u', '-s', '-cm', f'-o{pdf_output_local}', pdf_origin_local]
        crop(crop_config)
    except:
        return {'statusCode': 500, 'errorMessage': 'Error occurred while trying to crop pdf.'}

    # Upload file to s3
    try:
        s3.upload_file(Bucket=bucket_name, Key=pdf_output_key, Filename=pdf_output_local)
        os.remove(pdf_output_local)
    except ClientError as e:
        return {'statusCode': 500, 'errorMessage': e.response['Error']['Message']}
    except:
        return {'statusCode': 500, 'errorMessage': 'Unknown error.'}

    response = {
        'statusCode': 200,
        'body': json.dumps({
            'bucket': bucket_name,
            'object_key': pdf_output_key,
        })
    }
    return response


def validate_parameter(params):
    required_params = ['bucket_name', 'object_key']
    for required_param in required_params:
        if not (required_param in params):
            return False
    return True
