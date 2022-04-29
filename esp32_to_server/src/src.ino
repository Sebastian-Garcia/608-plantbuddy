#include <SPI.h>
#include <TFT_eSPI.h>
#include <WiFiClientSecure.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>
#include <string.h>


TFT_eSPI tft = TFT_eSPI();

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
const uint8_t IDLE = 0; //example definition
const uint8_t DOWN = 1; //example...
const uint8_t UP = 2; //change if you want!

WiFiClientSecure client; //global WiFiClient Secure object
WiFiClient client2; //global WiFiClient Secure object

const int BUTTON1 = 34;
const int BUTTON2 = 45;
const int BUTTON3 = 38;
int counter;
int offset;
int temp_num;
//choose one:
uint8_t state;  //system state (feel free to use)
unsigned long timer;  //used for storing millis() readings.


//const char NETWORK[] = "18_62";
//const char PASSWORD[] = "";
//
//
const char NETWORK[] = "MIT GUEST";
const char PASSWORD[] = "";
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
  int counter = 0;
  Serial.begin(115200);               // Set up serial port
  pinMode(BUTTON1, INPUT_PULLUP); //set input pin as an input!
  pinMode(BUTTON2, INPUT_PULLUP); //set input pin as an input!
  pinMode(BUTTON3, INPUT_PULLUP); //set input pin as an input!
  state = IDLE; //start system in IDLE state!
  //SET UP SCREEN:
  tft.init();  //init screen
  tft.setRotation(2); //adjust rotation
  tft.setTextSize(1); //default font size, change if you want
  tft.fillScreen(TFT_BLACK); //fill background
  tft.setTextColor(TFT_PINK, TFT_BLACK); //set color of font to hot pink foreground, black background

  //SET UP BUTTON:
  delay(100); //wait a bit (100 ms)

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

//main body of code
void loop() {
  
  if(!digitalRead(BUTTON1)){
    sprintf(request_buffer,"GET http://608dev-2.net/sandbox/sc/timmyd/milestone_1/server.py HTTP/1.1\r\n");
    strcat(request_buffer,"Host: 608dev-2.net\r\n");
    strcat(request_buffer,"\r\n"); //new line from header to body
    Serial.println(request_buffer);
    do_http_request("608dev-2.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT,true);
    Serial.println(response_buffer);
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, response_buffer);
    
  }
  if(!digitalRead(BUTTON2)){
    int len = strlen(json_body);
    request[0] = '\0'; //set 0th byte to null
    offset = 0; //reset offset variable for sprintf-ing
    offset += sprintf(request + offset, "POST http://608dev-2.net/sandbox/sc/timmyd/milestone_1/server.py?temp_num=%d  HTTP/1.1\r\n", counter);
    offset += sprintf(request + offset, "Host: 608dev-2.net\r\n");
    offset += sprintf(request + offset, "Content-Type: application/json\r\n");
    offset += sprintf(request + offset, "cache-control: no-cache\r\n");
    offset += sprintf(request + offset, "Content-Length: %d\r\n\r\n", len);
    offset += sprintf(request + offset, "%s\r\n", json_body);
    do_http_request("608dev-2.net", request, response, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT, true);
    Serial.println("-----------");
    Serial.println(response);
    Serial.println("-----------");
    counter = 0;
  }
  switch(state){
    case IDLE:
      if(!digitalRead(BUTTON3)){
        state = DOWN;
      }
      break; //don't forget break statements
    case DOWN:
      if(digitalRead(BUTTON3)){
        timer = millis(); 
        state = UP;
        counter += 1;
        Serial.println(counter);
      }
      break;
    case UP:
      
      if (millis()-timer < BUTTON_TIMEOUT){

        if(!digitalRead(BUTTON3)){
          state = DOWN;
        }else{
          state = IDLE;
        }
    
    }
  }

}

