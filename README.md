erie_watertreatment
===================

Erie Connect IQSoft26 experimental integration for Home Assistant (mainly for my own use and experiments).
No support is given.

Integration works by pooling Erie Connect API every 90 seconds. It uses API client from this repo:
https://github.com/tgebarowski/erie-connect

Installation
------------

1. Copy erie_watertreatment directory to custom_components/ directory of your Home Assistant configuration
2. In HomeAssistant choose Configuration | Integrations | Add (Orange + circle)
3. In opened dialog search for Erie Watertreatment IQ26
4. Provide login and password for Erie Connect 
5. Upon successful login new sensor will be exposed


Exposed sensors
---------------

- sensor.erie_watertreatment_flow - Display current water flow
- sensor.erie_watertreatment_last_maintenance - Last maintenance timestamp
- sensor.erie_watertreatment_last_maintenance_formatted_date - Last maintenance formatted date
- sensor.erie_watertreatment_last_regeneration - Last regeneration timestamp
- sensor.erie_watertreatment_last_regeneration_formatted_date - Last maintenance formatted date
- sensor.erie_watertreatment_nr_regenerations - Total number of regenerations
- sensor.erie_watertreatment_time_until_maintenance - Time until next maintenance (not working)
- sensor.erie_watertreatment_total_volume - Total volume since installation