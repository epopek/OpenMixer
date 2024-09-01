int pot1_pin = A0;
int pot2_pin = A5;

int pot1_val;
int pot2_val;

int MinChange = 2; //this is the minumum amount of change required in the potentiometers reported value required to send over serial. 
int PreviousPot1Val;
int PreviousPot2Val;

const int list_size = 2;
int InputAxis[list_size] = {A0, A5}; //Enter pin names that the potentiometers are connected to here.
int InputAxisPreValues[list_size];

String StringAxis;

void setup() {
Serial.begin(9600);
for (int i = 0; i < list_size; i++) {
        InputAxisPreValues[i] = analogRead(InputAxis[i]);
        
  }
}

void loop() {
  ReadInputs();
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

