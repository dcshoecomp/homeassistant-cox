To add cox_sensor to your installation, download the latest release zip and copy cox_sensor folder to <config directory>/custom_components/ and add the following to your configuration.yaml file:

Example configuration.yaml entry

```yaml
sensor:
- platform: cox_sensor<br>
  username: YOUR_USERNAME<br>
  password: YOUR_PASSWORD
```

states: <br>
data_used sensor will return the total current usage<br>
remaining_days sensor will return the number of days left in your service plan<br>
percentage_used sensor will return % used of total data<br>

Attributes:<br>
last_update: When cox updated your account usage<br>
data_plan: data allowance<br>
service_end: when your service plan ends<br>
service: Friendly name of your service plan<br>

It is currently set to check every 6 hours. 
