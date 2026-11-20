# Always-on MCU supervisor reference logic

C11 simulation of a low-power event controller: sleep/wake from PIR, NIR safety interlock state, power fault, bounded alert queue and event ACK. It has no physical GPIO, I2C/ADC, charging, battery hot-swap, RF, camera trigger or cryptographic drivers; therefore it is NOT safe for deployment or flash.

On development host:
\`\`\`bash
cc -std=c11 -Wall -Wextra -Werror -pedantic engineering/firmware/mcu_supervisor.c engineering/firmware/test_mcu.c -o /tmp/edge-mcu
/tmp/edge-mcu
\`\`\`

Next port after chosen MCU + BOM/power review: HAL for INA228 rail shunts, ambient/PCB temperature, tamper and PIR GPIO IRQ; RTC sequence/timestamp, FRAM buffered record; watchdog, UART authenticated host link, NIR hardware enable interlock, RF module UART/SPI, signed firmware and test harness in hardware-in-loop. The protective hardware circuit, not this code, must guarantee eye/thermal/battery safety.