# NDRxxx CommandLine

NDRxxx CLI Utility for sending JSON commands to radios supported through CyberRadioDriver. 

Contributing Authors:
    - Brandon Smith

# Installation

## No Frills Use the Script
```sh
git clone https://github.com/CyberRadio/NDRCommandLine.git
cd NDRCommandLine/ndrcommandline/scripts/
python3 ndrxxx_command_line.py -r ndr358 -i 192.168.0.10
```
## Installation from internal APT
```
sudo apt install python3-ndrcommandline 
```

## Installation from Source
```
makedeb -3 ndrcommandline
sudo dpkg -i <debian-name>
```

# Using the program
```sh
python3 ndrxxx_command_line.py -r ndr358 -i 192.168.0.10
>> qtuner id 0
TX: {'cmd': 'qtuner', 'params': {'id': 0}}
RX: {
    "aal": -32.0,
    "aas": -1.0,
    "aat": 1,
    "adl": -48.0,
    "ads": 0.0,
    "adt": 1,
    "all": 0,
    "asp": 0,
    "atten": 0,
    "aul": -40.0,
    "enable": false,
    "fnr": true,
    "freq": 1000000000,
    "id": 0,
    "ifatten": 14,
    "mode": "manual",
    "psmode": "wband",
    "rf1atten": 0,
    "rf2atten": 13
}
>> tuner id 0 freq 1000e6
TX: {'cmd': 'tuner', 'params': {'id': 0, 'freq': 1000000000}}
RX: {"cmd":"tuner","success":true,"msg":282,"rsp":819}
```
The Tool expects the following format:

>> <cmd> <param> <value>

There must be a space between <cmd> and <param> and <param> and <value>

You may place as many <param> <value> pairs on the line as you need

```sh
>> tuner id 0 freq 1000e6 enable true mode "manual"
```


