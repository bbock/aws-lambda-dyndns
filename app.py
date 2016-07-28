"""
AWS lambda function to update client IP address in a Route 53 DNS resource record

The inteded usage for this function is to provide a simple DDNS solution
for your domain hosted on AWS Route 53. Just make your router / DDNS client call
the API gateway endpoint on each IP address change.
"""

from chalice import Chalice
from chalice import BadRequestError
import boto3
import re

app = Chalice(app_name='route53-dyndns')
app.debug = False

config = {
    'ZoneId': 'AWS-Route53-ZoneID',
    'Username': 'ddns-username',
    'Password': 'ddns-password'
}


@app.route('/')
def index():
    """Main function"""
    client = boto3.client('route53')

    # check for mandatory hostname
    if 'hostname' in app.current_request.query_params:
        hostname = app.current_request.query_params['hostname']
    else:
        raise BadRequestError('Missing hostname!')

    # Authentication
    if ('username' in app.current_request.query_params and
            'password' in app.current_request.query_params):
        username = app.current_request.query_params['username']
        password = app.current_request.query_params['password']
    else:
        raise BadRequestError("Invalid credentials")
    if username != config['Username'] or password != config['Password']:
        raise BadRequestError("Invalid credentials")

    if 'ip4addr' in app.current_request.query_params:
        ip4addr = app.current_request.query_params['ip4addr']
    else:
        # fallback to X-Forwarded-For if client submits no IP in query params
        ip4addr = re.split(",?", app.current_request.headers['X-Forwarded-For'])[0]

    # define update for IPv4. this is mandatory
    changes = [{
        'Action': 'UPSERT',
        'ResourceRecordSet': {
            'Name': hostname,
            'Type': 'A',
            'TTL': 5,
            'ResourceRecords': [{
                'Value': ip4addr
            }]
        }
    }]

    # add update for IPv6, if defined
    if 'ip6addr' in app.current_request.query_params:
        ip6addr = app.current_request.query_params['ip6addr']
        changes.append({
            'Action': 'UPSERT',
            'ResourceRecordSet': {
                'Name': hostname,
                'Type': 'AAAA',
                'TTL': 5,
                'ResourceRecords': [{
                    'Value': ip6addr
                }]
            }
        })

    client.change_resource_record_sets(
        HostedZoneId=config['ZoneId'],
        ChangeBatch={
            'Comment': 'Update by AWS Lambda function for DDNS',
            'Changes': changes
        }
    )
    return "Update successful"
