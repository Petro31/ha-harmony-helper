# ha-harmony-helper

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
<br><a href="https://www.buymeacoffee.com/Petro31" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-black.png" width="150px" height="35px" alt="Buy Me A Coffee" style="height: 35px !important;width: 150px !important;" ></a>

Creates binary_sensors that represents separate commands.  Each command is mapped to configured harmony remote activities and devices.  This allows users to create a simple remote in lovelace by simply calling the harmony_helper.send_command service with a binary_sensor as the target.

The state of the binary sensor will be on/off based on the configuration.  For example, if a user has the channel up command mapped on TV and Roku activity, but not the Music activity.  The channel up binary_sensor will only be on during TV and Roku activities.

<h1><a class="title-link" name="installation" href="#installation"></a>Installation</h1>

* Install using HACS, or copy the contents of `custom_components/harmony_helper/` to `<config>/custom_components/harmony_helper/`
* Restart Home Assistant

<h1><a class="title-link" name="configuration" href="#configuration"></a>Configuration</h1>

<h3><a class="title-link" name="advanced (There is no basic configuration)" href="#advanced"></a>Basic</h3>

```
harmony_helper:
  living_room:
    source: remote.living_room
    activity_device_links:
      roku:
        activity: Roku
        device: Roku Ultra
      xbox_one:
        activity: Xbox One
        device: Microsoft Xbox One
      ps4:
        activity: PS4
        device: Sony PS4
      tv:
        activity: TV
        device: Sony TV
    commands:
    - Rewind
    - Play
    - Pause
    - command: FastForward
      name: Forward
    - command: DirectionUp
      name: Up
    - command: DirectionLeft
      name: Left
    - command: OK
      name: Confirm
    - command: DirectionRight
      name: Right
    - command: DirectionDown
      name: Down
    - Back
    - command: ChannelUp
      name: Up
    - command: ChannelDown
      name: Down
    - ChannelPrev
    - "0"
    - "1"
    - "2"
    - "3"
    - "4"
    - "5"
    - "6"
    - "7"
    - "8"
    - "9"
    
    - command: Period
      device_command: "."
      links:
      - tv
      
    - command: Home
      icon: mdi:home
      links:
      - roku
      - tv
      - link: ps4
        device_command: PS
      - link: xbox_one
        device_command: Xbox
        
    - command: Menu
      icon: mdi:menu
      links:
      - link: roku
        device_command: Options*
        icon: mdi:asterisk
      - tv
      - link: ps4
        device_command: Options
      - link: xbox_one
        icon: mdi:xbox-controller-menu
        
    - command: LowerLeft
      links:
      - link: roku
        device_command: Search
      - link: tv
        device_command: Options
        icon: mdi:asterisk
      - link: ps4
        device_command: Info
      - link: xbox_one
        device_command: View
        
    - command: LowerRight
      links:
      - link: roku
        device_command: Exit
      - link: tv
        name: Info
        device_command: TrackId
      - link: ps4
        device_command: Share
      - link: xbox_one
        name: One Guide
        device_command: OneGuide
      
    - command: BottomButton
      name: Confirm
      links:
      - link: ps4
        device_command: Cross
      - link: xbox_one
        device_command: A
        
    - command: RightButton
      name: Back
      links:
      - link: ps4
        device_command: Circle
      - link: xbox_one
        device_command: B
        
    - command: TopButton
      name: Search
      activities:
      links:
      - link: ps4
        device_command: Triangle
      - link: xbox_one
        device_command: Y
        
    - command: LeftButton
      name: Backspace
      links:
      - link: ps4
        device_command: Square
      - link: xbox_one
        device_command: X
```