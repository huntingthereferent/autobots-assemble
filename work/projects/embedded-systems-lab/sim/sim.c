#include <assert.h>
#include <stdio.h>

#include "../firmware/controller.h"

static void tick(controller_t *controller, int pressed, int milliseconds) {
    for (int i = 0; i < milliseconds; ++i) {
        controller_tick_1ms(controller, pressed ? 1 : 0);
    }
}

int main(void) {
    controller_t controller;
    controller_init(&controller);

    assert(controller.led_on == 0);

    /* Contact bounce: transitions never remain stable for 20 ms. */
    for (int i = 0; i < 8; ++i) {
        tick(&controller, 1, 2);
        tick(&controller, 0, 2);
    }
    assert(controller.led_on == 0);

    /* First stable press toggles LED on exactly once. */
    tick(&controller, 1, 25);
    assert(controller.led_on == 1);
    tick(&controller, 1, 50);
    assert(controller.led_on == 1);

    /* Stable release arms the next press. */
    tick(&controller, 0, 25);
    assert(controller.led_on == 1);

    /* Second stable press toggles LED off. */
    tick(&controller, 1, 25);
    assert(controller.led_on == 0);

    printf("SIM PASS: bounce suppressed; two stable presses produced two toggles\n");
    return 0;
}
