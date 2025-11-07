// Still gotta work on it, but it will get done, trust :pray: - Noki
// (Also just wanted to get this into the branch before more work)
#ifndef encoders_h
#define encoders_h

#include "Arduino.h"

// pick a default convention for A/B (rotary encoder model and A/B wiring)
// if different convention or wiring is used for some encoders, set B7 of state to override
#define ENCODER_CONVENTION 0b00 // 0b00 or 0b11

// rotary encoder and button pin connections 
// warning: direct register and bit manipulation being used on PORTB & PORTD
//          use the pins as listed below or the code must be changed too
#define NUM_ENCODERS 3
// encoders are arranged in groups of 3 bits
//   B0 = A signal
//   B1 = B signal
//   B2 = button
// rotary encoder #1
#define A1_PIN    2 // PD2 rotary encoder A signal
#define B1_PIN    3 // PD3 rotary encoder B signal
#define BTN1_PIN  4 // PD4 button
// rotary encoder #2
#define A2_PIN    5 // PD5 rotary encoder A signal
#define B2_PIN    6 // PD6 rotary encoder B signal
#define BTN2_PIN  7 // PD7 button
// rotary encoder #3 
#define A3_PIN    8 // PB0 rotary encoder A signal
#define B3_PIN    9 // PB1 rotary encoder B signal
#define BTN3_PIN 10 // PB2 button
// rotary encoder #4
#define A4_PIN   11 // PB3 rotary encoder A signal
#define B4_PIN   12 // PB4 rotary encoder B signal
#define BTN4_PIN 13 // PB5 requires stiff pullup (~330 Ohms) due to onboard LED

#define MIN_SPIN  -128  // max count limits,
#define MAX_SPIN   127  //    not a factor if you read the spin often enough

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
    uint8_t button_event = 0; // button pressed event, 0=none, 1..4=button number
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
