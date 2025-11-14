// ------------ CONFIG ------------

// Pins: 1..6
const int btnPins[6] = { D0, D1, D2, D3, D4, D5 };

// If pressed = HIGH, keep HIGH. If your wiring is inverted, change to LOW.
const int PRESSED_LEVEL = HIGH;

// Edge-based debounce settings (for D0..D3)
const unsigned long stableMsEdge = 60;   // input must be stable this long
const unsigned long minGapEdge   = 120;  // min time between events per button

// Sample-based settings (for D4, D5)
const unsigned long samplePeriodMs = 220;  // how often we "take a reading"


// ------------ STATE ------------

// For edge-based buttons (indexes 0..3: D0..D3)
int lastRawEdge[4];
unsigned long lastChangeTimeEdge[4];
int stableLevelEdge[4];
unsigned long lastEventTimeEdge[4];

// For sample-based buttons (indexes 4..5: D4, D5)
int lastSampleLevel[2];              // previous sampled HIGH/LOW
unsigned long lastSampleTime[2];     // last time we sampled

// Shared Note ON/OFF state for all 6 buttons
bool noteOn[6];

// Which of the sample-based buttons (D4/D5) to check this cycle: 0 -> D4, 1 -> D5
int whichSample = 0;


// ------------ MIDI HELPERS ------------

void sendMidiOn(uint8_t ch) {
  byte status = 0x90 | (ch & 0x0F);   // Note On, channel ch
  Serial1.write(&status, 1);
  Serial.print("MIDI Note On Sent Channel ");
  Serial.println(ch);
}

void sendMidiOff(uint8_t ch) {
  byte status = 0x80 | (ch & 0x0F);   // Note Off, channel ch
  Serial1.write(&status, 1);
  Serial.print("MIDI Note Off Sent Channel ");
  Serial.println(ch);
}

int readFilteredPin(int pin) {
  int ones = 0;
  const int N = 5;  // number of reads

  for (int k = 0; k < N; k++) {
    if (digitalRead(pin) == HIGH) ones++;
    delayMicroseconds(200);  // short spacing, ~1 ms total
  }

  return (ones >= (N / 2 + 1)) ? HIGH : LOW; // majority vote
}


// ------------ SETUP ------------

void setup() {
  Serial.begin(9600);
  Serial1.begin(31250);

  unsigned long now = millis();

  // Init D0..D3 (buttons 1..4) for edge-based debounce
  for (int i = 0; i < 4; i++) {
    pinMode(btnPins[i], INPUT);      // keep your existing external wiring

    int v = digitalRead(btnPins[i]);
    lastRawEdge[i]        = v;
    stableLevelEdge[i]    = v;
    lastChangeTimeEdge[i] = now;
    lastEventTimeEdge[i]  = 0;
    noteOn[i]             = false;
  }

// Init D4..D5 (buttons 5..6) for sample-based logic
for (int j = 0; j < 2; j++) {
  int idx = 4 + j;                 // 4 -> D4, 5 -> D5

  pinMode(btnPins[idx], INPUT_PULLDOWN);  // <--- try this first

  int v = readFilteredPin(btnPins[idx]);
  lastSampleLevel[j] = v;
  lastSampleTime[j]  = now;
  noteOn[idx]        = false;
}

  Serial.println("6-button MIDI footswitch: D0..D3 edge-based, D4..D5 sampled.");
}


// ------------ LOOP ------------

void loop() {
  unsigned long now = millis();

  // ----- EDGE-BASED: buttons 1..4 (D0..D3, indexes 0..3) -----
  for (int i = 0; i < 4; i++) {
    int idx = i;  // logical index = MIDI channel = i

    int raw = digitalRead(btnPins[idx]);

    // track raw stability
    if (raw != lastRawEdge[i]) {
      lastRawEdge[i]        = raw;
      lastChangeTimeEdge[i] = now;
    }

    // has the raw value been different from the stable value long enough?
    if (raw != stableLevelEdge[i] && (now - lastChangeTimeEdge[i] >= stableMsEdge)) {
      // enforce minimum time between events
      if (now - lastEventTimeEdge[i] < minGapEdge) {
        // too soon after last event; update stableLevel but don't send MIDI
        stableLevelEdge[i] = raw;
        continue;
      }

      // accept new stable level
      stableLevelEdge[i] = raw;
      lastEventTimeEdge[i] = now;

      bool pressed = (stableLevelEdge[i] == PRESSED_LEVEL);

      if (pressed && !noteOn[idx]) {
        sendMidiOn(idx);
        noteOn[idx] = true;
      } else if (!pressed && noteOn[idx]) {
        sendMidiOff(idx);
        noteOn[idx] = false;
      }
    }
  }

  // ----- SAMPLE-BASED: buttons 5..6 (D4..D5, indexes 4..5) -----
  {
    int j   = whichSample;   // 0 or 1
    int idx = 4 + j;         // 4 -> button 5 (D4), 5 -> button 6 (D5)

    if (now - lastSampleTime[j] >= samplePeriodMs) {
      lastSampleTime[j] = now;

      int v = digitalRead(btnPins[idx]);
      bool pressed = (v == PRESSED_LEVEL);

      // compare current sample to previous sample for THIS button
      if (v != lastSampleLevel[j]) {
        lastSampleLevel[j] = v;

        if (pressed && !noteOn[idx]) {
          sendMidiOn(idx);
          noteOn[idx] = true;
        } else if (!pressed && noteOn[idx]) {
          sendMidiOff(idx);
          noteOn[idx] = false;
        }
      }

      // after we’ve processed one sampled button, next cycle check the other one
      whichSample ^= 1;  // flip between 0 and 1
    }
  }


  delay(1);
}

