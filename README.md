# ha-harmony-helper

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
<br><a href="https://www.buymeacoffee.com/Petro31" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-black.png" width="150px" height="35px" alt="Buy Me A Coffee" style="height: 35px !important;width: 150px !important;" ></a>

Creates a `binary_sensor` that represents that commands are available. This will also create `button` entites for each configured command. Each command is mapped to configured harmony remote activities and devices.  The commands will produce warnings in the logs if there is no active harmony activity or if the harmony activity does not make use of the command.  If the activity and command are configured, the button will simply send the device the configured command based on the current activity.  This essentially mimics the hand held remote buttons.

The state of the binary sensor will be on/off based on an activity with commands.  If the activity has no commands, the binary sensor will be off.  If the activity has commands, it will be on.  This was specifically designed to hide/show buttons in a dashboard with the conditional card.

<h1><a class="title-link" name="installation" href="#installation"></a>Installation</h1>

* Install using HACS, or copy the contents of `custom_components/harmony_helper/` to `<config>/custom_components/harmony_helper/`
* Restart Home Assistant

<h1><a class="title-link" name="configuration" href="#configuration"></a>Configuration</h1>

<h3><a class="title-link" name="advanced" href="#advanced"></a>Advanced (There is no basic configuration)</h3>

This configuration shows all options for yaml.  Sorry, I'm not going to write out a config section for this.  If you happen to find this integration, you are essentially on your own with the yaml.  Do not use this integration if you do not understand yaml or Harmony remotes in HA.

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