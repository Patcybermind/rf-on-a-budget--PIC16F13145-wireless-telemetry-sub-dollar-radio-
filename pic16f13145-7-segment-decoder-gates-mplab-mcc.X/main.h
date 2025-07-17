#ifndef MAIN_H
#define MAIN_H

#include <stdint.h>

extern volatile uint8_t start_tx;
extern volatile uint8_t tx_data;
extern volatile uint8_t tx_bit_index;
extern volatile uint8_t half_bit_phase;

// Add these global or static variables somewhere in your code
extern uint8_t sync_sequence;
extern uint8_t sync_bit_index;
extern uint8_t sending_sync; // flag: 1 = sending sync, 0 = sending normal data
#endif // MAIN_H
