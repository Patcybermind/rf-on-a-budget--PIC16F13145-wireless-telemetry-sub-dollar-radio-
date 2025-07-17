 /*
 * MAIN Generated Driver File
 * 
 * @file main.c
 * 
 * @defgroup main MAIN
 * 
 * @brief This is the generated driver implementation file for the MAIN driver.
 *
 * @version MAIN Driver Version 1.0.0
*/

/*
© [2025] Microchip Technology Inc. and its subsidiaries.

    Subject to your compliance with these terms, you may use Microchip 
    software and any derivatives exclusively with Microchip products. 
    You are responsible for complying with 3rd party license terms  
    applicable to your use of 3rd party software (including open source  
    software) that may accompany Microchip software. SOFTWARE IS ?AS IS.? 
    NO WARRANTIES, WHETHER EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS 
    SOFTWARE, INCLUDING ANY IMPLIED WARRANTIES OF NON-INFRINGEMENT,  
    MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT 
    WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE, 
    INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY 
    KIND WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF 
    MICROCHIP HAS BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE 
    FORESEEABLE. TO THE FULLEST EXTENT ALLOWED BY LAW, MICROCHIP?S 
    TOTAL LIABILITY ON ALL CLAIMS RELATED TO THE SOFTWARE WILL NOT 
    EXCEED AMOUNT OF FEES, IF ANY, YOU PAID DIRECTLY TO MICROCHIP FOR 
    THIS SOFTWARE.
*/
#include "mcc_generated_files/system/system.h"

/*
    Main application
*/
#include <xc.h> // Standard header for PIC microcontroller registers




// === Part 1: Initialization Function ===
// Call this function once from your main() routine.

void init_100hz_timer(void) {
    // --- Step 1: Configure the output pin (RC0) ---
    LATCbits.LATC0 = 0;     // Start with the pin low
    TRISCbits.TRISC0 = 0;     // Set RC0 as an output
    ANSELCbits.ANSC0 = 0;   // IMPORTANT: Disable analog function on RC0

    // --- Step 2: Configure Timer1 for a 5ms interrupt period ---
    // Goal: 100 Hz output -> Toggle every 5ms (0.005s)
    // Clock Source: LFINTOSC (~31,000 Hz)
    // Prescaler: 1:1
    // Ticks needed = 0.005s * 31,000 Hz = 155 ticks.
    // Timer preload value = 65536 - 155 = 65381 (0xFF05)

    // ***FIXED***: Select LFINTOSC as the clock source for Timer1 using the T1CLK register.
    // The value 0b00100 corresponds to LFINTOSC in Table 22-4 on page 241.
    T1CLK = 0b00100;

    // ***FIXED***: Configure Timer1 Control Register with the correct bit names.
    // The TMR1CS bits are not in T1CON for this chip; that's handled by T1CLK now.
    T1CONbits.CKPS = 0b00;    // Use 'CKPS' for the Prescaler (1:1)
    T1CONbits.RD16 = 1;       // Enable 16-bit Read/Write mode
    
    // --- Step 3: Enable Interrupts ---
    PIR1bits.TMR1IF = 0;      // Clear the Timer1 interrupt flag
    PIE1bits.TMR1IE = 1;      // Enable Timer1 overflow interrupt
    INTCONbits.PEIE = 1;      // Enable Peripheral Interrupts
    INTCONbits.GIE = 1;       // Enable Global Interrupts

    // --- Step 4: Preload timer and turn it on ---
    TMR1H = 0xF9;
    TMR1L = 0x30;             // Low byte of 57686

    T1CONbits.TMR1ON = 1;     // Start Timer1
}


// === Part 2: Interrupt Service Routine (ISR) ===
// This function will be called automatically every 5ms.



// === Example main() function ===

volatile uint8_t tx_data = 0b10110010;   // Data byte to send
volatile uint8_t tx_bit_index = 0;       // Current bit index (0?7)
volatile uint8_t half_bit_phase = 0;     // 0 = first half, 1 = second half
volatile uint8_t start_tx = 0;           // Set to 1 externally to begin sending
volatile uint8_t manchester_bit = 0;       // The current bit to encode (0 or 1)
     // 0 = first half, 1 = second half

// Add these global or static variables somewhere in your code
uint8_t sync_sequence = 0b11111111;
uint8_t sync_bit_index = 0;
uint8_t sending_sync = 1; // flag: 1 = sending sync, 0 = sending normal data
int main(void)
{
    SYSTEM_Initialize();
    init_100hz_timer();

    // If using interrupts in PIC18 High/Low Priority Mode you need to enable the Global High and Low Interrupts 
    // If using interrupts in PIC Mid-Range Compatibility Mode you need to enable the Global and Peripheral Interrupts 
    // Use the following macros to: 

    // Enable the Global Interrupts 
    //INTERRUPT_GlobalInterruptEnable(); 

    // Disable the Global Interrupts 
    //INTERRUPT_GlobalInterruptDisable(); 

    // Enable the Peripheral Interrupts 
    //INTERRUPT_PeripheralInterruptEnable(); 

    // Disable the Peripheral Interrupts 
    //INTERRUPT_PeripheralInterruptDisable(); 
    
    CLBSWINL = 0;
    
    while(1)
    {
        __delay_ms(1000);         // 1000 is 1s
        
        tx_data = 0b10110010;
        
        sending_sync = 1;
        sync_bit_index = 0;
        tx_bit_index = 0;
        start_tx = 1;
        
        __delay_ms(1500);         // 1000 is 1s
    }    
}