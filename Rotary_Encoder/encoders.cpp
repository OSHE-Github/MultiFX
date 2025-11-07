//------------------------------------------------------------
// Rotary Encoders With Buttons
// Todo: Credit Fearless Night on implimentation
//------------------------------------------------------------

#include "encoders.h"

void encoders::begin() // required to initialize library
{
  // Set pinMode for all 3 encoders
  pinMode( A1_PIN,INPUT_PULLUP );  pinMode( B1_PIN,INPUT_PULLUP );  pinMode( BTN1_PIN,INPUT_PULLUP );
  pinMode( A2_PIN,INPUT_PULLUP );  pinMode( B2_PIN,INPUT_PULLUP );  pinMode( BTN2_PIN,INPUT_PULLUP );
  pinMode( A3_PIN,INPUT_PULLUP );  pinMode( B3_PIN,INPUT_PULLUP );  pinMode( BTN3_PIN,INPUT_PULLUP );
  
  // initialize state machines
  for (uint8_t i=0; i < NUM_ENCODERS; i++)
  { 
    encoder[i].state = 0b11; // detent state
    encoder[i].btn_debounce = 0;
    encoder[i].spin = 0;
    encoder[i].ticks = 0;
  }
}

void encoders::reverseAB( byte index ) // call after begin() to reverse A/B wiring convention for individual encoders
{
  if (index >= NUM_ENCODERS) return; // failsafe
  encoder[index].state |= 0x80;
}

// Method to check once a millisecond.
void encoders::msecTick() // Interrupt is called once a millisecond
{
  // Read ports once at the beginning of the interrupt
  byte pinsD = PIND; 
  byte pinsB = PINB;
  byte pba; // Will hold the packed (Button, B, A) bits for handleEncoder

  // --- Encoder 1 (Top): A=PB2, B=PB1, BTN=PB0 ---
  pba = 0; // Clear for next encoder
  // Bit 0 = A = (pinsB & _BV(PB2))
  // Bit 1 = B = (pinsB & _BV(PB1))
  // Bit 2 = Btn = (pinsB & _BV(PB0))
  if (pinsB & _BV(PB2)) pba |= _BV(0); // Set bit 0 if A (PB2) is HIGH
  if (pinsB & _BV(PB1)) pba |= _BV(1); // Set bit 1 if B (PB1) is HIGH
  if (pinsB & _BV(PB0)) pba |= _BV(2); // Set bit 2 if Button (PB0) is HIGH
  handleEncoder( 0, pba );

  // --- Encoder 2 (Middle): A=PD6, B=PD5, BTN=PD4 ---
  pba = 0; // Clear for next encoder
  // Bit 0 = A = (pinsD & _BV(PD6))
  // Bit 1 = B = (pinsD & _BV(PD5))
  // Bit 2 = Btn = (pinsD & _BV(PD4))
  if (pinsD & _BV(PD6)) pba |= _BV(0); // Set bit 0 if A (PD6) is HIGH
  if (pinsD & _BV(PD5)) pba |= _BV(1); // Set bit 1 if B (PD5) is HIGH
  if (pinsD & _BV(PD4)) pba |= _BV(2); // Set bit 2 if Button (PD4) is HIGH
  handleEncoder( 1, pba );

  // --- Encoder 3 (Bottom): A=PD3, B=PD2, BTN=PD1 ---
  pba = 0; // Clear for next encoder
  // Bit 0 = A = (pinsD & _BV(PD3))
  // Bit 1 = B = (pinsD & _BV(PD2))
  // Bit 2 = Btn = (pinsD & _BV(PD1))
  if (pinsD & _BV(PD3)) pba |= _BV(0); // Set bit 0 if A (PD3) is HIGH
  if (pinsD & _BV(PD2)) pba |= _BV(1); // Set bit 1 if B (PD2) is HIGH
  if (pinsD & _BV(PD1)) pba |= _BV(2); // Set bit 2 if Button (PD1) is HIGH
  handleEncoder( 2, pba );
}

//
// *** NO CHANGES NEEDED BELOW THIS LINE ***
//
// (handleEncoder logic is unchanged because msecTick now provides
// the 'encoderPBA' byte in the format it expects)
//
void encoders::handleEncoder( byte index, byte encoderPBA ) // encoderPBA is packed input pin states: B2=button, B1=B, B0=A
{
  // Software only quadrature encoder debouncing,
  // requires no hardware filtering on A/B signals.
  // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  encoder_t *e = &encoder[index]; // make a convenient pointer to this encoder state machine data

  // basic rotary encoder decoding
  //   See http://www.fearlessnight.com/rotaryHowTo/index.html
  //   for explanation of logic.
  byte BA = encoderPBA & 0b11; // mask to BA input pin bits
  if (e->state & MASK(AB_REVERSE_BIT)) if (BA==2 || BA==1) BA ^= 0b11;
  int8_t  spin = 0;
  uint8_t edge = ((e->state & 0b11) << 2) | BA;
  switch (edge)
  {
    case 0b0010: if (!(e->state & MASK(CCW_BIT))) spin = -1;
                 e->state &= ~(MASK(CW_BIT)|MASK(CCW_BIT));  break;

    case 0b0001: if (!(e->state & MASK(CW_BIT))) spin = 1;
                 e->state &= ~(MASK(CW_BIT)|MASK(CCW_BIT));  break;

    case 0b1000: e->state |= MASK(CCW_BIT);  break;

    case 0b0100: e->state |= MASK(CW_BIT);
  }

  // variable speed boost
  //   the faster you spin it the more it boosts
  if (spin) // boost the spin by a multiplier that's a function of the time between movements
  { // 4 speed velocirotor
    uint8_t            m =  1; // speed multiplier
    if (e->ticks < 50) m =  2; //  2'nd gear
    if (e->ticks < 20) m = 10; //  3'rd gear
    if (e->ticks <  8) m = 50; //  overdrive
    int nspin = e->spin + spin * m;         // calculate spin, which might exceed 8 bits
    if (nspin < MIN_SPIN) nspin = MIN_SPIN; // limit to fit in 8 bits,
    if (nspin > MAX_SPIN) nspin = MAX_SPIN; //   or you could use a 16 bit variable for Ludicrous spin speeds
    e->spin = nspin; // now it fits 8 bits
    e->ticks = 0;    // count time to next movement
  }
  else if (e->ticks < 255) e->ticks++; // count time between movements

  // track (update) BA bits, retain other state bits
  e->state = (e->state & 0b11111100) | BA; 

  // Button debouncing
  // ~~~~~~~~~~~~~~~~~
  // trigger immediately on button press, debounce on release

  if (encoderPBA & 0b100) // mask to button input pin, negative logic (0 is pressed)
  { // button is released
    if (e->btn_debounce)  // in release debounce, count down debounce ticks
      if (--e->btn_debounce == 0) e->state &= ~MASK(BTN_BIT); // set button state 0 (released)
  } else
  { // button is pressed, trigger press event
    if (e->btn_debounce == 0) // if not already pressed
    { e->state |= MASK(BTN_BIT);   //   set button state 1 (pressed)
      button_event = index+1;      //   set button press event
    }
    e->btn_debounce = DEBOUNCE_MS; // [re]start debounce timer
  }
}

// Get button press
uint8_t encoders::getButtonEvent() // returns button number (1..3) or zero if nothing was pressed
{
  noInterrupts();  // prevent interrupt interference while we fetch the data from storage
    uint8_t result = button_event;
    button_event = 0;
  interrupts();
  return result;
}

// Is the button pressed right now
boolean encoders::getButtonState( uint8_t index ) // returns true if button is pressed now
{
  if (index >= NUM_ENCODERS) return 0; // failsafe
  // reading only, so there are no interrupt interference issues accessing storage
  return (encoder[index].state & 0b100) != 0;
}

// Get dial spin
int8_t encoders::getSpin( uint8_t index ) // returns +/- increments since last call
{
  if (index >= NUM_ENCODERS) return 0; // failsafe
  noInterrupts();  // prevent interrupt interference while we fetch the data from storage
    int8_t result = encoder[index].spin;
    encoder[index].spin = 0;
  interrupts();
  return result;
}
