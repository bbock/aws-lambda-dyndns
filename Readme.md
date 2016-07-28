# Amazon Lambda function to use AWS Route53 as DynDNS service

The intended usage for this function is to provide a simple DDNS solution
for your domain hosted on AWS Route 53. Just make your router / DDNS client call
the API gateway endpoint on each IP address change.

This Lambda function is based on version 0.0.1 of [Chalice](https://github.com/awslabs/chalice),
which is a micro framework for AWS Lambda in python.

Unfortunately, Chalice does currently not support external modules or config
files. Therefore, you need to adapt your configuration directly in app.py.

## Usage

First, install dependencies in a local virtualenv for deployment on AWS:

```bash
virtualenv -p python2 venv
source venv/bin/activate
pip install -r requirements.txt
```

Enter your AWS credentials in ~/.aws/config, as required by acs-cli or boto.
If you have not set up proper AWS access keys yet, do that first. There are
plenty of tutorials in the net on how to do that.

Make sure to change ZoneId and credentials in the config section of app.py.

Then deploy to AWS:

```
chalice deploy
```

On the first run, chalice will tell you the autogenerated policy for the function
and the API gateway URL where the function is reachable.

Use this URL in your DynDNS client. You can provide the required parameters in
the query string. This is compatible with many DDNS clients.

The URL you have to use has looks like this:

```
https://abcedfg.execute-api.eu-west-1.amazonaws.com/dev/?hostname=your.host.name&username=ddnsuser&password=secret&ip4addr=1.2.3.4&ip6addr=2001::1
```

IPv6 is optional. IPv4 is taken from the query string, if provided, and extracted
from the source IP of the request, if not provided.

## FritzBox users

Quick note for users of the AVM Fritz!Box:

Unfortunately the Fritz!Box can send DDNS updates only unencrypted via HTTP,
while AWS API Gateway provides only HTTPS. :( If you intend to use this solution
with a Fritz!Box, you need an additional proxy in between which does HTTP->HTTPS
translation. Make sure to provide your IP address in the query string or send
a X-Forwarded-For header on the proxy, or the DDNS record will point to your
proxy!
