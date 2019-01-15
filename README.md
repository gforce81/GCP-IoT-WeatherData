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
Pin 1 (3.3V) - > VIN
Pin 3 (GPIO2) -> SDA
Pin 5 (GPIO3) -> SCL
Pin 9 (Ground) -> GND
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

## Step 5 - Configure Google Cloud Function

## Step 6 - Start Telemetry Streaming from IoT Device

## Step 7 - Create a Dashboard

### Step 7.1 - Google Data Studio

### Step 7.2 - Google GSheets
