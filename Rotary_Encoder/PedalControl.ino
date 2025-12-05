//------------------------------------------------------------
// MultiFX Pedal Keyboard Controller
//
// Libraries Used:
// Keyboard.h from https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json pico library
// RotaryEncoder.H by Matthias Hertel
// Bounce2 by Thomas O Fredericks
//------------------------------------------------------------

#include <Keyboard.h>
#include <RotaryEncoder.h>
#include <Bounce2.h>

// If you have more than 3 encoders, you will have to add their functionality
#define NUM_ENCODERS 3 

// Encoder 1 (Top, Red) - D10, D9, D8
#define A1_PIN    4   // D10 = GPIO3
#define B1_PIN    3   // D9  = GPIO4
#define SW1_PIN   2   // D8  = GPIO2

// Encoder 2 (Middle, Green) - D6, D5, D4
#define A2_PIN    7   // D6 = GPIO0
#define B2_PIN    0   // D5 = GPIO7
#define SW2_PIN   6   // D4 = GPIO6

// Encoder 3 (Bottom, Blue) - D3, D2, D1
#define A3_PIN    28  // D3 = GPIO29
#define B3_PIN    29  // D2 = GPIO28
#define SW3_PIN   27  // D1 = GPIO27

// Footswitch - D0
#define FS_PIN    26  // D0 = GPIO26

// --- Keyboard Mappings --- (Currently unimplimented, hardcoded values worked)
// const char enc_left_key[] = { 'q', 'a', 'z' };
// const char enc_click_key[] = { 'w', 's', 'x' };
// const char enc_right_key[] = { 'e', 'd', 'c' };
// const char fs_key = 'r';

// --- Encoder Objects (using FOUR0 latch mode - library default) ---
RotaryEncoder enc1(A1_PIN, B1_PIN, RotaryEncoder::LatchMode::FOUR0);
RotaryEncoder enc2(A2_PIN, B2_PIN, RotaryEncoder::LatchMode::FOUR0);
RotaryEncoder enc3(A3_PIN, B3_PIN, RotaryEncoder::LatchMode::FOUR0);

// --- Button Objects ---
Bounce btn1 = Bounce();
Bounce btn2 = Bounce();
Bounce btn3 = Bounce();

#define DEBOUNCE_MS 10

// --- Position Tracking ---
long enc1_oldPos = 0;
long enc2_oldPos = 0;
long enc3_oldPos = 0;

// --- Footswitch Interrupt State ---
volatile bool sendFootswitchKey = false; // Flag to tell main loop to send key
volatile unsigned long last_fs_int_time = 0;

//------------------------------------------------------------
// Interrupt Service Routines
//------------------------------------------------------------
void checkEncoder1() { enc1.tick(); }
void checkEncoder2() { enc2.tick(); }
void checkEncoder3() { enc3.tick(); }
void footswitchISR() {
  unsigned long now = millis();
  
  // Debounce: If an interrupt happens within 50ms of the last one, ignore it.
  if (now - last_fs_int_time < 100) {
    return; // Ignore bounce
  }
  
  // This is a valid new press, record the time
  last_fs_int_time = now;
  
  // Set the flag for the main loop (this is safe)
  sendFootswitchKey = true;
  delay(10);
}
//------------------------------------------------------------
// Setup
//------------------------------------------------------------
void setup()
{
  Serial.begin(115200);
  Serial1.begin(31250);
  delay(1000);
  Serial.println("\n=== RP2040 Pedal Controller ===");
  Serial.println("Using corrected GPIO mapping for Seeed Xiao\n");

  // --- Initialize Encoder Pins ---
  pinMode(A1_PIN, INPUT_PULLUP);
  pinMode(B1_PIN, INPUT_PULLUP);
  pinMode(A2_PIN, INPUT_PULLUP);
  pinMode(B2_PIN, INPUT_PULLUP);
  pinMode(A3_PIN, INPUT_PULLUP);
  pinMode(B3_PIN, INPUT_PULLUP);

  // --- Attach Interrupts ---
  attachInterrupt(digitalPinToInterrupt(A1_PIN), checkEncoder1, CHANGE);
  attachInterrupt(digitalPinToInterrupt(B1_PIN), checkEncoder1, CHANGE);
  attachInterrupt(digitalPinToInterrupt(A2_PIN), checkEncoder2, CHANGE);
  attachInterrupt(digitalPinToInterrupt(B2_PIN), checkEncoder2, CHANGE);
  attachInterrupt(digitalPinToInterrupt(A3_PIN), checkEncoder3, CHANGE);
  attachInterrupt(digitalPinToInterrupt(B3_PIN), checkEncoder3, CHANGE);

  // --- Initialize Footswitch ---
  pinMode(FS_PIN, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(FS_PIN), footswitchISR, CHANGE);
  
  // --- Initialize Buttons ---
  btn1.attach(SW1_PIN, INPUT_PULLUP);
  btn2.attach(SW2_PIN, INPUT_PULLUP);
  btn3.attach(SW3_PIN, INPUT_PULLUP);

  btn1.interval(DEBOUNCE_MS);
  btn2.interval(DEBOUNCE_MS);
  btn3.interval(DEBOUNCE_MS);

  // --- Start Keyboard HID ---
  Keyboard.begin();
  
  Serial.println("Key Mappings:");
  Serial.println("  Encoder 1 (Top):    q(left) w(click) e(right)");
  Serial.println("  Encoder 2 (Middle): a(left) s(click) d(right)");
  Serial.println("  Encoder 3 (Bottom): z(left) x(click) c(right)");
  Serial.println("  Footswitch:         r");
  Serial.println("\nReady!\n");
}

//------------------------------------------------------------
// Encoder 1 Rotation Handler
//------------------------------------------------------------
void handleEncoder1Rotation()
{
  long newPos = enc1.getPosition();
  
  if (newPos > enc1_oldPos)
  {
    Serial.println("ENC1 RIGHT → 'e'");
    Keyboard.write('e');
    enc1_oldPos = newPos;
  }
  else if (newPos < enc1_oldPos)
  {
    Serial.println("ENC1 LEFT → 'q'");
    Keyboard.write('q');
    enc1_oldPos = newPos;
  }
}

//------------------------------------------------------------
// Encoder 2 Rotation Handler
//------------------------------------------------------------
void handleEncoder2Rotation()
{
  long newPos = enc2.getPosition();
  
  if (newPos > enc2_oldPos)
  {
    Serial.println("ENC2 RIGHT → 'd'");
    Keyboard.write('d');
    enc2_oldPos = newPos;
  }
  else if (newPos < enc2_oldPos)
  {
    Serial.println("ENC2 LEFT → 'a'");
    Keyboard.write('a');
    enc2_oldPos = newPos;
  }
}

//------------------------------------------------------------
// Encoder 3 Rotation Handler
//------------------------------------------------------------
void handleEncoder3Rotation()
{
  long newPos = enc3.getPosition();
  
  if (newPos > enc3_oldPos)
  {
    Serial.println("ENC3 RIGHT → 'c'");
    Keyboard.write('c');
    enc3_oldPos = newPos;
  }
  else if (newPos < enc3_oldPos)
  {
    Serial.println("ENC3 LEFT → 'z'");
    Keyboard.write('z');
    enc3_oldPos = newPos;
  }
}

//------------------------------------------------------------
// Button Press Handler
//------------------------------------------------------------
void handleButtonPresses()
{
  if (btn1.fell())
  {
    Serial.println("BTN1 CLICK → 'w'");
    Keyboard.write('w');
  }
  
  if (btn2.fell())
  {
    Serial.println("BTN2 CLICK → 's'");
    Keyboard.write('s');
  }
  
  if (btn3.fell())
  {
    Serial.println("BTN3 CLICK → 'x'");
    Keyboard.write('x');
  }
}
//------------------------------------------------------------
// Midi Switch Handler
//------------------------------------------------------------
void check_midi(){
  if(Serial1.available()){
    int midiMessage = 0;

    midiMessage=Serial1.read();
    Serial.print(midiMessage, HEX);
    midiMessage = midiMessage & 0x000F;
    Serial.println("");
    Serial.print(midiMessage, HEX);
    Serial.println("");

    switch(midiMessage){
      case(0):
      {
        Keyboard.print("f");
        break;
      }
      case(1):
      {
        Keyboard.print("g");
        break;
      }
      case(2):
      {
        Keyboard.print("h");
        break;
      }
      case(3):
      {
        Keyboard.print("j");
        break;
      }
      case(4):
      {
        Keyboard.print("k");
        break;
      }
      case(5):
      {
        Keyboard.print("l");
        break;
      }
      default:
        break;

    }
    delay(50);
    while(Serial1.available()){
      delay(10);
      Serial1.read();
    }
  }
}

//------------------------------------------------------------
// Main Loop
//------------------------------------------------------------
void loop()
{
  // Update all button states
  btn1.update();
  btn2.update();
  btn3.update();
  

  // Handle all inputs
  handleEncoder1Rotation();
  handleEncoder2Rotation();
  handleEncoder3Rotation();
  handleButtonPresses();
  check_midi();

  if(sendFootswitchKey){
    Keyboard.write('r');
    delay(200);
    sendFootswitchKey = false;
  }
  
  delay(1);
}
