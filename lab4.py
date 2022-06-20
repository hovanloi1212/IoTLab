print("IoT Gateway")
from gc import collect
#from simpleAI import *
import paho.mqtt.client as mqttclient
import time
import json

import serial.tools.list_ports

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
mess = ""

#TODO: Add your token and your comport
#Please check the comport in the device manager
THINGS_BOARD_ACCESS_TOKEN = "88lbBIvmjolmHsh0CfMR"
bbc_port = "COM10"
if len(bbc_port) > 0:
    ser = serial.Serial(port=bbc_port, baudrate=115200)

def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    #TODO: Add your source code to publish data to the server
    try:
        sensordata(splitData[0],splitData[1],splitData[2])
    except ValueError:
        pass

def sensordata(id,telemetry,data):
    global light,temp,light2,temp2
    try:
        counter = name_data.index(id)
    except ValueError:
        if (len(id) != 5): 
            return 
        print("New sensor")
        name_data.append(id)
        counter = len(name_data) - 1

    if (counter == 0):          
        if telemetry == "0" :
            temp = data
        if telemetry == "1":
            light = data

    if (counter == 1):
        if telemetry == "0" :
            temp2 = data
        if telemetry == "1":
            light2 = data

def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")

def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    cmd = 1
    id = 0
    #TODO: Update the cmd to control 2 devices
    try:
        jsonobj = json.loads(message.payload)

        if jsonobj['method'] == "setLED":
            id = 0
            temp_data['value'] = jsonobj['params']
            if temp_data['value'] == True: cmd = 1
            else: cmd = 0
            client.publish('v1/devices/me/BUTTON_LED', json.dumps(temp_data), 1)
        if jsonobj['method'] == "setFAN":
            id = 0
            temp_data['valueFAN'] = jsonobj['params']
            client.publish('v1/devices/me/BUTTON_FAN', json.dumps(temp_data), 1)
            if temp_data['valueFAN'] == True: cmd = 3
            else: cmd = 2

        if jsonobj['method'] == "setLED2":
            id = 1
            temp_data['valueLED2'] = jsonobj['params']
            if temp_data['valueLED2'] == True: cmd = 1
            else: cmd = 0
            client.publish('v1/devices/me/BUTTON_LED2', json.dumps(temp_data), 1)
        if jsonobj['method'] == "setFAN2":
            id = 1
            temp_data['valueFAN2'] = jsonobj['params']
            client.publish('v1/devices/me/BUTTON_FAN2', json.dumps(temp_data), 1)
            if temp_data['valueFAN2'] == True: cmd = 3
            else: cmd = 2

    except:
        pass

    if len(bbc_port) > 0:
        ser.write((name_data[id] + ":" + str(cmd) + "#").encode())

def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()
client.on_subscribe = subscribed
client.on_message = recv_message
collect_data = {}
name_data = []

temp = 0
light = 0
temp2 = 0
light2 = 0
isMasked = []
while True:
    if len(bbc_port) >  0:
        readSerial()
        # capture_image()
        # isMasked = AI_detection()
        # print(isMasked)
        collect_data  = {'temperature': temp, 'light':light, 'temperature2': temp2, 'light2':light2}
        client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    time.sleep(1)