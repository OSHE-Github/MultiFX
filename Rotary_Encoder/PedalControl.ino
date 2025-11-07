//------------------------------------------------------------
// Guitar Pedal Keyboard Controller
// Also Vibe Coded, will check and debug.
//
// CONTROLS:
// 3 Rotary Encoders
// 1 Footswitch (on D0)
//
//------------------------------------------------------------

// For sending HID keyboard commands
#include <Keyboard.h>

// Rotary encoder library (your original)
#include "encoders.h"
encoders encoder;
ISR (TIMER0_COMPA_vect) { encoder.msecTick(); }

// --- Pin Definitions ---
// Encoder pins are defined in encoders.h
#define FS_PIN 0 // Footswitch (FS) on D0

// --- Footswitch Debounce Variables ---
unsigned long lastFsTime = 0;
bool lastFsState = HIGH; // Assumes INPUT_PULLUP

//------------------------------------------------------------
// Setup
//------------------------------------------------------------
void setup()
{
  Serial.begin(115200); // diagnostic messages
  Serial.println("Guitar Pedal Controller Starting...");

  // --- Initialize Footswitch Pin ---
  pinMode(FS_PIN, INPUT_PULLUP);

  // --- Initialize Encoders ---
  encoder.begin();
  // hook timer0 (1 ms interrupt) by adding interrupt-on-compare-match
  OCR0A   = 0x80;         
  TIMSK0 |= _BV(OCIE0A);  

  // --- Start Keyboard ---
  Keyboard.begin();
  
  Serial.println("Setup Complete.");
}

//------------------------------------------------------------
// Loop
//------------------------------------------------------------
void loop()
{
  //-- Watch for encoder button events
  // Note: getButtonEvent() returns 1, 2, or 3
  if (uint8_t btn = encoder.getButtonEvent()) // button pressed?
  { 
    Serial.print("BUTTON "); Serial.println(btn); 
    
    switch (btn) {
      case 1: // Top (Red) Encoder Click
        Keyboard.write('w');
        break;
      case 2: // Middle (Green) Encoder Click
        Keyboard.write('s');
        break;
      case 3: // Bottom (Blue) Encoder Click
        Keyboard.write('x');
        break;
    }
  }

  //-- Watch for encoder spin events
  for (uint8_t i = 0; i < NUM_ENCODERS; i++)
  {
    // i = 0 (Encoder 1, Top)
    // i = 1 (Encoder 2, Middle)
    // i = 2 (Encoder 3, Bottom)
    if (int8_t spin = encoder.getSpin(i)) 
    { 
      Serial.print("SPIN "); Serial.print(i); 
      Serial.print(" = "); Serial.println(spin); 
      
      if (spin > 0) { // Turned Right
        switch (i) {
          case 0: Keyboard.write('e'); break; // Top Right
          case 1: Keyboard.write('d'); break; // Middle Right
          case 2: Keyboard.write('c'); break; // Bottom Right
        }
      } else { // Turned Left
        switch (i) {
          case 0: Keyboard.write('q'); break; // Top Left
          case 1: Keyboard.write('a'); break; // Middle Left
          case 2: Keyboard.write('z'); break; // Bottom Left
        }
      }
    }
  }

  //-- Watch for Footswitch (D0)
  bool fsState = digitalRead(FS_PIN);
  // Check if state changed AND debounce time has passed
  if (fsState != lastFsState && millis() - lastFsTime > DEBOUNCE_MS) {
    lastFsTime = millis();
    // Check for a press (HIGH to LOW)
    if (fsState == LOW) {
      Serial.println("Footswitch, Sending: f");
      Keyboard.write('f');
    }
    lastFsState = fsState; // Save the new state
  }
}
