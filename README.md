# IoT Weather Station (Temperature, Pressure, Humidity, DewPoint) with BME280 sensor

This project is based on on Google Cloud's Codelab example: https://codelabs.developers.google.com/codelabs/iot-data-pipeline/index.html

It was modified to include:
- Google Cloud IoT Core
- MQTT and ES256 for security
- GSheets App script macro to import Google BigQuery data

## What does it do

A temperature/pressure/humidity/dewpoint monitoring system that:
* starts with an IoT device (the Rasperry Pi + BMI280 sensor)
* utilizes Google Cloud IoT Core with communication over MQTTS
* levarages a message queue to receive and deliver data (Google Cloud Pub/Sub)
* takes advantage of a serverless function (Google Cloud Function) to move the data...
* ... to a data warehouse (Google BigQuery)
* creates a dashboard using Google Data Studio and/or Google GSheets
(insert architecture diagram)

## Getting started

### Requirements

* Raspberry Pi 3 Model B or Raspberry Zero. A Raspberry Pi 3 B+ (amazon link) was used for the tests. It's faster :-)
* Texas Instrument BME280 Temperature & Pressure sensor (amazon link)
* Female-to-female breadboard wires (amazon link)
* SD-Card with Raspbian OS
* keyboard/mouse
* external monitor over HDMI
Optional:
* Raspberry Pi official 7" touch display (amazon link)
* SmartPi touch display mount (amazon link)
* 5.2V, 3A power supply to supply both the Raspberry Pi and the touch display
(insert photo)

### Assembly

Raspberry Pi pin -> Sensor (BME280)
```
    Pin 1 (3.3V) - > VIN
    Pin 3 (GPIO2) -> SDA
    Pin 5 (GPIO3) -> SCL
    Pin 9 (Ground) -> GND
```
(insert schematic)
(insert photo)

## Step 1 - Raspberry Pi Initial Configuration

From the Raspberry device:
* Go to the Pi menu, open "Raspberry Pi Configuration"
    * Make sure that I2C, and SSH are enabled
    * Double check your Locale and Timezone as well
    * Reboot
* Open a terminal and clone this Github repository
```
	git clone https://github.com/gforce81/GCP-IoT-WeatherData.git
```
* From GCP-IoT-WeatherData folderm install dependencies and required libraries:
```
	cd GCP-IoT-WeahterData
	sh ./initialsoftware.sh
```
* Generate encryption keys (private and public)
```
	sh ./generate_keys.sh
```
* Export securely the public key (~/.ssh/ec_public.pem) to your main computer (use a USB key, SFTP, SSH, etc.)
* Move out of GCP-IoT-WeatherData repository
```
	cd ..
```
* Clone the Adafruit repository for sensor drivers
```
	git clone https://github.com/adafruit/Adafruit_Python_GPIO
```
* Install the drivers
```
	cd Adafruit_Python_GPIO
	sudo python setup.py install
```
* Copy the required drivers to the project repository
```
	cd GCP-IoT-WeatherData/third_party/Adafruit_BME280
	mv Adafruit_BME280.py ../..
```
* Type in the following command to make certain that the sensor is correctly connected.

```
  sudo i2cdetect -y 1
```
* The response should be "77"
    * A result other than "77" could indicate that the type of sensor doesn’t match the one recommended and this will cause the sensor driver to not function correctly. To fix this situation, edit the Adafruit_BME280.py script. For example, if the result is showing 76, change the BME280_I2CADDR to 0x76.

## Step 2 - Setup a Google Cloud Project

* Log into the Google Cloud Console. If you don't have a Google Cloud account, you can create one here (http://console.cloud.google.com/)
* Create a new project (e.g. IoT-temperarature-sensor-IoT)
* Take note of the Project ID

### Step 2.1 - Enable Google Cloud APIs

* From the Google Cloud Console menu, select APIs & Services -> Library
* Enable the following APIs for your project:
    * BigQuery API
    * BigQuery Data Transfer API
    * Cloud Functions API
    * Cloud IoT API
    * Cloud Pub/Sub API
    * Google Cloud Realtime API

## Step 3 - Configure Google Cloud IoT Core

### Step 3.1 - Create an IoT Core Registry

* From the left side menu, select IoT Core
* Click on "Create Device Registry"
* Fill the details for your project, e.g.:
```
	Registry ID: TemperatureData-Nodes
	Region: us-central1
	Protocol: MQTT, HTTP
```
* Create Cloud Pub/Sub topics, e.g.:
```
	Default Telemetry: temperature-events
	Device state: temperature-device-state
```
* Do not add a certificate for now. Keys will be added at a later step
* Create the registry

### Step 3.2 Register an IoT Core Device
* From the registry page, click "Create a Device"
* Set a device ID, e.g.:
```
	temperature-sensor-01
```
* Make sure the device communication is allowed
* Authentication Input Method: 
```
	Enter manually
```
* Public Key format: 
```
	RS256
```
* Public Key value: copy/paste the content of ec_public.pem that was previously exported
* Leave other options as default
* Enter additional device metadata (not required)

## Step 4 - Configure Google BigQuery

* From the Google Cloud Console
    * From the left side menu, select BigQuery
* At the BigQuery welcome screen, select
```
    Create a new dataset 
```
* Provide the requried information
```
    Dataset ID: weatherData
    Data location: US
    Data expiration: Never
```
* Click the "+" sign next to the new dataset to create a new table
    * For Source Data, select "Create empty table"
    * For Destination table name, enter "weatherDataTable"
    * Under schema, click on "Add Field"
    * Add the following fields:
```
    sensorID: STRING, NULLABLE
    timecollected: TIMESTAMP, NULLABLE
    zipcode: INTEGER, NULLABLE
    latitude: FLOAT, NULLABLE
    longitude: FLOAT, NULLABLE
    temperature: FLOAT, NULLABLE
    humidity: FLOAT, NULLABLE
    dewpoint: FLOAT, NULLABLE
    pressure: FLOAT, NULLABLE
```
* Create the table

## Step 5 - Configure Google Cloud Function

* From the Google Cloud Console
    * From the left side menu, select Cloud Functions
* Select
```
    Create Function
```
* Provide a function name, e.g.:
```
     function-weatherPubSubToBQ
```
* Select the following parameters:
```
    Memory allocated: 256 MB
    Trigger: Cloud Pub/Sub
    Topic: e.g. bme280-events
    Source Code: Inline Editor
    Runtime: Node.js 6
```
* In the inline code editor:
    * Under index.js: copy the content of cloudfunction.js
    * Under package.json: copy the content of weatherFunction-pacakge.json
* Funcion to execute:
```
    subscribe
```
* Create the cloud function
    * It may take few minutes
    * A green checkmark will appear

## Step 6 - Send Telemetry Data

### Step 6.1 - Start Capturing and Streaming Telemetry Data from IoT Device

* On the Rapberry Pi:
    * Open a terminal window
```
    cd GCP-IoT-WeatherData
```
* Start the python script to capture and stream telemetry data
```
    python checkWeather-modified.py
```
* After a very short delay, telemetry should start streaming

### Step 6.2 - Check Data

* Check the data is being correctly inserted in BigQuery
* Open BigQuery
    * Select the project -> dataset
    * In the Query Editor, enter e.g.:
```
    SELECT * FROM weatherData.weahterDataTable ORDER BY timecollected
```
* You should see sensor data at 1 minute interval

## Step 7 - Create a Dashboard

### Step 7.1 - Google Data Studio

### Step 7.2 - Google GSheets
