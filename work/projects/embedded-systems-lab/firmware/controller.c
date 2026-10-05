#include "controller.h"

#define DEBOUNCE_MS 20

void controller_init(controller_t *controller) {
    controller->stable_button = 0;
    controller->candidate_button = 0;
    controller->candidate_ms = 0;
    controller->led_on = 0;
}

void controller_tick_1ms(controller_t *controller, uint8_t raw_button_pressed) {
    raw_button_pressed = raw_button_pressed ? 1 : 0;

    if (raw_button_pressed != controller->candidate_button) {
        controller->candidate_button = raw_button_pressed;
        controller->candidate_ms = 1;
        return;
    }

    if (controller->candidate_ms < DEBOUNCE_MS) {
        controller->candidate_ms++;
    }

    if (
        controller->candidate_ms == DEBOUNCE_MS &&
        controller->stable_button != controller->candidate_button
    ) {
        controller->stable_button = controller->candidate_button;

        if (controller->stable_button) {
            controller->led_on = controller->led_on ? 0 : 1;
        }
    }
}
