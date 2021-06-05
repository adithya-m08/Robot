const int pingPin = 7; // Trigger Pin
const int echoPin = 6; // Echo Pin
long duration, cm;

void setup() {
   Serial.begin(9600);
   pinMode(pingPin, OUTPUT);
   pinMode(echoPin, INPUT);
}

void loop() {
   digitalWrite(pingPin, LOW);
   delayMicroseconds(2);
   digitalWrite(pingPin, HIGH);
   delayMicroseconds(10);
   digitalWrite(pingPin, LOW);

   duration = pulseIn(echoPin, HIGH);
   cm = duration/58.2;
   if(cm<=15)
    Serial.println(1);
   delay(100);
}