import argparse
from uuid import uuid4

import json
import requests
import base64

from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer

class Device(object):
       def __init__(self, deviceId, deviceLocation, deviceTemp, timestamp):
        self.deviceId = deviceId
        self.deviceLocation = deviceLocation
        self.deviceTemp = deviceTemp
        self.timestamp = timestamp

def device_to_dict(device, ctx):
    return dict(deviceId=device.deviceId,
                deviceLocation=device.deviceLocation,
                deviceTemp=device.deviceTemp,
                timestamp=device.timestamp
               )

def delivery_report(err, msg):
  """ Called once for each message produced to indicate delivery result.
      Triggered by poll() or flush(). """
  if err is not None:
      print('Message delivery failed: {}'.format(err))
  else:
      print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

def getConsumer():
  consumer_conf = {'bootstrap.servers': 'lsrdtszyacea.streaming.ap-melbourne-1.oci.oraclecloud.com:9092',
                 'group.id': 'mygroup',
                 'auto.offset.reset': 'earliest'
                }
  sasl_conf = {'security.protocol':'SASL_SSL',
               'sasl.mechanism':'PLAIN',
               'sasl.username':'apaccpt03/oracleidentitycloudservice/omid.izadkhasti@oracle.com/ocid1.streampool.oc1.ap-melbourne-1.amaaaaaap77apcqa7t4whz6xuhv33f6xsul2dkdn3ewmxbs3lsrdtszyacea',
               'sasl.password':'r6Ubv{j<rZNn+<vf9v<M'
              }  
  
  consumer_conf.update(sasl_conf)
  consumer = Consumer(consumer_conf)
  
  produconsumer = Consumer(consumer_conf)
  return consumer  

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

  schema_str = """
  {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "iotDeviceTemprature",
    "description": "IOT Device Temprature",
    "type": "object",
    "properties": {
      "deviceId": {
        "description": "Device ID",
        "type": "integer"
      },
      "deviceLocation": {
        "description": "Device Location",
        "type": "string"
      },
      "deviceTemp": {
        "description": "Device Temprature",
        "type": "number"
      },
      "timestamp": {
        "description": "Timestamp",
        "type": "string"
      }
    },
    "required": [ "deviceId", "deviceLocation", "deviceTemp" ]
  }
  """
  
  schema_registry_conf = {'url': 'http://172.16.1.125:30200'}
  schema_registry_client = SchemaRegistryClient(schema_registry_conf)

  string_serializer = StringSerializer('utf_8')
  json_serializer = JSONDeserializer(schema_str, from_dict=device_to_dict)

  consumer = getConsumer()

  consumer.subscribe([topic])

  while true;
    try:
        msg = consumer.poll(1.0)
        if msg is None:
           continue
          
        device = json_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE)
        if device is not None:
           print("Device ID: {} Device Temperature: {}".format(device.deviceId, device.deviceTemp))
    except KeyboardIntrupt:
        break;


    consumer.close()

main()
