# Wireless on a budget

This project was built for microchip's configurable logic block design challenge and was published [here](https://maker.pro/configurable-logic-block/projects/wireless-on-a-budget)

It uses a PIC16f13145 curiosity nano dev board which is a dev board for a configurable logic bloc chip.

using no external hardware it transits digital data that can then be picked up and decoded on another radio.

For more details visit my [post](https://maker.pro/configurable-logic-block/projects/wireless-on-a-budget) !

## How it works:
### Encoding:
The configurable logic uses logic to turn on and off a pin conected to wire which acts as an antenna forming a square wave which causes harmonics allowing us to transmit at 96mhz. This is our carrier.
Then we use timers to decide when to turn on or off the the carrier. We use on off keying which means the carrier is either on or off and to increase resilience to timing problems we use manchester encoding.
Manchester encoding works by using edges or transitions in aplitude levels to encode 1 and 0. In our case we use the following:

bit == 0: outputs 1 then 0 → High to Low → IEEE Manchester 0

bit == 1: outputs 0 then 1 → Low to High → IEEE Manchester 1
In a spectrogram it looks like this:

<img width="851" height="904" alt="image (3)" src="https://github.com/user-attachments/assets/625f9570-cfd8-48d4-bd37-3add1084dfbd" />


When translated to 1 and 0 to be decoded it looks like this:

<img width="681" height="404" alt="image (4)" src="https://github.com/user-attachments/assets/a85b2402-9da8-44e2-98e0-8eae88ddfdf7" />

We use a sync sequence before each data byte. in this case being 0b11111111. This allows the decoder to understand the timing and synchronise the phase of the manchester encoding.

In this example its transmitting 8 bits per second but it could be much faster, this was done so you could see the encoding in the spectrogram.

### Antenna
You could get real fancy and use a real 100mhz fm antenna but for our case we just need a wire that will radiate the rf carrier.
Ideally the wire would be 1/4th the wavelength of the carrier which at around 100mhz is around 75cm but thats relatively long and for short ranges we can afford to make our antenna much smaller even if it costs us signal strength.
In my tests i used a 8cm 22awg wire another good thing is that having a short wire will help filter out out of band frequencies such as our original 32mhz signal that creates our 96 mhz harmonic. Though admitedly, at the power level we are transmitting it doesnt matter
that much.

### Decoding and receiving
I used an rtl-sdr and I used a python script (main.py) to read samples at 512hz for 8bps and then convert them to digital 1s or 0s which are written to test.txt for me to open on pulseview using the import digital data or binary data option.
I can then use the OOK and manchester decoding function that's integrated in pulseview. You could also do this using python directly but then its harder to visualise what's going on. In an earlier commit it did do that though.

## how to use the code
* sync_sequence : defines the sync sequence default is 0b11111111
* start_tx : set to 1 to start tx
* sending_sync : set to 1 when you send sync (otherwise only the txbyte wil be sent upon setting start_tx to 1

If you want to change the bitrate you can do so by changing the high and low bytes of the timer defined as 100hz timer even though its only 16hz by default

