#include <string.h>

unsigned long latest_emit_ms = 0;

#define MAX_MESSAGE_CHARS 128
#define START_MARKER '<'
#define END_MARKER '>'

char received_chars[MAX_MESSAGE_CHARS];
uint8_t partial = 0;

void setup() {
    Serial.begin(115200);
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
    uint8_t new_data = read_chunk();
    if (new_data == 1) {
      handle_command();
    }
  emit_data();
}

void emit_data() {
  unsigned long now_ms = millis();
  if (now_ms - latest_emit_ms > 50) {
    latest_emit_ms = now_ms;
    Serial.print("{\"time_ms\":");
    Serial.print(now_ms);
    Serial.print(", \"some_key\":1}\n");
    delay(10);
  }
}

uint8_t read_chunk() {
    uint8_t new_data = 0;
    static uint8_t receive_in_progress = 0;
    static uint8_t next_index = 0;

    char rc;
 
    while (Serial.available() > 0 && new_data == 0) {
      if (next_index + 1 >= MAX_MESSAGE_CHARS)
      {
        received_chars[next_index] = '\0';
        new_data = 1;
        next_index = 0;
        partial = 1;
        break;
      }
      partial = 0;
      
        rc = Serial.read();

        if (receive_in_progress == 1) {
            if (rc == END_MARKER) {
                // terminate the string
                received_chars[next_index] = '\0';
                new_data = 1;
               receive_in_progress = 0;
                next_index = 0;
                break;
            }
            else {
              received_chars[next_index] = rc;
              next_index += 1;
            }
        }
        else if (rc == START_MARKER) {
            receive_in_progress = 1;
        }
    }

    return new_data;
}

void handle_command() {
    // <command=command>
    char command[16];
    sscanf(
      received_chars,
      "command=%[^\t\n]",
      command
    );
    if (strcmp(command, "TURN_ON_LED") == 0) {
      digitalWrite(LED_BUILTIN, HIGH);
    } else if (strcmp(command, "TURN_OFF_LED") == 0) {
      digitalWrite(LED_BUILTIN, LOW);
    } else {
      //
    }

}