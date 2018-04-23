# Code Dependencies
---

### AI Stuff
 * ROS
 * Tensorflow
 * OpenCV

### Utilities 
---

**ServoBlaster** controls the servos

```
git clone https://github.com/richardghirst/PiBits.git
cd PiBits/ServoBlaster/user
sudo make install
```

[WiringPi](http://wiringpi.com/download-and-install/) provides a C library for 
interfacing with GPIO, as well as nice commandline tools.

``` sudo apt-get install i2c-tools libi2c-dev ```

_Note: be sure to enable i2c in raspi-config_

# Other helpful things
---

``` sudo apt install screen vim sl ```

**toggle\_wifi\_access\_point**: allows for nice clean switching between WiFi access point and client.

```
sudo apt update
sudo apt upgrade
git clone https://github.com/openrocketryinitiative/utilities.git
cd utilities/toggle_wifi_access_point
sudo chmod +x rPi3-ap-setup.sh
sudo ./rPi3-ap-setup.sh <yourPassword> <yourAPName>
sudo reboot
```

