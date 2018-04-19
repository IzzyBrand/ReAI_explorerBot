# Code Dependencies
---
**ServoBlaster** controls the servos

```
git clone https://github.com/richardghirst/PiBits.git
cd PiBits/ServoBlaster/user
sudo make install
```
### AI Stuff
 * ROS
 * Tensorflow
 * OpenCV

# Utilities 
---
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
### Other helpful things

``` sudo apt install screen vim sl ```