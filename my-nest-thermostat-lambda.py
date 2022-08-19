import json
import urllib3
from urllib.parse import urlencode
import boto3
import logging
import time

# initializing logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# urllib3 pool
http = urllib3.PoolManager()


def set_temp(thermostats, temp, access_token, project_id):
    # Iterate through thermostats and set the temp
    for _ in thermostats:
        logging.info("===================================================================================")
        logging.info("===================================================================================")
        logging.info(f"Setting {temp} temp at {thermostats.index(_) + 1} floor thermostat")

        url_set_mode = "https://smartdevicemanagement.googleapis.com/v1/enterprises/" + project_id + "/devices/" + _ + ":executeCommand"

        headers = {
            "Content-Type": "application/json",
            "Authorization": access_token,
        }

        data = {"command": "sdm.devices.commands.ThermostatTemperatureSetpoint.SetRange", "params": temp}
        encoded_data = json.dumps(data).encode("utf-8")
        r = http.request("POST", url_set_mode, headers=headers, body=encoded_data)
        logging.info(f"response status is {r.status}")
        logging.info(f"response data is {r.data}")
        logging.info("===================================================================================")
        logging.info("===================================================================================")


def modify_mode(thermostats, mode, access_token, project_id):
    # Iterate through thermostats and set the mode
    for _ in thermostats:
        logging.info("===================================================================================")
        logging.info("===================================================================================")
        logging.info(f"Setting {mode} mode at {thermostats.index(_) + 1} floor thermostat")

        url_set_mode = "https://smartdevicemanagement.googleapis.com/v1/enterprises/" + project_id + "/devices/" + _ + ":executeCommand"

        headers = {
            "Content-Type": "application/json",
            "Authorization": access_token,
        }

        data = {"command": "sdm.devices.commands.ThermostatMode.SetMode", "params": {"mode": mode}}
        encoded_data = json.dumps(data).encode("utf-8")
        r = http.request("POST", url_set_mode, headers=headers, body=encoded_data)
        logging.info(f"response status is {r.status}")
        logging.info(f"response data is {r.data}")
        logging.info("===================================================================================")
        logging.info("===================================================================================")


def lambda_handler(event, context):
    # secret params
    ssm = boto3.client("ssm")
    nest_params = ssm.get_parameters(
        Names=[
            "nest_client_id",
            "nest_client_secret",
            "nest_project_id",
            "nest-refresh-token",
            "nest-ff-device-id",
            "nest-sf-device-id"
            "nest-heat-celsius",
            "nest-cold-celsius",
        ],
        WithDecryption=True
    )

    for param in nest_params["Parameters"]:
        if param["Name"] == "nest-refresh-token":
            refresh_token = param["Value"]
        elif param["Name"] == "nest_project_id":
            project_id = param["Value"]
        elif param["Name"] == "nest_client_secret":
            client_secret = param["Value"]
        elif param["Name"] == "nest_client_id":
            client_id = param["Value"]
        elif param["Name"] == "nest-ff-device-id":
            ff_device_id = param["Value"]
        elif param["Name"] == "nest-sf-device-id":
            sf_device_id = param["Value"]
        elif param["Name"] == "nest-heat-celsius":
            heat_celsius = param["Value"]
        elif param["Name"] == "nest-cold-celsius":
            cold_celsius = param["Value"]

    # generate the token using refresh_token
    params = {"client_id": client_id, "client_secret": client_secret,
              "refresh_token": refresh_token, "grant_type": "refresh_token"}
    encoded_args = urlencode(params)
    url = "https://www.googleapis.com/oauth2/v4/token?" + encoded_args
    r = http.request("POST", url)
    response_json = json.loads(r.data.decode("utf-8"))
    access_token = response_json["token_type"] + " " + response_json["access_token"]
    thermostats = [ff_device_id, sf_device_id]

    # setting the thermostat mode OFF or HEATCOOL(ON)
    if event["action"] == "OFF":
        # setting the thermostat mode to OFF using their device ids
        modify_mode(thermostats, "OFF", access_token, project_id)
    elif event["action"] == "ON":
        # setting the thermostat mode to ON using their device ids
        modify_mode(thermostats, "HEATCOOL", access_token, project_id)

        # after turning it ON set the temp so that it does not default to
        # previous low temp
        temp = {"heatCelsius": float(heat_celsius), "coolCelsius": float(cold_celsius)}

        # For some reason set temp is not working randomly and not setting the
        # desired temp. So to avoid that let"s call the set_temp twice
        # as it is idempotent API calls
        for _ in range(2):
            time.sleep(1)
            set_temp(thermostats, temp, access_token, project_id)
