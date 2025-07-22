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
10 hours:

Today i spent a lot of time first trying to get the ide to work and compiling and upoading using a tutorial but i ended up just using a pre made tutorial project as a template which worked Because before
it did kind of work but not really because i couldnt get the output pins to work. they would only work if i set them to be the clk out pins but that wast not really an option that would work because although it did generate a carrier that i could see in the sdr there wasnt reallty a good way for me to turn the carrier on and off to encode data. Anywas after a while of strugleing  i could finally turn it on and off using logic. I played around with how it would turn on and off and wheter it would be on high or off high, if id invert the output or not if id use an and or an or to activate the carrier or not because that would actually change the signal strength of the received radio. i imagine that that is because of the way its layed out once the design is converted into a bitstream which is interesting
but i think i ended with the most signal strength / drive strength i could get which using a small wire as the antenna was around -55db max when really close. which is under the -40db legal limit. with a longer antenna you do kind of get close to -40db because at 96mhz its much more efficient to use a 75cm antenna which is quarter wavelength than a 8cm antenna. After that i started trying to encode data.

I decided to go with manchester encoding because from the research i had done previously it seemed to be the most reliable when it works properly. It basically works by detecting falling and rising edges in the carrier being turned on or off

after that i wrote a python script that interfaces with the rtl sdr and outputs 1 and 0 which can be imported into pulseview and decoded using their included tool. I also made a python script that could do it in real time but with the time but it worked less well.

<img width="1578" height="477" alt="image (2)" src="https://github.com/user-attachments/assets/0b1c8388-ef16-4ff1-9ae3-46e8ab4242cc" />

0b11111111 as synch and preamble followed by a databyte

<img width="1521" height="771" alt="image (3)" src="https://github.com/user-attachments/assets/028221e9-6211-46e4-8022-f3e25be1b4c3" />

what it looks like on sdr

## july 17th
3 hours
As i said it wasnt working well so i had to fix a few things with timings in the hardware timers and in the python script that converts the sdr readings into 1 and 0 but it ended up working after a while!
its pretty cool!
<img width="681" height="404" alt="image (5)" src="https://github.com/user-attachments/assets/72364db2-48fc-4474-a10f-8179c80940cf" />


