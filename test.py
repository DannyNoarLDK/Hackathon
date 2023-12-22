# Xxokzs/iMGZ1pbqn4yxN5K9dOKBrsbvFqM+FAn/J

import json
import os
import sys

import boto3
import botocore
from botocore.config import Config

import re
import os

base_path = 'force-app/main/default/objects/Opportunity/recordTypes'
file_names = os.listdir(base_path)
pattern_bp = re.compile(r'<businessProcess>(.*?)</businessProcess>', re.DOTALL)
pattern_fn = re.compile(r'<fullName>(.*?)</fullName>', re.DOTALL)

record_types = {}
for file_name in file_names:
    with open(base_path + '/' + file_name, 'r') as file:
        xml_content = file.read()
    record_types[pattern_fn.findall(xml_content)[0]] = {
        'BusinessProcess':pattern_bp.findall(xml_content)[0]
    }

base_path = 'force-app/main/default/objects/Opportunity/businessProcesses'
file_names = os.listdir(base_path)
pattern_fn = re.compile(r'<fullName>(.*?)</fullName>', re.DOTALL)

for file_name in file_names:
    with open(base_path + '/' + file_name, 'r') as file:
        xml_content = file.read()
    allNames = pattern_fn.findall(xml_content)
    if allNames[0] not in record_types:
        record_types[allNames[0]] = {}
    record_types[allNames[0]]['stages'] = allNames[1:]

session = boto3.Session()
bedrock_client = session.client(
    service_name='bedrock-runtime',
    config=Config(
        region_name='us-east-1',
        retries={
            "max_attempts": 10,
            "mode": "standard",
        },
    )
)

picked_record_type = list(record_types.keys())[0]

text = (
    'Generate Salesforce process documentation for a Sales process called: ' +
    'Record Type: ' + picked_record_type + ' With the following sales process stages: ' + 
    str(record_types[picked_record_type]['stages'])
)
# text = (
#     'Can you make a sales process documentation for the following: ' +
#     'Record Type: ' + picked_record_type + ', ' + str(record_types[picked_record_type])
# )
response = bedrock_client.invoke_model(
    # body = json.dumps({"inputText": text}), 
    body = json.dumps({ 
        'prompt': text,
        'max_gen_len': 2048,
        'top_p': 0.9,
        'temperature': 0.2
    }),
    modelId = "meta.llama2-13b-chat-v1", 
    accept = "application/json", 
    contentType = "application/json"
)
response_body = json.loads(response.get("body").read())

# print(response_body.get("results")[0].get("outputText"))
print(response_body['generation'])

with open('output.txt', 'w') as file:
    file.write(response_body['generation'])

print('done')