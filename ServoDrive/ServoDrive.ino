// Basic serial interface for driving two servos.
// Runs at 115200 baud and accepts 2-byte commands to set the servo position with (approximately) 1-degree precision.

#include <Servo.h>

Servo servo1;
Servo servo2;
int tempByte = -1;

void setup() {
  // put your setup code here, to run once:
  pinMode(13, OUTPUT);
  Serial.begin(115200);
}

void loop() {

  while (Serial.available())
  {
    if (tempByte < 0)
    {
      tempByte = Serial.read();
      Serial.print(tempByte & 0x7F);
      if (tempByte == 255)
      {
        Serial.println("^C");
        tempByte = -1;
        break;
      }
      else if (tempByte & 0x80)
      {
        Serial.println(" OFF");
        if ((tempByte & 0x7F) == 0) servo1.detach();
        else if ((tempByte & 0x7F) == 1) servo2.detach();
        tempByte = -1;
        break;
      }
    }
    else
    {
      uint8_t pos = Serial.read();
      Serial.print(" ");
      Serial.println(pos);
      uint8_t servo_id = (uint8_t)tempByte;
      tempByte = -1;
      if (pos == 255)
      {
        Serial.println("^C");
        break;
      }

      if (servo_id == 0)
      {
        if (!servo1.attached()) 
          servo1.attach(2);
        servo1.write(pos);
      }
      else if (servo_id == 1)
      {
        if (!servo2.attached())
          servo2.attach(3);
        servo2.write(pos);
      }
    }
  }
  if (tempByte < 0) digitalWrite(13, LOW);
  else digitalWrite(13, HIGH);
}
