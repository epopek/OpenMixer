#define MAX_SERIAL_BUFFER_SIZE 64

uint8_t sindex = 0;

int pot1_pin = A0;
int pot2_pin = A5;

int pot1_val;
int pot2_val;

int MinChange = 2; //the pots must report this amount of change before data is sent over the serial to prevent constantly sending the same value
int PreviousPotVal;

static char buffer[MAX_SERIAL_BUFFER_SIZE];

void setup() {
  // put your setup code here, to run once:
Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
pot1_val = analogRead(pot1_pin);
pot2_val = analogRead(pot2_pin);

pot1_val = map(pot1_val, 0, 1023, 0, 100);
pot2_val = map(pot2_val, 0, 1023, 0, 100);

    if (abs(pot1_val - PreviousPotVal) >=MinChange||abs(pot2_val - PreviousPotVal) >=MinChange){ //prevents Pots from sending data constantly (they only send when change is detected)
      Serial.print(pot1_val); Serial.print(","); Serial.println(pot2_val);
      PreviousPotVal = pot1_val;
    // }

  if (Serial.available() > 0){
    char incomingChar = Serial.read();
    if (incomingChar == '\r' || incomingChar == '\n'){
      buffer[sindex] = '\0';
      ProcessCommand(buffer);
      sindex = 0;
      } else {
        if (sindex < MAX_SERIAL_BUFFER_SIZE - 1){
          buffer[sindex++] = incomingChar;
        }
      }
    }
  }
}

void ProcessCommand(char*command){
   if (strncmp(command, "?POTS",5)==0){ //query the number of pots connected to the arduino on startup of the software.
    Serial.println("2");
  }
}
