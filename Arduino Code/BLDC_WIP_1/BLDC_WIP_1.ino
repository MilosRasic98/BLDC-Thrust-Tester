// Libraries we need
#include <Servo.h>
#include "HX711.h"
#include "TimerOne.h"

// All of the pin connection on the Arduino
#define pinRelay 2
#define pinESC 3
#define pinDT 4
#define pinSCK 5
#define pinCurrent A0

// Defining our scale and ESC
HX711 scale;
Servo ESC;

// Variables
int power = 0;
volatile long previousMillis = 0;
long previousMillis1 = 0;
double thrust = 0;
int current = 0;
int throttle = 0;
bool rise = true;

void setup() {
  
  Serial.begin(9600); 
  pinMode(pinRelay, INPUT);

  // This part will setup our load cell to work properly
  scale.begin(pinDT, pinSCK);
  scale.set_scale(-205);            
  scale.tare();

  // This part will turn on our ESC and the delay will 
  // let it to it's start up procedure
  ESC.attach(pinESC);
  ESC.write(0);
  delay(5000);
   
}

// Function for sending power to ESC - not currently used
void ControlESC(int pwr){
    if(pwr > 100) pwr = 100;
    if(pwr < 0) pwr = 0;
    int pwr1 = map(pwr, 0, 100, 0, 180);
    ESC.write(pwr1);
  }

// Function for sending data over Serial in a specific format
void SendData(int g, int c){
    s = "";
    s = "t" + String(0) + "g" + String(g) + "r" + String(0) + "c" + String(c) + "v" + String(0) + "e";
    Serial.println(s);
  }

void loop() {
  // This will read out our thrust every set amount of ms
  if(millis() - previousMillis >= 100){
      
      previousMillis = millis();
      thrust = scale.get_units();
      current = analogRead(pinCurrent);
      SendData(thrust, current);
    }

  // This will create a sawtooth style throttle curve
  if(millis() - previousMillis1 >= 500){
      previousMillis1 = millis();
      if(throttle >= 100) rise = false;
      if(throttle <= 0) rise = true;
      if(rise == true){
          throttle += 1;
          ESC.write(throttle);
        }
        else{
            throttle -= 1;
            ESC.write(throttle);
          }
      
    }
}
