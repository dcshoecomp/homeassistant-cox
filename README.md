# Description

Contains a sensor and a switch. The sensor returns relevant information about cox data usage plan. The switch when toggled on will immediately initiate a modem(or router) reboot, then turn back off. 
 
# Changes

Sensor Version | Changes
:--- | :---
 v0.0.6 | fixed expected_usage sensor
<strike>v0.0.4</strike> | added expected_usage sensor
<strike>v0.0.3</strike> | fixed service_end variable calls in if statement
<strike>v0.0.2</strike> | added more sensors and attributes
<strike>v0.0.1</strike> | initial commit

Switch Version | Changes
:--- | :---
 v0.0.1 | Initial commit of reboot switch


# cox_sensor

To add cox_sensor to your installation, download the latest release zip and copy cox_sensor folder to `<config directory>/custom_components/` and add the following to your configuration.yaml file:

**Example configuration.yaml entry**
```yaml
sensor:
- platform: cox_sensor
  username: YOUR_USERNAME
  password: YOUR_PASSWORD
switch:
- platform: cox_sensor
  username: YOUR_USERNAME
  password: YOUR_PASSWORD
```
**Sensor Configuration variables:**  

key | description  
:--- | :---  
**username** | YOUR_USERNAME
**password** | YOUR_PASSWORD

**Switch Configuration variables:**  

key | description  
:--- | :---  
**username** | YOUR_USERNAME
**password** | YOUR_PASSWORD
**resources** | (Optional list) Default: reboot


**states:** 

sensor state | description
:-- | :--
data_used sensor | returns the total byte usage
remaining_days sensor | returns the number of days left in your service plan
percentage_used sensor | returns % used of total data
expected_usage | returns the % of data you are expected to use to hit 100% on service_end

attribute | description  
:--- | :---  
last_update | When cox updated your account usage
data_plan | data allowance
service_end | when your service plan ends
service | Friendly name of your service plan
