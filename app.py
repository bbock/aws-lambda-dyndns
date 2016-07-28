"""
AWS lambda function to update client IP address in a Route 53 DNS resource record

The inteded usage for this function is to provide a simple DDNS solution
for your domain hosted on AWS Route 53. Just make your router / DDNS client call
the API gateway endpoint on each IP address change.
"""

from chalice import Chalice
import boto3
import re

app = Chalice(app_name='route53-dyndns')
app.debug = False

config = {
    'ZoneId': 'AWS-ZoneID',
    'Hostname': 'fqdn.of.ddns.client.example.net'
}


@app.route('/')
def index():
    """Main function"""
    client = boto3.client('route53')
    client_ip = re.split(",?", app.current_request.headers['X-Forwarded-For'])[0]
    client.change_resource_record_sets(
        HostedZoneId=config['ZoneId'],
        ChangeBatch={
            'Comment': 'Update by AWS Lambda function',
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': config['Hostname'],
                        'Type': 'A',
                        'TTL': 5,
                        'ResourceRecords': [
                            {
                                'Value': client_ip
                            }
                        ]
                    }
                }
            ]
        }
    )
    return "Update successful"
