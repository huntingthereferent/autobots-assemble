#ifndef CONTROLLER_H
#define CONTROLLER_H

#include <stdint.h>

typedef struct {
    uint8_t stable_button;
    uint8_t candidate_button;
    uint8_t candidate_ms;
    uint8_t led_on;
} controller_t;

void controller_init(controller_t *controller);
void controller_tick_1ms(controller_t *controller, uint8_t raw_button_pressed);

#endif
