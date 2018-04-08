"""create instances for
https://github.com/Praqma/LearnKubernetes/blob/master/kamran/Kubernetes-The-Hard-Way-on-AWS.md"""

# stdlib
import logging
from json import load, dumps
from time import sleep

# 3rd party
import boto3

#local

ec2 = boto3.client('ec2', region_name='us-east-1')

with open('config.json') as fd:
  config = load(fd)

user_data = """\
#!/bin/bash
echo "10.0.0.245 etcd1" >> /etc/hosts
echo "10.0.0.246 etcd2" >> /etc/hosts
echo "10.0.0.137 controller1" >> /etc/hosts
echo "10.0.0.138 controller2" >> /etc/hosts
echo "10.0.0.181 worker1" >> /etc/hosts
echo "10.0.0.182 worker2" >> /etc/hosts
"""

instances = {'etcd1': '10.0.0.245',
             'etcd2': '10.0.0.246',
             'controller1': '10.0.0.137',
             'controller2': '10.0.0.138',
             'worker1': '10.0.0.181',
             'worker2': '10.0.0.182'}

results = []

for instance_name in instances:
  name = f'{config["name_modifier"]}-{instance_name}'
  res = ec2.run_instances(ImageId=config['ami_id'],
                          UserData=user_data,
                          MaxCount=1,
                          MinCount=1,
                          InstanceType='t2.micro',
                          KeyName=config['key_name'],
                          NetworkInterfaces=[
                            {'AssociatePublicIpAddress': True,
                             'Groups': config['security_groups'],
                             'DeviceIndex': 0,
                             'DeleteOnTermination': True,
                             'PrivateIpAddress': instances[instance_name],
                             'SubnetId': config['subnet_id']}
                          ],
                          TagSpecifications=[
                            {'ResourceType': 'instance',
                             'Tags': [
                              {'Key': 'Name',
                               'Value': name}
                             ]}
                          ])
  results.append(res['Instances'][0]['InstanceId'])

# wait a bit to allow public IPs to be assigned
sleep(3)

instance_data = ec2.describe_instances(InstanceIds=results)

for r in instance_data['Reservations']:
  for instance in r['Instances']:
    name = instance['Tags'][0]['Value']
    _id = instance['InstanceId']
    public_ip = instance['PublicIpAddress']
    print(f'{name} - {_id} - {public_ip}')