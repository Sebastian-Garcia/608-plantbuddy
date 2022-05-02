#include <SPI.h>
#include <TFT_eSPI.h>
#include <WiFi.h>
#include <ArduinoJson.h>

int val = 0; //value for storing moisture value 
int soilPin = 5;//Declare a variable for the soil moisture sensor 
int soilPower = 7;//Variable for Soil moisture Power, to prevent ongoing power, and only when we need it.
bool ledOn = false;
//LED pins
const uint8_t RED_LED = 2;
const uint8_t GREEN_LED = 3;
const uint8_t BLUE_LED = 4;

// const uint8_t RED_PWM = 0;
// const uint8_t GREEN_PWM = 1;
// const uint8_t BLUE_PWM = 2;


TFT_eSPI tft = TFT_eSPI();




void setup() {
  Serial.begin(115200);

  //Set up LCD Screen
  tft.init();  //init screen
  tft.setRotation(2); //adjust rotation
  tft.setTextSize(1); //default font size, change if you want
  tft.fillScreen(TFT_BLACK); //fill background
  tft.setTextColor(TFT_PINK, TFT_BLACK); //set color of font to hot pink foreground, black background

  //Set up LED

  // //set up RED_PWM which we will control in this lab for red light:
  // ledcSetup(RED_PWM, 200, 8);//12 bits of PWM precision
  // ledcWrite(RED_PWM, 0); //0 is a 0% duty cycle for the NFET
  // ledcAttachPin(RED_LED, RED_PWM);
  // //set up GREEN_PWM which we will control in this lab for green light:
  // ledcSetup(GREEN_PWM, 200, 8);//12 bits of PWM precision
  // ledcWrite(GREEN_PWM, 0); //0 is a 0% duty cycle for the NFET
  // ledcAttachPin(GREEN_LED, GREEN_PWM);
  // //set up BLUE_PWM which we will control in this lab for blue light:
  // ledcSetup(BLUE_PWM, 200, 8);//12 bits of PWM precision
  // ledcWrite(BLUE_PWM, 0); //0 is a 0% duty cycle for the NFET
  // ledcAttachPin(BLUE_LED, BLUE_PWM);

  analogReadResolution(10);
  delay(100);
  //change_color(0, 0, 0); // Turns LED completely off to start
  //pinMode(soilPower, OUTPUT);//Set soilPower pin as an OUTPUT
  //digitalWrite(soilPower, LOW);
}

void loop() {
  Serial.print("Soil Moisture = ");    
  //get soil moisture value from the function below and print it
  

  //Clear screen, move cursor to top line, and print new sensor value
  tft.fillScreen(TFT_BLACK);
  tft.setCursor(0,0,1);
  val = readSoil();
  Serial.println(val);

  

  //Turn on LED (for now Blue for testing purposes)
  if (!ledOn){
    //Write to LED,
    //change_color(0,0,200); // Turns LED blue
    ledOn = true;
  }

  
  //This 5 second timefrme is used so you can test the sensor and see it change in real-time.
  //For in-plant applications, you will want to take readings much less frequently.
  delay(5000);//take a reading every second
}

int readSoil()
{
    //digitalWrite(soilPower, HIGH);//turn D7 "On"
    delay(10);//wait 10 milliseconds 
    val = analogRead(soilPin);//Read the SIG value form sensor 
    //digitalWrite(soilPower, LOW);//turn D7 "Off"

    tft.print("Soil Moisture = ");
    tft.println(val);
    tft.print("Category of Moisture: ");
    if (val < 250){
      tft.println("Dry");
    }
    else if (val < 500){
      tft.println("Wet but Underwatered");
    }
    else if (val < 750){
      tft.println("Moist, good moisture level");
    }
    else 
    {
      tft.println("Overwatered");
    }

    return val;//send current moisture value
}

// void change_color(int R, int G, int B){
//   ledcWrite(RED_PWM, 255- R);
//   ledcWrite(GREEN_PWM, 255 - G);
//   ledcWrite(BLUE_PWM, 255 - B);
// }
