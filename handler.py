import json

import boto3
from botocore.exceptions import ClientError
from pdfCropMargins import crop


def main(event, context):
    if not validate_parameter(event):
        return {'statusCode': 400, 'errorMessage': 'Invalid parameter.'}

    s3 = boto3.client('s3')
    """ :type : pyboto3.s3 """

    # Download file from s3
    try:
        s3.download_file(Bucket=event['bucket_name'], Key=event['object_key'], Filename=event['object_key'])
    except ClientError as e:
        return {'statusCode': 400, 'errorMessage': e.response['Error']['Message']}

    # crop pdf
    try:
        # -s : 모든 페이지를 같은 크기로 변경
        # -u : 각 페이지를 같은 크기로 crop
        output = event['object_key'].replace('.pdf', '_cropped.pdf')
        crop_config = ['-u', '-s', f'-o{output}', event['object_key']]
        crop(crop_config)
    except:
        return {'statusCode': 500, 'errorMessage': 'Error occurred while trying to crop pdf.'}

    # Upload file to s3
    try:
        s3.upload_file(output, Bucket=event['bucket_name'], Key=output)
    except ClientError as e:
        return {'statusCode': 500, 'errorMessage': e.response['Error']['Message']}

    body = {
        'bucket': event['bucket_name'],
        'object_key': output,
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


def validate_parameter(event):
    required_params = ["bucket_name", "object_key"]
    for required_param in required_params:
        if not (required_param in event):
            return False
    return True
