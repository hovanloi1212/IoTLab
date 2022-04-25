print("Xin chao ThingBoard")
import paho.mqtt.client as mqttclient
import time
import json
import asyncio
import winrt.windows.devices.geolocation as wdg

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "88lbBIvmjolmHsh0CfMR"


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setValue":
            temp_data['value'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
    except:
        pass


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")

async def get_current_location():
    global longitude, latitude
    locator = wdg.Geolocator()
    pos = await locator.get_geoposition_async()
    longitude = pos.coordinate.longitude
    latitude = pos.coordinate.latitude

client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message
temp = 30
humi = 50
light_intesity = 10
counter = 0
loop = asyncio.get_event_loop()
while True:
    loop.run_until_complete(get_current_location())
    collect_data = {'temperature': temp, 'humidity': humi, 'light':light_intesity, 'longitude': longitude, 'latitude': latitude}
    print(longitude, latitude)
    temp += 1
    humi += 1
    light_intesity += 1
    client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    time.sleep(5)  