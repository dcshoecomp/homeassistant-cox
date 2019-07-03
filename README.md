To add cox_sensor to your installation, download the latest release zip and copy cox_sensor folder to <config directory>/custom_components/ and add the following to your configuration.yaml file:

Example configuration.yaml entry

```yaml
sensor:
- platform: cox_sensor<br>
  username: YOUR_USERNAME<br>
  password: YOUR_PASSWORD
```
key	description<br>
states: sensor will return the total current usage

