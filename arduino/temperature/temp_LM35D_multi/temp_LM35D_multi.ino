


int Npins = 4;

const int sensorPins[] = {
  0, 1, 2, 3
};

void setup() {
  // put your setup code here, to run once:

//analogReference(INTERNAL);//1.1 V arduino uno
analogReference(INTERNAL1V1);//1.1 V arduino mega
Serial.begin(9600);  
delay(2000);

}

void loop() {
  // put your main code here, to run repeatedly:

  for (int thisPin = 0; thisPin < Npins; thisPin++) {
    float sensorVal = analogRead(sensorPins[thisPin]);	    
    float temp = calculateTemp(sensorVal);	
    Serial.print(temp);
    if (thisPin < Npins-1){ 
      Serial.print(" ");
    }
  } 

//float sensorVal = analogRead(sensorPins[0]);
//float temp = calculateTemp(sensorVal);
//float voltage = sensorVal * 1100 / 1024; // Nsamples * (1100 mV / 1024) samples -> mV
//float temp = voltage / 10; // mV / 10 (mV/Celsius) --> Celsius a partire da 0

//Serial.print("Analog = "); 
//Serial.print(sensorVal);
//Serial.print(" ADC counts"); 
//Serial.print("      Voltage = ");
//Serial.print(voltage);
//Serial.print(" mV");
//Serial.print("      Temp = ");
//Serial.println(temp);
Serial.println("");

delay(1000);

}

float calculateTemp(float sensorValue){
  float temperature;
  float voltage = sensorValue * 1100 / 1024; // Nsamples * (1100 mV / 1024) samples -> mV	
  temperature = voltage / 10; // mV / 10 (mV/Celsius) --> Celsius a partire da 0
  return temperature;
}
