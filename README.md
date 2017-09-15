# alice-hardware
The hardware specification for alice. Including a library to controll the hardware.

## Installation

Install dependencies

```bash
sudo apt-get install python screen
```

Clone the repository into the folder /home/pi/git.

```bash
# If not using /home/pi/git folder you have to fix the launch.sh script with the correct path.
cd /home/pi/git
git clone https://github.com/penguinmenac3/alice-hardware.git
```

You can make alice-harware automatically launch on boot by adding the following to your rc.local

```bash
sudo nano /etc/rc.local
sudo -su pi /home/pi/git/alice-hardware/launch.sh
```

## Usage

Simply run the code on your raspberrypi inside alicebot.

```bash
# cd /path/to/repo/alice-hardware
python main.py
```

Then connecct with the alice-ai from your laptop or also on the raspi. For that see the doc of the ai.

You can also use the alice-remote to control the robot manually.

## Manufacturing AliceBot Hardware

TOOD coming sooner or later
### Wiring-Diagram

![Wiring diagram](https://github.com/penguinmenac3/alice-hardware/blob/master/Wiring%20Alice.png?raw=true)
