#include <SPI.h>
#include <TFT_eSPI.h>
#include <math.h>
#include <Adafruit_BMP280.h>
#include <WiFiClientSecure.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>
#include <string.h>
Adafruit_BMP280 bmp; // I2C

TFT_eSPI tft = TFT_eSPI();
const int LOOP_PERIOD = 50;     //speed of main loop
const int freq = 100;
const int resolution = 12;
int loop_timer;                 //used for loop timing
int sample_timer;               //used for 2-hour sample timing
int num_samples;
const int thirty_minutes = 500;
const int full_day = 24000;
uint8_t button_state; //used for containing button state and detecting edges
int old_button_state; //used for detecting button edges
float sampling_period_sunlight;
float last_sunlight;
const uint8_t BUTTON = 45;
float temp_count;
float moist_count;

const uint16_t RESPONSE_TIMEOUT = 6000;
const uint16_t IN_BUFFER_SIZE = 3500; //size of buffer to hold HTTP request
const uint16_t OUT_BUFFER_SIZE = 1000; //size of buffer to hold HTTP response
const uint16_t JSON_BODY_SIZE = 3000;
char request[IN_BUFFER_SIZE];
char request_buffer[IN_BUFFER_SIZE];
char response[OUT_BUFFER_SIZE]; //char array buffer to hold HTTP request
char response_buffer[IN_BUFFER_SIZE];
char json_body[JSON_BODY_SIZE];
const int BUTTON_TIMEOUT = 1000; //button timeout in milliseconds
int offset;

WiFiClientSecure client; //global WiFiClient Secure object
WiFiClient client2; //global WiFiClient Secure object

int val = 0; //value for storing moisture value 
int soilPin = 5;//Declare a variable for the soil moisture sensor 
bool ledOn = false;
//const uint8_t SOIL_PWM = 0; //Variable for Soil moisture Power, to prevent ongoing power, and only when we need it.


const char NETWORK[] = "MIT GUEST";
const char PASSWORD[] = "";
const char user[] = "alexplantbuddy608@gmail.com";
const char plant[] = "bob";
int old_count;
int count;
//
//const char NETWORK[] = "608_24G";
//const char PASSWORD[] = "608g2020";

/* Having network issues since there are 50 MIT and MIT_GUEST networks?. Do the following:
    When the access points are printed out at the start, find a particularly strong one that you're targeting.
    Let's say it is an MIT one and it has the following entry:
   . 4: MIT, Ch:1 (-51dBm)  4:95:E6:AE:DB:41
   Do the following...set the variable channel below to be the channel shown (1 in this example)
   and then copy the MAC address into the byte array below like shown.  Note the values are rendered in hexadecimal
   That is specified by putting a leading 0x in front of the number. We need to specify six pairs of hex values so:
   a 4 turns into a 0x04 (put a leading 0 if only one printed)
   a 95 becomes a 0x95, etc...
   see starting values below that match the example above. Change for your use:
   Finally where you connect to the network, comment out
     WiFi.begin(network, password);
   and uncomment out:
     WiFi.begin(network, password, channel, bssid);
   This will allow you target a specific router rather than a random one!
*/
uint8_t channel = 1; //network channel on 2.4 GHz
byte bssid[] = {0x04, 0x95, 0xE6, 0xAE, 0xDB, 0x41}; //6 byte MAC address of AP you're targeting.

void setup() {
  unsigned status;
  status = bmp.begin();
  if (!status) {
    Serial.println(F("Could not find a valid BMP280 sensor, check wiring or "
                     "try a different address!"));
    Serial.print("SensorID was: 0x"); Serial.println(bmp.sensorID(), 16);
    esp_restart();
  }
  /* Default settings from datasheet. */
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,     /* Operating Mode. */
                  Adafruit_BMP280::SAMPLING_X2,     /* Temp. oversampling */
                  Adafruit_BMP280::SAMPLING_X16,    /* Pressure oversampling */
                  Adafruit_BMP280::FILTER_X16,      /* Filtering. */
                  Adafruit_BMP280::STANDBY_MS_500); /* Standby time. */
  Serial.println("bmp280 setup done");
  analogReadResolution(12);       // initialize the analog resolution
  Serial.begin(115200);           // Set up serial port
  delay(100); 
  //TFT initializtation stuff:
  tft.init();  //init screen
  tft.setRotation(2); //adjust rotation
  tft.setTextSize(1); //default font size
  tft.fillScreen(TFT_WHITE); //fill background
  tft.setTextColor(TFT_BLACK, TFT_WHITE); //set color for font
  tft.setCursor(0, 0, 2); //set cursor
  tft.printf("Test");
  delay(100); //wait a bit (100 ms)
  pinMode(BUTTON, INPUT_PULLUP);

  //Set up PWM for soil
  //pinMode(SOIL_PWM, OUTPUT); // Setup PWM For Soil
  //digitalWrite(SOIL_PWM, LOW);


  loop_timer = millis();
  sample_timer = millis();
  num_samples = 0;
  sampling_period_sunlight = 0;
  last_sunlight = 0;
  temp_count = 0;
  moist_count = 0;

    //PRINT OUT WIFI NETWORKS NEARBY
  int n = WiFi.scanNetworks();
  Serial.println("scan done");
  if (n == 0) {
    Serial.println("no networks found");
  } else {
    Serial.print(n);
    Serial.println(" networks found");
    for (int i = 0; i < n; ++i) {
      Serial.printf("%d: %s, Ch:%d (%ddBm) %s ", i + 1, WiFi.SSID(i).c_str(), WiFi.channel(i), WiFi.RSSI(i), WiFi.encryptionType(i) == WIFI_AUTH_OPEN ? "open" : "");
      uint8_t* cc = WiFi.BSSID(i);
      for (int k = 0; k < 6; k++) {
        Serial.print(*cc, HEX);
        if (k != 5) Serial.print(":");
        cc++;
      }
      Serial.println("");
    }
  }
  delay(100); //wait a bit (100 ms)

  //if using regular connection use line below:
  WiFi.begin(NETWORK, PASSWORD);
  //if using channel/mac specification for crowded bands use the following:
  //WiFi.begin(network, password, channel, bssid);

  uint8_t count = 0; //count used for Wifi check times
  Serial.print("Attempting to connect to ");
  Serial.println(NETWORK);
  while (WiFi.status() != WL_CONNECTED && count < 12) {
    delay(500);
    Serial.print(".");
    count++;
  }
  delay(2000);
  if (WiFi.isConnected()) { //if we connected then print our IP, Mac, and SSID we're on
    Serial.println("CONNECTED!");
    Serial.printf("%d:%d:%d:%d (%s) (%s)\n", WiFi.localIP()[3], WiFi.localIP()[2],
                  WiFi.localIP()[1], WiFi.localIP()[0],
                  WiFi.macAddress().c_str() , WiFi.SSID().c_str());
    delay(500);
  } else { //if we failed to connect just Try again.
    Serial.println("Failed to Connect :/  Going to restart");
    Serial.println(WiFi.status());
    ESP.restart(); // restart the ESP (proper way)
  }


}

void loop() {

    // drawEmotion(true);
    // constant GET request
    sprintf(request_buffer,"GET /sandbox/sc/team58/plantbuddy/server.py?user=%s&name=%s&from=arduino HTTP/1.1\r\n", user, plant);
    strcat(request_buffer,"Host: 608dev-2.net\r\n");
    strcat(request_buffer,"\r\n"); //new line from header to body
    do_http_request("608dev-2.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT,true);
    old_count = count;
    count = atoi(response_buffer);
    

  // when GET request tells ESP32 to start new sampling period
  button_state = digitalRead(BUTTON);

  if (count != old_count || (!button_state && button_state != old_button_state)){
    clear_screen(tft);
    tft.setCursor(0, 0, 2);
    num_samples = 0;
    sample_timer = millis();
    sampling_period_sunlight = 0;
    temp_count = 0;
    moist_count = 0;
  }

  if (num_samples > 48){
    return;
  }
  if (num_samples == 48) {
    json_body[0] = '\0';

    sprintf(json_body, "name=%s&user=%s&sunlight=%0.1f&temperature=%0.1f&moisture=%0.1f&from=arduino", plant, user, sampling_period_sunlight/2.0, temp_count/48.0, (moist_count/48.0)/4096.0*100.0);

    int len = strlen(json_body);
    request[0] = '\0'; //set 0th byte to null
    offset = 0; //reset offset variable for sprintf-ing
    offset += sprintf(request + offset, "POST /sandbox/sc/team58/plantbuddy/server.py HTTP/1.1\r\n");
    offset += sprintf(request + offset, "Host: 608dev-2.net\r\n");
    offset += sprintf(request + offset, "Content-Type: application/x-www-form-urlencoded\r\n");
    // offset += sprintf(request + offset, "cache-control: no-cache\r\n");
    offset += sprintf(request + offset, "Content-Length: %d\r\n\r\n", len);
    offset += sprintf(request + offset, "%s\r\n", json_body);
    do_http_request("608dev-2.net", request, response, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT, true);

    Serial.println("-----------");
    Serial.println(response);
    Serial.println("-----------");

    sample_timer = millis();
    num_samples += 1;

    tft.setCursor(0, 0, 2); //set cursor

    tft.printf("Your plant absorbed %0.1f foot-candles of sunlight at an average temperature of %0.1f degrees Celsius", sampling_period_sunlight/2.0, temp_count/48.0);
  }

  if (millis() - sample_timer > thirty_minutes && num_samples < 48) {
    // SAMPLING State
    Serial.println("sampling");
    float temperature = bmp.readTemperature(); //variable for temperature
    float pressure = bmp.readPressure();    //variable for pressure
    float brightness = sample_brightness();
    float moisture = readSoil();
    tft.setCursor(0, 0, 2); //set cursor

    tft.printf("Foot-Candles: %0.1f\n", brightness*.092903);
    sampling_period_sunlight += brightness*.092903;
    tft.printf("Temp.(C): %d\n", (int)temperature);
    temp_count += temperature;
    tft.printf("Pres.(hPa): %0.1f\n", pressure*.01);
    moist_count += moisture;

    sample_timer = millis();
    num_samples += 1;
  }

  old_button_state = button_state;
  while (millis()-loop_timer<LOOP_PERIOD);
  loop_timer = millis();
}





float sample_brightness(){
  float brightness;
  float stored_values[100];
  int index = 0;

  for (int i=0; i<50; i++){
    int photoVal = analogRead(3);
    float vout = (photoVal) / 4096.0 * 3.3;
    float input = brightnessExtractor(vout);
    if (input > 9999){
      input = 9999;
    }
    brightness = averaging_filter(input, stored_values, 50, &index);
  }

  return brightness;
}

float averaging_filter(float input, float* stored_values, int order, int* index) {
    if (order == 0){
    stored_values[0] = input;
    return input;
  }
  stored_values[*index] = input;
  if (*index == order){
    *index = 0;
  }else{
    *index += 1;
  }
  float total = 0;
  for (int i = 0; i < order; i++){
    total += stored_values[i];
  }
  return total/(order + 1);
}

float resistanceExtractor(float vin,float rb,float vout){
    return (vout/vin*rb) / (1 - vout/vin);
}

float brightnessExtractor(float vout){
    float resis = resistanceExtractor(3.3, 20000, vout);
    float logR = log10(resis);
    return pow(10, (logR - 8.65)/-2);
}

void clear_screen(TFT_eSPI tft){
  tft.setCursor(0, 0, 2); //set cursor
  tft.fillScreen(TFT_WHITE);
  tft.printf("Sampling");
}

int readSoil(){
    //Use PWM Channel to turn on Soil Pin only when trying to read a value.

    //digitalWrite(SOIL_PWM, HIGH);
    delay(10);
    val = analogRead(soilPin);//Read the SIG value form sensor 
    //digitalWrite(SOIL_PWM, LOW);

    return val;//send current moisture value
}


void drawEmotion(bool happy){
  tft.fillScreen(TFT_WHITE); //fill background
  tft.setCursor(0,0,10);
  if (happy == true) {
    tft.print(":)");
  }
  else{
    tft.print(":(");
  }
}