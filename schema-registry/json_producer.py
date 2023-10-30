import argparse
from uuid import uuid4

import json
import requests
import base64

from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer


def delivery_report(err, msg):
  """ Called once for each message produced to indicate delivery result.
      Triggered by poll() or flush(). """
  if err is not None:
      print('Message delivery failed: {}'.format(err))
  else:
      print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

def createProducer():
  producer_conf = {'bootstrap.servers': 'lsrdtszyacea.streaming.ap-melbourne-1.oci.oraclecloud.com:9092'}
  sasl_conf = {'security.protocol':'SASL_SSL','sasl.mechanism':'PLAIN','sasl.username':'apaccpt03/oracleidentitycloudservice/omid.izadkhasti@oracle.com/ocid1.streampool.oc1.ap-melbourne-1.amaaaaaap77apcqa7t4whz6xuhv33f6xsul2dkdn3ewmxbs3lsrdtszyacea','sasl.password':'r6Ubv{j<rZNn+<vf9v<M'}
  
  producer_conf.update(sasl_conf)
  print(producer_conf)
  
  producer = Producer(producer_conf)
  return producer  

def getSchema(schemaRegUrl, schemaId):

  headers = {
    'Content-type': 'application/json'
  }

  data = {
  }

  url=envConfig["schemaRegUrl"]+"/"+schemaId

  resp = requests.get(url, headers=headers)

  return resp.json()  
    

def main():
  topic = 'mytopic'
  schema_registry_conf = {'url': 'http://172.16.1.125:30100/api/artifacts'}
  schema_registry_client = SchemaRegistryClient(schema_registry_conf)

  string_serializer = StringSerializer('utf_8')
  #json_serializer = JSONSerializer(schema_str, schema_registry_client, user_to_dict)





#producer.produce('mytopic', data.encode('utf-8'), callback=delivery_report)

# Wait for any outstanding messages to be delivered and delivery report
# callbacks to be triggered.
#producer.flush()
