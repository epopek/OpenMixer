int pot1_pin = A0;
int pot2_pin = A5;

int pot1_val;
int pot2_val;

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
Serial.print(pot1_val); Serial.print(","); Serial.println(pot2_val);

}
