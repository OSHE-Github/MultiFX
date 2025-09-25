

void setup() {
  Serial.begin(9600);
  Serial1.begin(31250);
  pinMode(D0, INPUT);
  pinMode(D1, INPUT);
  pinMode(D2, INPUT);
  pinMode(D3, INPUT);
  pinMode(D4, INPUT);
  pinMode(D5, INPUT);
  attachInterrupt(digitalPinToInterrupt(D0), ISR0, CHANGE);
  attachInterrupt(digitalPinToInterrupt(D1), ISR1, CHANGE);
  attachInterrupt(digitalPinToInterrupt(D2), ISR2, CHANGE);
  attachInterrupt(digitalPinToInterrupt(D3), ISR3, CHANGE);
  attachInterrupt(digitalPinToInterrupt(D4), ISR4, CHANGE);
  attachInterrupt(digitalPinToInterrupt(D5), ISR5, CHANGE);
  
}
//default states
  volatile bool off0 = true;   
  volatile bool off1 = true;   
  volatile bool off2 = true;   
  volatile bool off3 = true;   
  volatile bool off4 = true;   
  volatile bool off5 = true;   
  
//channel 0
void MIDIOff0(){
  byte midiNoteOff0[] = {0x80};   
  Serial1.write(midiNoteOff0, sizeof(midiNoteOff0));
  Serial.println("MIDI Note Off Sent Channel 0");
 
}
void MIDIOn0(){
  byte midiNoteOn0[] = {0x90};  
  Serial1.write(midiNoteOn0, sizeof(midiNoteOn0));
  Serial.println("MIDI Note On Sent Channel 0");
}

//channel 1
void MIDIOff1(){
  byte midiNoteOff1[] = {0x81}; 
  Serial1.write(midiNoteOff1, sizeof(midiNoteOff1));
  Serial.println("MIDI Note Off Sent Channel 1");
 
}
void MIDIOn1(){
  byte midiNoteOn1[] = {0x91}; 
  Serial1.write(midiNoteOn1, sizeof(midiNoteOn1));
  Serial.println("MIDI Note On Sent Channel 1");
}

//channel 2
void MIDIOff2(){
  byte midiNoteOff2[] = {0x82}; 
  Serial1.write(midiNoteOff2, sizeof(midiNoteOff2));
  Serial.println("MIDI Note Off Sent Channel 2");
 
}
void MIDIOn2(){
  byte midiNoteOn2[] = {0x92};  
  Serial1.write(midiNoteOn2, sizeof(midiNoteOn2));
  Serial.println("MIDI Note On Sent Channel 2");
}

//channel 3
void MIDIOff3(){
  byte midiNoteOff3[] = {0x83}; 
  Serial1.write(midiNoteOff3, sizeof(midiNoteOff3));
  Serial.println("MIDI Note Off Sent Channel 3");
 
}
void MIDIOn3(){
  byte midiNoteOn3[] = {0x93}; 
  Serial1.write(midiNoteOn3, sizeof(midiNoteOn3));
  Serial.println("MIDI Note On Sent Channel 3");
}

//channel 4
void MIDIOff4(){
  byte midiNoteOff4[] = {0x84}; 
  Serial1.write(midiNoteOff4, sizeof(midiNoteOff4));
  Serial.println("MIDI Note Off Sent Channel 4");
 
}
void MIDIOn4(){
  byte midiNoteOn4[] = {0x94}; 
  Serial1.write(midiNoteOn4, sizeof(midiNoteOn4));
  Serial.println("MIDI Note On Sent Channel 4");
}

//channel 5
void MIDIOff5(){
  byte midiNoteOff5[] = {0x85};
  Serial1.write(midiNoteOff5, sizeof(midiNoteOff5));
  Serial.println("MIDI Note Off Sent Channel 5");
 
}
void MIDIOn5(){
  byte midiNoteOn5[] = {0x95};
  Serial1.write(midiNoteOn5, sizeof(midiNoteOn5));
  Serial.println("MIDI Note On Sent Channel 5");
}


void ISR0(){
  if (off0){
    MIDIOn0();
    off0 = false;
  } else {
    MIDIOff0();
    off0 = true;
  }
}
 

void ISR1(){
  if (off1){
    MIDIOn1();
    off1 = false;
  } else {
    MIDIOff1();
    off1 = true;
  }
}

void ISR2(){
  if (off2){
    MIDIOn2();
    off2 = false;
  } else {
    MIDIOff2();
    off2 = true;
  }
}

void ISR3(){
  if (off3){
    MIDIOn3();
    off3 = false;
  } else {
    MIDIOff3();
    off3 = true;
  }
}

void ISR4(){
  if (off4){
      MIDIOn4();
      off4 = false;
    } else {
      MIDIOff4();
      off4 = true;
    }
}

void ISR5(){
   if (off5){
      MIDIOn5();
      off5 = false;
    } else {
      MIDIOff5();
      off5 = true;
    }
}

void loop() {    

