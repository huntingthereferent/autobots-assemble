#include <avr/interrupt.h>
#include <avr/io.h>

#include "controller.h"

static controller_t controller;

static void gpio_init(void) {
    DDRB |= _BV(DDB5);
    DDRD &= ~_BV(DDD2);
    PORTD |= _BV(PORTD2);
}

static void timer0_init_1ms(void) {
    TCCR0A = _BV(WGM01);
    TCCR0B = _BV(CS01) | _BV(CS00);
    OCR0A = 249;
    TIMSK0 = _BV(OCIE0A);
}

ISR(TIMER0_COMPA_vect) {
    uint8_t pressed = (PIND & _BV(PIND2)) ? 0 : 1;
    controller_tick_1ms(&controller, pressed);

    if (controller.led_on) {
        PORTB |= _BV(PORTB5);
    } else {
        PORTB &= ~_BV(PORTB5);
    }
}

int main(void) {
    controller_init(&controller);
    gpio_init();
    timer0_init_1ms();
    sei();

    for (;;) {
    }
}
