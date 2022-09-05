# DMX_Receiver
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