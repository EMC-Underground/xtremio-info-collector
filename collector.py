#!/usr/bin/python
import json
import sys
import requests
import time
import coloredlogs
import logging
import os

start_time = time.time()

# First we read in the environement variables telling us a XMS IP address,
# username, password and where we want to send the information to (API endpoint)

try:
    xms_ip          = os.environ['XMS_IP']
    xio_name        = os.getenv("XIO_NAME", "")
    username        = os.environ['USERNAME']
    password        = os.environ['PASSWORD']
    target_api_url  = os.environ['TARGET_API_URL']
    log_level       = os.getenv("LOG_LEVEL", "INFO")
    cert            = os.getenv("VERIFY_CERT", "/etc/ssl/certs/ca-certificates.crt")
    if cert == "False":
        cert = False
except:
    print("invalid environmental variables passed")
    sys.exit(1)

# Setup the logger as alfred
alfred = logging.getLogger("Xtremio_Collector")
coloredlogs.install(level=log_level, logger=alfred)
alfred.info("Begining Xtremio_Collector script")

def get_cluster(ip_address, username, password):
    """Method retrieve all pertinent data about the XtremIO cluster

    Args:
        ip_address: Ip address of the XMS
        username: Username to authenticate with XMS
        password: Password to authenticate with XMS

    Returns:
        resp['content']: dict containing all the cluster data
    """
    url="https://{0}/api/json/v2/types/clusters/1".format(ip_address)
    alfred.debug("Making a GET request to: {0}".format(url))
    try:
        resp=requests.get(url, auth=(username, password), verify=False).json()
    except:
        alfred.error("Failed to make api call to {0}".format(url))
        sys.exit(1)

    return resp['content']


def calc_capacity(total_space, space_in_use):
    """Method to calculate the appropriate capacities of the XtremIO cluster

    Args:
        total_space: usable space of the array
        space_in_use: space used on the array

    Returns:
        capacity: dict containing the usable/consumed/avail capacities
                    of the array
    """
    capacity = {}
    capacity["usable_tb"]    = float(total_space) / 2**30
    capacity["consumed_tb"]  = float(space_in_use) / 2**30
    capacity["available_tb"] = capacity["usable_tb"] - capacity["consumed_tb"]

    return capacity


def send_to_target_api(payload, verify_cert):
    """Method to send full payload to API endpoint

    Sends the payoad to the api endpoint specificied in our
    environement variable captured in the begining of the script.
    This should be the last method called in the logic.

    Args:
        payload: dict containing the fields required by our storage API
        verify_cert: The location of certs or False to ignore self signed

    Returns:
        None
    """
    alfred.info("Making post request to: {0}".format(target_api_url))
    json_payload = json.dumps(payload)
    try:
        r = requests.post(target_api_url, data=json_payload, verify=cert)
    except requests.exceptions.RequestException as e:
        alfred.critical("Critical error trying to post to api: {0}".format(e))
        alfred.info("Finished VNX_Collector script in {0} seconds"
                .format("%.3f" % (time.time() - start_time)))
        sys.exit(1)
    except requests.exceptions.HTTPError as err:
        alfred.error("HTTP error trying to post to api: {0}".format(err))
        alfred.info("Finished VNX_Collector script in {0} seconds"
                .format("%.3f" % (time.time() - start_time)))
        sys.exit(1)


def main():

    xtremio = get_cluster(xms_ip,
                          username,
                          password)

    capacities = calc_capacity(xtremio["ud-ssd-space"],
                               xtremio["ud-ssd-space-in-use"])

    array_details = {}

    array_details["array_name"]                 = xtremio["name"]
    array_details["serial_number"]              = xtremio["sys-psnt-serial-number"]
    array_details["vendor"]                     = "DellEMC"
    array_details["model"]                      = "Xtremio {0}".format(xtremio["size-and-capacity"])
    array_details["tier"]                       = "Performance"
    array_details["capacity"]                   = {}
    array_details["capacity"]["usable_tb"]      = capacities["usable_tb"]
    array_details["capacity"]["available_tb"]   = capacities["available_tb"]
    array_details["capacity"]["consumed_tb"]    = capacities["consumed_tb"]

    alfred.debug("Getting read to send payload to API endpoint. "+
                "Here is the payload: {0}".format(json.dumps(array_details)))

    # Post the array_details to the API Endpoint
    send_to_target_api(array_details,cert)

    alfred.info("Finished Xtremio_Collector script in {0} seconds"
                .format("%.3f" % (time.time() - start_time)))

    sys.exit(0)

if __name__ == "__main__":
    main()
