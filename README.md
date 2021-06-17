Interface to control CAEN power supplies for the 8pi and ULGe detector using a python wrapper to the CAEN C API
Must install : https://www.caen.it/products/caen-hv-wrapper-library/

# Requirements
* Python 3.6+
* CAEN wrapper library
* Network access to CAEN power supply

# Bias
## Bias based on config file settings
The following will bias channel 1 using settings defined in config file (hvps.cfg)
```
hvps_ctrl.py --action bias --channel 1
```

To specify bias voltage on command line, such as bias channel 1 to 2000 volts. This will still
need to read the ramping rate from the config file.
```
hvps_ctrl.py --action bias --channel 1 --bias_voltage 2000
```

# Unbias
To unbias a channel use the following.  This will also read in and apply the ramping rate from the config file.
```
hvps_ctrl.py --action unbias --channel 1
```

# Set Parameter
To set one of the following parameters : ISet, RUp, RDwn, PDwn, IMRange, Trip the action set_param is used.
The following sets the Ramp Down rate (V/s) to be 10 V/s on channel 1
```
hvps_ctrl.py --action set_param --param RDwn --param_value 10 --channel 1
```

# View Status
The status of all channels will be displayed by running hvps_ctrl.py without any parameters

# Config file

# Code Layout
