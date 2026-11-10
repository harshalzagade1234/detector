// ESP32 + AS7341 + 365 nm UV LED -> prints one JSON line per scan over Serial (115200)
// Libraries: "Adafruit AS7341". Wiring: AS7341 SDA=21, SCL=22, 3V3, GND. UV LED via transistor on GPIO 25.
// Serial commands from PC: "S" = take one scan.
#include <Adafruit_AS7341.h>
Adafruit_AS7341 as7341;
const int UV_PIN = 25;
uint16_t r[12];

bool grab(uint16_t *out) {           // returns F1..F8, Clear, NIR
  if (!as7341.readAllChannels(r)) return false;
  out[0]=r[0]; out[1]=r[1]; out[2]=r[2]; out[3]=r[3];      // F1..F4 (415,445,480,515)
  out[4]=r[6]; out[5]=r[7]; out[6]=r[8]; out[7]=r[9];      // F5..F8 (555,590,630,680)
  out[8]=r[4]; out[9]=r[5];                                // Clear, NIR
  return true;
}

void setup() {
  Serial.begin(115200);
  pinMode(UV_PIN, OUTPUT); digitalWrite(UV_PIN, LOW);
  if (!as7341.begin()) { Serial.println("{\"error\":\"AS7341 not found\"}"); while (1) delay(10); }
  as7341.setATIME(100); as7341.setASTEP(999); as7341.setGain(AS7341_GAIN_64X);
}

void printArr(const char *name, uint16_t *v) {
  Serial.print("\""); Serial.print(name); Serial.print("\":[");
  for (int i = 0; i < 10; i++) { Serial.print(v[i]); if (i < 9) Serial.print(","); }
  Serial.print("]");
}

void loop() {
  if (Serial.available() && Serial.read() == 'S') {
    uint16_t dark[10], lit[10];
    digitalWrite(UV_PIN, LOW);  delay(100); grab(dark);   // ambient/dark reference
    digitalWrite(UV_PIN, HIGH); delay(300); grab(lit);    // fluorescence under UV
    digitalWrite(UV_PIN, LOW);
    Serial.print("{"); printArr("dark", dark); Serial.print(","); printArr("lit", lit); Serial.println("}");
  }
}
