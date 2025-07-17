/**
 * Interrupt Manager Generated Driver File
 *
 * @file interrupt.c
 * 
 * @ingroup interrupt 
 * 
 * @brief This file contains the API implementation for the Interrupt Manager driver.
 * 
 * @version Interrupt Manager Driver Version 2.0.5
*/

/*
© [2024] Microchip Technology Inc. and its subsidiaries.

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

#include "../../system/interrupt.h"
#include "../../system/system.h"
#include "../pins.h"
#include "../../../main.h"
void (*INT_InterruptHandler)(void);

void INTERRUPT_Initialize (void)
{
    // Clear the interrupt flag
    // Set the external interrupt edge detect
    EXT_INT_InterruptFlagClear();   
    EXT_INT_risingEdgeSet();
    // Set Default Interrupt Handler
    INT_SetInterruptHandler(INT_DefaultInterruptHandler);
    // EXT_INT_InterruptEnable();
}

/**
 * @ingroup interrupt
 * @brief Services the Interrupt Service Routines (ISR) of enabled interrupts and is called every time an interrupt is triggered.
 * @pre Interrupt Manager is initialized.
 * @param None.
 * @return None.
 */
void __interrupt() INTERRUPT_InterruptManager (void)
{
    // interrupt handler
    if(PIE0bits.IOCIE == 1 && PIR0bits.IOCIF == 1)
    {
        PIN_MANAGER_IOC();
    }
    // <<< --- START OF ADDED CODE --- >>>
    else if(PIE1bits.TMR1IE == 1 && PIR1bits.TMR1IF == 1)
    {
        // Toggle the state of pin RC0 to generate the 100 Hz signal
        //LATCbits.LATC0 = ~LATCbits.LATC0;
        
        // Reload the timer value for the next  period
        // Preload value = 65536 - 155 = 65381 (0xFF05)
        TMR1H = 0xF9;
        TMR1L = 0x30; // 16 interupts per second
        
        // Clear the Timer1 interrupt flag so it can trigger again
        PIR1bits.TMR1IF = 0;
        
        
        // MY CODE
        
        if (start_tx)
        {
            uint8_t bit;
            if (sending_sync)
            {
                bit = (sync_sequence >> (7 - sync_bit_index)) & 0x01;
            }
            else
            {
                bit = (tx_data >> (7 - tx_bit_index)) & 0x01;
            }

            if (half_bit_phase == 0)
            {
                CLBSWINL = (bit == 0) ? 1 : 0;
                half_bit_phase = 1;
            }
            else
            {
                CLBSWINL = ~CLBSWINL;
                half_bit_phase = 0;

                if (sending_sync)
                {
                    sync_bit_index++;
                    if (sync_bit_index >= 8)
                    {
                        sync_bit_index = 0;
                        sending_sync = 0;  // Done sending sync, start sending normal data
                        tx_bit_index = 0;  // Reset data bit index
                    }
                }
                else
                {
                    tx_bit_index++;
                    if (tx_bit_index >= 8)
                    {
                        tx_bit_index = 0;
                        start_tx = 0;  // Transmission complete
                    }
                }
            }
        }
        else
        {
            CLBSWINL = 0;  // Ensure carrier off when idle
        }
        
    }
    // <<< --- END OF ADDED CODE --- >>>
    else
    {
        //Unhandled Interrupt
    }
}

// The rest of the file remains unchanged.

void INT_ISR(void)
{
    EXT_INT_InterruptFlagClear();

    // Callback function gets called everytime this ISR executes
    INT_CallBack();    
}

void INT_CallBack(void)
{
    // Add your custom callback code here
    if(INT_InterruptHandler)
    {
        INT_InterruptHandler();
    }
}

void INT_SetInterruptHandler(void (* InterruptHandler)(void)){
    INT_InterruptHandler = InterruptHandler;
}

void INT_DefaultInterruptHandler(void){
    // add your INT interrupt custom code
    // or set custom function using INT_SetInterruptHandler()
}
/**
 End of File
*/