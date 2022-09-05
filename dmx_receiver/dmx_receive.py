import os, time, sys
import json

import sacn

from homeassistant_api import Client

print("Starting DMX receiver")

if "SUPERVISOR_TOKEN" not in os.environ:
    print("Please set SUPERVISOR_TOKEN with your bearer token")
    quit()

options = None

standalone = True

HAURL = "http://supervisor/core/api"
if len(sys.argv) > 1:
    # Running standalone
    HAURL = sys.argv[1]
    with open("data/options.json", "r") as optionsfile:
        options = json.load(optionsfile)
else:
    # Running under homeassistant
    standalone = False
    with open("/data/options.json", "r") as optionsfile:
        options = json.load(optionsfile)

def log(thing):
    if standalone:
        print(thing)

map = options["map"]
universe = options["universe"]
callers = []

print(f"Connecting to HA with URL {HAURL}")

def createFloatCaller(entity, channels, mode):
    if len(channels) == 1:
        def caller(dmxData):
            value = dmxData[channels[0]-1]
            if value == 0:
                light.turn_off(entity_id=entity)
                log(f"Set {entity} to off")
            else:
                data = {mode : value}
                light.turn_on(entity_id=entity, transition=0.0, **data)
                log(f"Set {entity} to {value}")
        return caller
    else:
        def caller(dmxData):
            values = [dmxData[c-1] for c in channels]
            if sum(values) == 0:
                light.turn_off(entity_id=entity)
                log(f"Set {entity} to off")
            else:
                data = {mode : values}
                light.turn_on(entity_id=entity, transition=0.0, **data)
                log(f"Set {entity} to {values}")
        return caller

def createBinaryCaller(entity, channel):
    def caller(dmxData):
        if dmxData[channel-1] < 127:
            light.turn_off(entity_id=entity)
            log(f"Set {entity} to off")
        else:
            light.turn_on(entity_id=entity)
            log(f"Set {entity} to on")
    return caller

with Client(HAURL, os.environ["SUPERVISOR_TOKEN"]) as client:
    print("Connected to HA!")

    light = client.get_domain(domain_id="light")

    for i, e in enumerate(map):
        s = client.get_state(entity_id=e["entity"])
        cm = s.attributes['supported_color_modes']
        print(f"Configuring {e['entity']}")
        if "rgb" in cm:
            if len(e["channels"]) != 3:
                print(f"RGB Light {e['entity']} should have 3 channels not {len(e['channels'])} channels")
                quit()
            callers.append(createFloatCaller(e['entity'], e["channels"], "rgb_color"))
        elif "rgbw" in cm:
            if len(e["channels"]) != 4:
                print(f"RGBW Light {e['entity']} should have 4 channels not {len(e['channels'])} channels")
                quit()
            callers.append(createFloatCaller(e['entity'], e["channels"], "rgbw_color"))
        elif "brightness" in cm:
            if len(e["channels"]) != 1:
                print(f"Monochrome Light {e['entity']} should have 1 channel not {len(e['channels'])} channels")
                quit()
            callers.append(createFloatCaller(e['entity'], e["channels"], "brightness"))
        elif "onoff" in cm:
            if len(e["channels"]) != 1:
                print(f"Binary Light {e['entity']} should have 1 channel not {len(e['channels'])} channels")
                quit()
            callers.append(createBinaryCaller(e['entity'], e["channels"][0]))
        else:
            print(f"{e['entity']} only has non-supported color modes {cm}")

    #Bind and start ACN receiver
    receiver = sacn.sACNreceiver()
    receiver.start()
    print("ACN receiver thread started")

    # define ACN callback function
    @receiver.listen_on('universe', universe=universe)  # listen
    def callback(packet):  # packet type: sacn.DataPacket
        log("Got dmx data!")
        for c in callers:
            c(packet.dmxData)

    print("ACN receiver callback added")
    # optional: if you want to use multicast use this function with the universe as parameter
    #receiver.join_multicast(1)

    while True:
        time.sleep(1)
    receiver.stop()
    print("Done")
