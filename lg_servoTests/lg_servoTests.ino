/* Sweep
 by BARRAGAN <http://barraganstudio.com>
 This example code is in the public domain.

 modified 8 Nov 2013
 by Scott Fitzgerald
 http://www.arduino.cc/en/Tutorial/Sweep
*/

#include <Servo.h>

Servo s1;
Servo s2;
Servo s3;

bool goingUp = true;

int s3_pos = 0;    // variable to store the servo position

void setup() {
  s1.attach(9);
  s2.attach(10);
  s3.attach(3);
  s1.write(90);
  s2.write(90);
  s3.write(90);
}

void loop() {
  s1.write(90);
  s2.write(30);
  s3.write(90);

  //backAndForth();  
  
  delay(10);
}

void backAndForth()
{
    if(goingUp)
  {
    s3_pos++;
    if(s3_pos >= 180)
      goingUp = false;
  }
  else
  {
    s3_pos--;
    if(s3_pos <= 0)
      goingUp = true;
  }
}



/*
void loop() {
  for (pos = 0; pos <= 180; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    myservo.write(pos); 
    //servo2.write(pos);// tell servo to go to position in variable 'pos'
    delay(5);                       // waits 15ms for the servo to reach the position
  }
  for (pos = 180; pos >= 0; pos -= 1) { // goes from 180 degrees to 0 degrees
    myservo.write(pos);
    //servo2.write(pos);// tell servo to go to position in variable 'pos'
    delay(5);                       // waits 15ms for the servo to reach the position
  }
}
*/
