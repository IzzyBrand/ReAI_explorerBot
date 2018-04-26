# Code Dependencies
---

## AI Stuff

 * ROS
 * OpenCV

I wouldn't recommend trying to install ROS and OpenCV yourself on a Pi. Luckily, RosBots has a [Raspbian Stretch Lite image](https://medium.com/@rosbots/ready-to-use-image-raspbian-stretch-ros-opencv-324d6f8dcd96) that comes with prebuilt with ROS Kinetic and OpenCV.

**To Install Tensorflow on a pi**

```
wget https://github.com/samjabrahams/tensorflow-on-raspberry-pi/releases/download/v1.1.0/tensorflow-1.1.0-cp27-none-linux_armv7l.whl
sudo pip install tensorflow-1.1.0-cp27-none-linux_armv7l.whl
```

## Utilities 

Be sure to enable i2c in raspi-config. You'll also need

```
sudo apt install i2c-tools libi2c-dev
pip install picamera 
```

**ServoBlaster** controls the servos

```
cd ~
git clone https://github.com/richardghirst/PiBits.git
cd ~/PiBits/ServoBlaster/user
sudo make install
```

[**WiringPi**](http://wiringpi.com/download-and-install/) provides a C library for 
interfacing with GPIO, as well as nice commandline tools.

```
cd ~
git clone git://git.drogon.net/wiringPi
cd ~/wiringPi
./build
```

**vl6180_pi** interfaces with the vl6180 time-of-flight distance sensors. This is already in our repo (see `ReAI_explorerBot/vl6180_pi/readme.md ` for info on that library). To build it and then build our tof-flight-sensor script you'll need to run

```
cd ~/ReAI_explorerBot/vl6180_pi
make
sudo make install
cd ~/ReAI_explorerBot
cc tof_test.c -o tof_test -lvl6180_pi -lwiringPi
```


# Other helpful things
---

``` sudo apt install screen vim sl ```

**toggle\_wifi\_access\_point**: allows for nice clean switching between WiFi access point and client.

```
sudo apt update
sudo apt upgrade
cd ~
git clone https://github.com/openrocketryinitiative/utilities.git
cd ~/utilities/toggle_wifi_access_point
sudo chmod +x rPi3-ap-setup.sh
sudo ./rPi3-ap-setup.sh <yourPassword> <yourAPName>
sudo reboot
```



