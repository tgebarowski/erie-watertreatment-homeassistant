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


Sensors exposed by this integration
-----------------------------------

- sensor.erie_watertreatment_last_maintenance - Last maintenance timestamp
- sensor.erie_watertreatment_last_regeneration - Last regeneration timestamp
- sensor.erie_watertreatment_nr_regenerations - Total number of regenerations
- sensor.erie_watertreatment_total_volume - Total volume since device installation (in liters)
- sensor.erie_watertreatment_flow -  Water flow per time period sensor (in liters)
- binary_sensor.erie_watertreatment_low_salt - True when low salt level detected


Exemplary template snippets
---------------------------

### water.yaml:

```yaml
- platform: template
  sensors:
    erie_watertreatment_last_maintenance_formatted_date:
      friendly_name: Last Maintenance Date
      value_template: >
       {{ as_timestamp(states('sensor.erie_watertreatment_last_maintenance')) | timestamp_custom("%d/%m/%Y @ %H:%M:%S", True) }}

- platform: template
  sensors:
    erie_watertreatment_last_regeneration_formatted_date:
      friendly_name: Last Regeneration Date
      value_template: >
       {{ as_timestamp(states('sensor.erie_watertreatment_last_regeneration')) | timestamp_custom("%d/%m/%Y @ %H:%M:%S", True) }}

- platform: template
  sensors:
    erie_watertreatment_time_until_maintenance:
      friendly_name: Time Until Maintenance
      value_template: >
       {%- set days = (( as_timestamp(states('sensor.erie_watertreatment_last_maintenance')) + 3600 * 24 * 30 * 12 - as_timestamp(now()) )/ (3600*24)) | round(0, "ceil") -%}
       {% if days > 30 %}
       {{ (days / 30) | round(0, "ceil") }} months
       {% elif days > 14 %}
       {{ days }} days
       {% else %}
       {{ days }} days ❗️
       {% endif %}
```

Exemplary Lovelace cards:
------------------------

### Infobox

<img src="https://github.com/tgebarowski/erie-watertreatment-homeassistant/blob/main/img/entities-card.png" width="500">

```yaml
cards:
  entities:
    - entity: sensor.erie_watertreatment_warnings
      name: Warnings
        - entity: sensor.erie_watertreatment_total_volume
          name: Total water consumption
          icon: mdi:water
        - entity: sensor.erie_watertreatment_last_regeneration_formatted_date
          name: Last regeneration
          icon: mdi:calendar-clock
        - entity: sensor.erie_watertreatment_nr_regenerations
          name: Regenerations count
          icon: mdi:recycle
        - entity: sensor.erie_watertreatment_last_maintenance_formatted_date
          name: Last service
          icon: mdi:calendar-clock
        - entity: sensor.erie_watertreatment_time_until_maintenance
          name: Time till next service
          icon: mdi:calendar-clock

```

### Displaying water consumption during last 7 days:

<img src="https://github.com/tgebarowski/erie-watertreatment-homeassistant/blob/main/img/water-flow-week.png" width="700">

```yaml
cards:
  - type: custom:mini-graph-card
    entities:
      - entity: sensor.erie_watertreatment_flow
        icon: mdi:water
        aggregate_func: sum
        name: "Water consumption"
    name: Daily water consumption (last 7 days)
    hours_to_show: 168
    group_by: date
    show:
      graph: bar
      labels: true
    color_thresholds:
      - value: 0
        color: "#f5fdff"
      - value: 1
        color: "#3295a8" 
    style: |
      ha-card {
        --ha-card-border-radius: '8px';
        --ha-card-border-size: '1px';
        --ha-card-border-color: rgba(255, 255, 0, 0);
        --ha-card-box-shadow: 'none';
      }                 
```

### Displaying water consumption during last 24 hours:

<img src="https://github.com/tgebarowski/erie-watertreatment-homeassistant/blob/main/img/water-flow-24hrs.png" width="700">


```yaml
cards:
  - type: custom:mini-graph-card
    entities:
      - entity: sensor.erie_watertreatment_flow
        aggregate_func: sum
        name: "Water consumption"
    name: Last 24 hours water consumption
    hours_to_show: 24
    group_by: hour
    hour24: true
    show:
      graph: bar
      labels: true
    color_thresholds:
      - value: 0
        color: "#f5fdff"
      - value: 1
        color: "#3295a8"               
    style: |
     ha-card {
        --ha-card-border-radius: '8px';
        --ha-card-border-size: '1px';
        --ha-card-border-color: rgba(255, 255, 0, 0);
        --ha-card-box-shadow: 'none';
     }  
```

