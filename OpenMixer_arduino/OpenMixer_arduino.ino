#define MAX_SERIAL_BUFFER_SIZE 64

uint8_t sindex = 0;

int pot1_pin = A0;
int pot2_pin = A5;

int pot1_val;
int pot2_val;

int MinChange = 2; //the pots must report this amount of change before data is sent over the serial to prevent constantly sending the same value.
int PreviousPot1Val;
int PreviousPot2Val;

static char buffer[MAX_SERIAL_BUFFER_SIZE];

const int list_size = 2;
int InputAxis[list_size] = {A0, A5};
int InputAxisPreValues[list_size];

String StringAxis;

void setup() {

  // put your setup code here, to run once:
Serial.begin(9600);
//Serial.println("Established");
for (int i = 0; i < list_size; i++) {
        InputAxisPreValues[i] = analogRead(InputAxis[i]);
  }
}

void loop() {

ReadInputs();

// pot1_val = analogRead(pot1_pin);
// pot2_val = analogRead(pot2_pin);

// pot1_val = map(pot1_val, 0, 1023, 0, 100);
// pot2_val = map(pot2_val, 0, 1023, 0, 100);

    // if (abs(pot1_val - PreviousPot1Val) >=MinChange||abs(pot2_val - PreviousPot2Val) >=MinChange){ //prevents Pots from sending data constantly (they only send when change is detected).
    //   //Serial.print(pot1_val); Serial.print(","); Serial.println(pot2_val);
    //   PreviousPot1Val = pot1_val;
    //   PreviousPot2Val = pot2_val;
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

void ProcessCommand(char*command){
   if (strncmp(command, "?POTS",5)==0){ //query the number of pots connected to the arduino on startup of the software.
    Serial.println("2");
  }
}

void ReadInputs() {
    StringAxis = ""; 
    bool change = false; 
    
    for (int i = 0; i < list_size; i++) {
        int ReadAxis = analogRead(InputAxis[i]);
        ReadAxis = map(ReadAxis, 0, 1023, 0, 100);
        StringAxis += String(ReadAxis) + String(",");

        if (abs(ReadAxis - InputAxisPreValues[i]) >= MinChange) {
            InputAxisPreValues[i] = ReadAxis;
            change = true; 
        }
    }
    if (change) {
        Serial.println(StringAxis);
    }
}
