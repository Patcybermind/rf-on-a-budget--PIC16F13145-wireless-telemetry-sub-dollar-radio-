---
title: "PIC CLB based 1 dollar wireless telemetry"
author: "pat/patcybermind"
description: "using a 1 dollar chip to easily transmit telemetry for debugging with no extra hardware"
created_at: "2024-06-29"
---

total hours: 16

## july 6th:
3 hours

I started workign on it but before i fire up the mplab x ide i want to test to see how well harmonics work because the plan of the project is to have harmonics that create a higher frequency carrier that is higher than just the 32mhz max that the clock and logic can provide on the pic. So to do this i started by doing it with an arduino because thats fairly easy to code and although it wont let me turn on and off a pin very fast it can do so at 1mhz which is enough for basic rf. another thing i realise was that it also generated a ton of noise but i later kind of managed to fix it
i uploaded this later but here is what that looks like on an sdr: [here](https://youtube.com/shorts/YGda9Y8YHIw?si=WaVRmfhKILbVXihJ) i also tested different length antennas to see what chagned and stuff which will be useful later

## july 13th:
5 hours:

![](https://files.slack.com/files-tmb/T0266FRGM-F0968LJG456-b62dd6af1c/image_720.png)
