# Copyright 2018 Google LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/python

import time
import datetime
import uuid
import json
import jwt
from google.cloud import pubsub
from oauth2client.client import GoogleCredentials
from Adafruit_BME280 import *
from tendo import singleton
import paho.mqtt.client as mqtt

me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

# constants - change to fit your project and location
SEND_INTERVAL = 60 #seconds
sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
credentials = GoogleCredentials.get_application_default()
# change project to your Project ID
project="pi-iot-sensor-project01"
# change topic to your PubSub topic name
topic = "bme280-events"
# set the following four constants to be indicative of where you are placing your weather sensor
sensorID = "bme280-001"
sensorZipCode = "02364"
sensorLat = "41.9933"
sensorLong = "-70.7285"
# set crypto info
ssl_private_key_filepath="./certs/rsa_private.pem"
ssl_algorithm="RS256_X509"
root_cert_filepath="./certs/rsa_cert.pem"
project_id=project
token_life = 60
# set MQTT info
gcp_location="us-central1"
registry_id="Pi3-BME280-Nodes"
device_id="BME280-node1"
sensorID=registry_id + "." + device_id
googleMQTTURL
googleMQTTPort
receiver_in

	
def create_jwt(cur_time, projectID, privateKeyFilepath, algorithmType):
  token = {
  'iat': cur_time,
  'exp': cur_time + datetime.timedelta(minutes=token_life),
  'aud': projectID
  }

  with open(privateKeyFilepath, 'r') as f:
    private_key = f.read()

  return jwt.encode(token, private_key, algorithm=algorithmType)

def read_sensor(weathersensor):
    tempF = weathersensor.read_temperature_f()
    # pascals = sensor.read_pressure()
    # hectopascals = pascals / 100
    pressureInches = weathersensor.read_pressure_inches()
    dewpoint = weathersensor.read_dewpoint_f()
    humidity = weathersensor.read_humidity()
    temp = '{0:0.2f}'.format(tempF)
    hum = '{0:0.2f}'.format(humidity)
    dew = '{0:0.2f}'.format(dewpoint)
    pres = '{0:0.2f}'.format(pressureInches)
    return (temp, hum, dew, pres)

def createJSON(id, timestamp, zip, lat, long, temperature, humidity, dewpoint, pressure):
    data = {
      'sensorID' : id,
      'timecollected' : timestamp,
      'zipcode' : zip,
      'latitude' : lat,
      'longitude' : long,
      'temperature' : temperature,
      'humidity' : humidity,
      'dewpoint' : dewpoint,
      'pressure' : pressure
    }

    json_str = json.dumps(data)
    return json_str

def main():
    args = parse_command_line_args()
    googleMQTTURL = args.mqtt_bridge_hostname
    googleMQTTPort = args.mqtt_bridge_port
    receiver_in = args.receiver_in
    
    _CLIENT_ID = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(project_id, gcp_location, registry_id, device_id)
    _MQTT_TOPIC = '/devices/{}/events'.format(device_id)
  
    while True:
      client = mqtt.Client(client_id=_CLIENT_ID)
      cur_time = datetime.datetime.utcnow()
      # authorization is handled purely with JWT, no user/pass, so username can be whatever
      client.username_pw_set(
          username='unused',
          password=create_jwt(cur_time, project_id, ssl_private_key_filepath, ssl_algorithm))
      
      client.on_connect = on_connect
      client.on_publish = on_publish

      client.tls_set(ca_certs=root_cert_filepath) # Replace this with 3rd party cert if that was used when creating registry
      client.connect(googleMQTTURL, googleMQTTPort)

      jwt_refresh = time.time() + ((token_life - 1) * 60) #set a refresh time for one minute before the JWT expires

      client.loop_start()

      last_checked = 0
      while time.time() < jwt_refresh: # as long as the JWT isn't ready to expire, otherwise break this loop so the JWT gets refreshed
        try:
          if time.time() - last_checked > SEND_INTERVAL:
            last_checked = time.time()
            temp, hum, dew, pres = read_sensor(sensor)
            currentTime = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            s = ", "
            weatherJSON = createJSON(sensorID, currentTime, sensorZipCode, sensorLat, sensorLong, temp, hum, dew, pres)
            client.publish(_MQTT_TOPIC, weatherJSON, qos=1)
            print("{}\n".format(weatherJSON))
            time.sleep(0.5)
            previousInput = inputReceived
          except Exception as e:
      print "There was an error"
      print (e)
    
      client.loop_stop()
if __name__ == '__main__':
  main()

