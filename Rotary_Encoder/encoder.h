// Bit vibecoded, may have to iron out some kinks
#ifndef encoders_h
#define encoders_h

#include "Arduino.h"

// pick a default convention for A/B (rotary encoder model and A/B wiring)
// if different convention or wiring is used for some encoders, set B7 of state to override
#define ENCODER_CONVENTION 0b00 // 0b00 or 0b11

// rotary encoder and button pin connections 
// warning: direct register and bit manipulation being used on PORTB & PORTD
//          use the pins as listed below or the code must be changed too
//
// **** IMPORTANT ****
// The logic for reading these pins is in the (missing) "encoders.cpp" file.
// That file MUST be re-written to read from these new pin locations.
// The Footswitch on D0 is handled separately in the .ino file.

#define NUM_ENCODERS 3 // Changed from 4 to 3

// encoders are arranged in groups of 3 bits
//   B0 = A signal
//   B1 = B signal
//   B2 = button
//
// rotary encoder #1 (Top, Red)
#define A1_PIN    10 // D10 (PB2)
#define B1_PIN    9  // D9  (PB1)
#define BTN1_PIN  8  // D8  (PB0)
// rotary encoder #2 (Middle, Green)
#define A2_PIN    6  // D6  (PD6)
#define B2_PIN    5  // D5  (PD5)
#define BTN2_PIN  4  // D4  (PD4)
// rotary encoder #3 (Bottom, Blue)
#define A3_PIN    3  // D3  (PD3)
#define B3_PIN    2  // D2  (PD2)
#define BTN3_PIN  1  // D1  (PD1)

// max count limits are not a factor if you read the spin often enough
#define MIN_SPIN  -128  
#define MAX_SPIN   127  

#define DEBOUNCE_MS 50  // pushbutton contact debounce time

// state bits; BA state is in low 2 bits
#define AB_REVERSE_BIT 7
#define CW_BIT         6
#define CCW_BIT        5
#define BTN_BIT        2
#define MASK(b) (1 << b)

class encoders
{
  public:
    void begin();
    void msecTick();
    void reverseAB( byte index );
    uint8_t getButtonEvent();
    boolean getButtonState( uint8_t index );
    int8_t  getSpin( uint8_t index );
    
  private:
    // state information is owned by interrupt, use getButtonEvent() and getSpin() to access
    uint8_t button_event = 0; // button pressed event, 0=none, 1..3=button number
                              //   if buttons are pressed simultaneously, or not read before another is pressed, only the last one pressed registers
    struct  encoder_t   // encoder state information
    { uint8_t  state;         // packed bits: B7=AB convention override, B2=button, B1=B, B0=A
      uint8_t  btn_debounce;  // 1ms button debounce ticks left 
       int8_t  spin;          // rotary encoder movement since last read
      uint8_t  ticks;         // 1ms ticks since last encoder movement
    } encoder[NUM_ENCODERS];

    void handleEncoder( byte index, byte encoderPBA );
};

#endif
