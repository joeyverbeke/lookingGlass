/* Sweep
  by BARRAGAN <http://barraganstudio.com>
  This example code is in the public domain.

  modified 8 Nov 2013
  by Scott Fitzgerald
  http://www.arduino.cc/en/Tutorial/Sweep
*/

#include <Servo.h>

Servo servoPan;
Servo servoTilt;

int lastPos_pan = 0;

void setup() {
  servoPan.attach(9);  // attaches the servo on pin 9 to the servo object
  servoTilt.attach(10);
  Serial.begin(9600);
  Serial.println("<Arduino is ready>");
}

void loop() {
  recvFromPi();
}

void recvFromPi() {

  if (Serial.available() > 0) {

    char servoType = Serial.read();
 
    if(servoType == 'p')
    { 
      //Serial.print('p');
      int panPos = Serial.parseInt();

      if(panPos > 135 || panPos < 45)
      {
        //panPos = 180-panPos;
        int posDif = abs(panPos - lastPos_pan);
        posDif /= 10;
  
        if(lastPos_pan < panPo
        {
          panPos = panPos - posDif;
          if(panPos < 0)
            panPos = 0;
        }
        else if(lastPos_pan > panPos)
        {
          panPos = panPos + posDif;
          if(panPos > 180)
            panPos = 180;
        }
        
        servoPan.write(panPos);
  
        lastPos_pan = panPos;
      }
    }
    else if(servoType == 't')
    {
      //Serial.print('t');
      int tiltPos = Serial.parseInt();

      //Serial.println(tiltPos);

      tiltPos = 180-tiltPos;

      servoTilt.write(tiltPos);
    }
    else
    {
      //do nothing
    }
    
  }
}

