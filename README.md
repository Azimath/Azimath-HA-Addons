# Azimath-HA-Addons
Installing on HAOS is easy: From the addons page store, select the 3 dots at top right, select "Repositories", paste the github URL into the field, and click add. Once HA grabs the repo the addons should show up on the store, then just install the one you want.

If you don't have the HA supervisor you can still use the DMX receiver (see below)

## DMX_Receiver
Allows receiving DMX messages over sACN and mapping them to binary, monochrome, RGB, and RGBW lights.

To use, open the configuration page and set up the map (check "Show unused optional configuration options" if you don't see it). The map tells the addon which channels control which lights. Here's an example of configuring some lights:

```
- entity: lights.rgb_lamp
  channels:
    - 1
    - 2
    - 3
- entity: lights.rgbw_lamp
  channels:
    - 1
    - 255
    - 3
    - 4
```

Note that lights can share channels, and if you don't want to use a particular channel you can just set some high channel number that won't get set by anything. Channel numbers start at 1 and go up to 512.

Once configured, save the config, go back to the info screen and start the addon. 

Stopping the addon when not in use is a good idea, as sACN doesn't have authentication, so anything on the network could send a packet and flip the mapped lights on or off while the addon is running. Lights not mapped and other parts of HA won't be affected by this.

### Standalone operation (if you can't use HA addons)
If you want to run the DMX receiver standalone, you can! 
1. With a recent ish version of python3, pip install `sacn` and `homeassistant-api`. 
2. Open your HA user profile and create a long-lived access token. 
3. Clone the repo and create a folder inside `dmx_receiver` named `data`
4. Create a file named `options.json` in the `data` folder. This file has the same content as the YAML map but in JSON format (example below).
5. Set the environment variable `SUPERVISOR_TOKEN` to the access token.
6. From the `dmx_receiver` folder, run `python3 dmx_receive.py https://your-home-assistant-url:port/api`

The standalone mode prints all the commands it gets so it can be useful for debugging.

Example `options.json`:
```
{
    "map": [
      {
        "entity": "light.athom_rgb_light_strip",
        "channels": [
          1,
          255,
          3
        ]
      },
      {
        "entity": "light.athom_rgb_light_strip_2",
        "channels": [
          2,
          255,
          3
        ]
      }
    ],
    "universe" : 1
}
```

If you use VS code, you can make launching and debugging easy by creating a launch.json with the default "run current python file" and adding these lines to the launch configuration:

```
"env": {"SUPERVISOR_TOKEN" : "your token"},
"args": ["https://your-HA-url:port/api"]
```