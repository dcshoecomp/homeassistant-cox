Version | Changes
:--- | :---
 v0.0.5 | fixed expected_usage sensor
<strike>v0.0.4</strike> | added expected_usage sensor
v0.0.3 | fixed service_end variable calls in if statement
<strike>v0.0.2</strike> | added more sensors and attributes
v0.0.1 | initial commit

# cox_sensor

To add cox_sensor to your installation, download the latest release zip and copy noaa_alerts folder to `<config directory>/custom_components/` and add the following to your configuration.yaml file:

**Example configuration.yaml entry**
```yaml
sensor:
- platform: cox_sensor<br>
  username: YOUR_USERNAME<br>
  password: YOUR_PASSWORD
```
**Configuration variables:**  

key | description  
:--- | :---  
**username** | YOUR_USERNAME
**password** | YOUR_PASSWORD

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
