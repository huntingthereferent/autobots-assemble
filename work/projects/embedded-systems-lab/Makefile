MCU=atmega328p
F_CPU=16000000UL

AVR_CC=avr-gcc
AVR_OBJCOPY=avr-objcopy
AVR_SIZE=avr-size
HOST_CC=gcc

CFLAGS_AVR=-std=c11 -Os -Wall -Wextra -Werror -mmcu=$(MCU) -DF_CPU=$(F_CPU)
CFLAGS_HOST=-std=c11 -O2 -Wall -Wextra -Werror

BUILD=build

.PHONY: all firmware sim test size clean

all: firmware sim

$(BUILD):
	mkdir -p $(BUILD)

firmware: $(BUILD)/firmware.hex

$(BUILD)/firmware.elf: firmware/main.c firmware/controller.c firmware/controller.h | $(BUILD)
	$(AVR_CC) $(CFLAGS_AVR) firmware/main.c firmware/controller.c -o $@

$(BUILD)/firmware.hex: $(BUILD)/firmware.elf
	$(AVR_OBJCOPY) -O ihex -R .eeprom $< $@

sim: $(BUILD)/sim

$(BUILD)/sim: sim/sim.c firmware/controller.c firmware/controller.h | $(BUILD)
	$(HOST_CC) $(CFLAGS_HOST) sim/sim.c firmware/controller.c -o $@

test: $(BUILD)/sim
	$(BUILD)/sim

size: $(BUILD)/firmware.elf
	$(AVR_SIZE) -C --mcu=$(MCU) $(BUILD)/firmware.elf

clean:
	rm -rf $(BUILD)
