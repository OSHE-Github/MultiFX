#include <Keyboard.h>

// Rotary Encoder Module connections
#define PinSW D5   // Rotary Encoder Switch 1
#define PinDT D8    // DATA signal 1
#define PinCLK D1   // CLOCK signal 1
#define PinSW2 D6   // Rotary Encoder Switch 2
#define PinDT2 D3    // DATA signal 2
#define PinCLK2 D2   // CLOCK signal 2
#define PinSW3 D4   // Rotary Encoder Switch 3
#define PinDT3 D10    // DATA signal 3
#define PinCLK3 D9   // CLOCK signal 3

// Footswitch connections
#define FootSW D0 // Footswitch signal

// Variables to debounce Rotary Encoder
long TimeOfLastDebounce = 0;
int DelayofDebounce = 0.0001;

// Variables to delay Pushbuttons
int DelayOfButton = 200;
long TimeOfLastButton = 0;
int Wait = 0;
long TimeOfLastButton2 = 0;
int Wait2 = 0;
long TimeOfLastButton3 = 0;
int Wait3 = 0;

// Store previous Pins state
int PreviousCLK;   
int PreviousDATA;
int PreviousCLK2;   
int PreviousDATA2;
int PreviousCLK3;   
int PreviousDATA3;
int PreviousFootSW;

void setup() {
  // Put current pins state in variables

  Serial1.begin(31250);
  PreviousCLK=digitalRead(PinCLK);
  PreviousDATA=digitalRead(PinDT);
  PreviousCLK2=digitalRead(PinCLK2);
  PreviousDATA2=digitalRead(PinDT2);
  PreviousCLK3=digitalRead(PinCLK3);
  PreviousDATA3=digitalRead(PinDT3);
  PreviousFootSW=digitalRead(FootSW);

  // Set the Switch pin to use Arduino PULLUP resistors
  pinMode(PinSW, INPUT_PULLUP);
  pinMode(PinSW2, INPUT_PULLUP);
  pinMode(PinSW3, INPUT_PULLUP);
  pinMode(PinDT, INPUT);
  pinMode(PinDT2, INPUT);
  pinMode(PinDT3, INPUT);
  pinMode(PinCLK, INPUT);
  pinMode(PinCLK2, INPUT);
  pinMode(PinCLK2, INPUT);
  pinMode(FootSW, INPUT);

  //Initiate Keyboard Output
  Keyboard.begin();
}
void loop() {
  // If enough time has passed check the rotary encoder
  if ((millis() - TimeOfLastDebounce) > DelayofDebounce) {
    
    check_rotary();  // Rotary Encoder check routine below
    check_button();  // Pushbotton check routine below
    check_footsw();  // Footswitch check routine below
    check_midi();
    
    PreviousCLK=digitalRead(PinCLK);
    PreviousDATA=digitalRead(PinDT);
    PreviousCLK2=digitalRead(PinCLK2);
    PreviousDATA2=digitalRead(PinDT2);
    PreviousCLK3=digitalRead(PinCLK3);
    PreviousDATA3=digitalRead(PinDT3);
    PreviousFootSW=digitalRead(FootSW);

    TimeOfLastDebounce=millis();  // Set variable to current millis() timer
  }
}

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
// Check if Rotary Encoder switch 1 was pressed
void check_button() {
  if (digitalRead(PinSW) == LOW) {
    if (Wait == 0){
      TimeOfLastButton=millis();
      Wait = 1;
    }
  }
  if (Wait == 1){
    if ((millis() - TimeOfLastButton) > DelayOfButton) {
      Keyboard.print("w");
      Wait = 0;
    }
  }
  // Check if Rotary Encoder switch 2 was pressed
  if (digitalRead(PinSW2) == LOW) {
    if (Wait2 == 0){
      TimeOfLastButton2=millis();
      Wait2 = 1;
    }
  }
  if (Wait2 == 1){
    if ((millis() - TimeOfLastButton2) > DelayOfButton) {
      Keyboard.print("s");
      Wait2 = 0;
    }
  }
  // Check if Rotary Encoder switch 3 was pressed
  if (digitalRead(PinSW3) == LOW) {
    if (Wait3 == 0){
      TimeOfLastButton3=millis();
      Wait3 = 1;
    }
  }
  if (Wait3 == 1){
    if ((millis() - TimeOfLastButton3) > DelayOfButton) {
      Keyboard.print("x");
      Wait3 = 0;
    }
  }
}

// Check if Rotary Encoder was moved
void check_rotary() {
  // Rotary 1 Code
  if ((PreviousCLK == 1) && (PreviousDATA == 0)) {
    if ((digitalRead(PinCLK) == 0) && (digitalRead(PinDT) == 1)) {
      Keyboard.print("e");
    }
    if ((digitalRead(PinCLK) == 0) && (digitalRead(PinDT) == 0)) {
      Keyboard.print("q");
    }
  }
  if ((PreviousCLK == 1) && (PreviousDATA == 1)) {
    if ((digitalRead(PinCLK) == 0) && (digitalRead(PinDT) == 1)) {
      Keyboard.print("e");
    }
    if ((digitalRead(PinCLK) == 0) && (digitalRead(PinDT) == 0)) {
      Keyboard.print("q");
    }
  }  
  // Rotary 2 Code
  if ((PreviousCLK2 == 1) && (PreviousDATA2 == 0)) {
    if ((digitalRead(PinCLK2) == 0) && (digitalRead(PinDT2) == 1)) {
      Keyboard.print("d");
    }
    if ((digitalRead(PinCLK2) == 0) && (digitalRead(PinDT2) == 0)) {
      Keyboard.print("a");
    }
  }
  if ((PreviousCLK2 == 1) && (PreviousDATA2 == 1)) {
    if ((digitalRead(PinCLK2) == 0) && (digitalRead(PinDT2) == 1)) {
      Keyboard.print("d");
    }
    if ((digitalRead(PinCLK2) == 0) && (digitalRead(PinDT2) == 0)) {
      Keyboard.print("a");
    }
  }  
  // Rotary 3 Code
  if ((PreviousCLK3 == 1) && (PreviousDATA3 == 0)) {
    if ((digitalRead(PinCLK3) == 0) && (digitalRead(PinDT3) == 1)) {
      Keyboard.print("c");
    }
    if ((digitalRead(PinCLK3) == 0) && (digitalRead(PinDT3) == 0)) {
      Keyboard.print("z");
    }
  }
  if ((PreviousCLK3 == 1) && (PreviousDATA3 == 1)) {
    if ((digitalRead(PinCLK3) == 0) && (digitalRead(PinDT3) == 1)) {
      Keyboard.print("c");
    }
    if ((digitalRead(PinCLK3) == 0) && (digitalRead(PinDT3) == 0)) {
      Keyboard.print("z");
    }
  }           
}
 
void check_footsw() {
  if (PreviousFootSW == 0){
    if (digitalRead(FootSW) == 1){
      Keyboard.print("r");
    }
  }
  if (PreviousFootSW == 1){
    if (digitalRead(FootSW) == 0){
      Keyboard.print("r");
    }
  }
}
