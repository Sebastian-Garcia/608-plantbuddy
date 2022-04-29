#include <SPI.h>
#include <TFT_eSPI.h>
#include <math.h>
#include <Adafruit_BMP280.h>
Adafruit_BMP280 bmp; // I2C

TFT_eSPI tft = TFT_eSPI();
const int LOOP_PERIOD = 50;     //speed of main loop
const int freq = 100;
const int resolution = 12;
int loop_timer;                 //used for loop timing
int sample_timer;                 //used for 2-hour sample timing
int num_samples;
const int two_seconds = 2000;
const int two_hours = 7200000;
uint8_t button_state; //used for containing button state and detecting edges
int old_button_state; //used for detecting button edges
float sampling_period_sunlight;
float last_sunlight;
const uint8_t BUTTON = 45;
float temp_count;

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

  loop_timer = millis();
  sample_timer = millis();
  num_samples = 0;
  sampling_period_sunlight = 0;
  last_sunlight = 0;
  temp_count = 0;
}

void loop() {
  button_state = digitalRead(BUTTON);

  if (!button_state && button_state != old_button_state){
    clear_screen(tft);
    tft.setCursor(0, 0, 2);
    num_samples = 0;
    sample_timer = millis();
    sampling_period_sunlight = 0;
    temp_count = 0;
  }

  if (num_samples >= 12) {
      Serial.println("finished with sampling period");
      tft.setCursor(0, 0, 2); //set cursor
      tft.printf("Your plant soaked up %0.1f foot-candle-seconds at an average temperature of %0.1f degrees Celsius!\n", sampling_period_sunlight, temp_count/12.0);
      tft.printf("                   \n");
      tft.printf("Press button after taking proper action.");

      sample_timer = millis();
  }

  if (millis() - sample_timer > two_seconds && num_samples < 12) {
    Serial.println("sampling");
    float temperature = bmp.readTemperature(); //variable for temperature
    float pressure = bmp.readPressure();    //variable for pressure
    float brightness = sample_brightness();
    tft.setCursor(0, 0, 2); //set cursor
    Serial.println(brightness);

    tft.printf("Lux: %0.1f\n", brightness);
    tft.printf("Foot-Candles: %0.1f\n", brightness*.092903);
    sampling_period_sunlight += last_sunlight + brightness*.092903;
    last_sunlight = brightness*.092903;
    tft.printf("Temp.(C): %d\n", (int)temperature);
    temp_count += temperature;
    tft.printf("Pres.(hPa): %0.1f\n", pressure*.01);
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
  tft.printf("                                                                                                                                                                                                                                                                    ");
}

