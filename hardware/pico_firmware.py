"""
Firmware de referencia para el control basado en Raspberry Pi Pico W.

📌 Copia este archivo a la memoria del Pico como ``main.py`` usando Thonny.
📌 Asegúrate de ajustar los pines si tu cableado es diferente.
📌 El script publica eventos por el puerto USB (CDC Serial) que son
    consumidos por ``hardware.pico_controller`` en el equipo host.
"""

from machine import Pin, ADC
import time
import sys

BTN_PINS = {
    "ARRIBA": Pin(2, Pin.IN, Pin.PULL_UP),
    "IZQUIERDA": Pin(3, Pin.IN, Pin.PULL_UP),
    "DERECHA": Pin(4, Pin.IN, Pin.PULL_UP),
    "ABAJO": Pin(5, Pin.IN, Pin.PULL_UP),
}

LED_GPIO = 15
led = Pin(LED_GPIO, Pin.OUT)
led.value(0)

joystick_x = ADC(26)
joystick_y = ADC(27)
joystick_btn = Pin(28, Pin.IN, Pin.PULL_UP)

THRESHOLD_LOW = 20000
THRESHOLD_HIGH = 45000
DEBOUNCE_MS = 120

last_press = {name: 0 for name in BTN_PINS}
last_dir = None
last_btn_state = False


def send_event(event) -> None:
    print(event)
    # En MicroPython, sys.stdout puede no tener flush()
    # Usar try/except para compatibilidad
    try:
        sys.stdout.flush()
    except AttributeError:
        # En algunos entornos de MicroPython, flush() no está disponible
        # El print() ya envía los datos, así que podemos ignorar el error
        pass


def button_handler():
    global last_btn_state
    active = False
    now = time.ticks_ms()
    for name, pin in BTN_PINS.items():
        pressed = not pin.value()
        if pressed and time.ticks_diff(now, last_press[name]) > DEBOUNCE_MS:
            last_press[name] = now
            send_event(name)
            active = True
            # Encender LED cuando se presiona cualquier botón
            led.value(1)
    # Apagar LED si no hay botones activos (se manejará en joystick_handler también)


def joystick_handler():
    global last_dir, last_btn_state
    x = joystick_x.read_u16()
    y = joystick_y.read_u16()
    btn = not joystick_btn.value()

    # El joystick solo navega, no selecciona
    # Prefijo "JOY_" para distinguir del botón físico ABAJO
    direction = None
    joystick_moved = False
    
    if x < THRESHOLD_LOW:
        direction = "JOY_IZQUIERDA"
        joystick_moved = True
    elif x > THRESHOLD_HIGH:
        direction = "JOY_DERECHA"
        joystick_moved = True
    elif y < THRESHOLD_LOW:
        direction = "JOY_ARRIBA"
        joystick_moved = True
    elif y > THRESHOLD_HIGH:
        direction = "JOY_ABAJO"
        joystick_moved = True

    # Encender LED cuando el joystick se mueve
    if joystick_moved:
        led.value(1)
    elif direction is None:
        # Joystick en posición neutral, apagar LED después de un pequeño delay
        # (se manejará en el loop principal)
        pass

    # Solo enviar evento si hay una dirección nueva y diferente a la anterior
    # Cuando vuelve a neutral (direction is None), NO enviar ningún evento
    if direction and direction != last_dir:
        last_dir = direction
        send_event(direction)
    elif direction is None and last_dir is not None:
        # El joystick volvió a neutral, solo resetear last_dir sin enviar evento
        last_dir = None
        # NO enviar ningún evento aquí para evitar selecciones accidentales

    # Botón del joystick (GP28) = SELECT
    if btn and not last_btn_state:
        last_btn_state = True
        send_event("JOYSTICK")
        led.value(1)  # Encender LED cuando se presiona el botón del joystick
    elif not btn and last_btn_state:
        last_btn_state = False


print("🎮 Pico controller listo")
print("Enviando eventos por USB serial...")

# Variable para controlar el LED con delay
led_off_timer = 0
LED_OFF_DELAY_MS = 100  # Mantener LED encendido 100ms después del último movimiento

while True:
    button_handler()
    joystick_handler()
    
    # Apagar LED después de un delay si no hay actividad
    now_ms = time.ticks_ms()
    if led.value() == 1:
        if led_off_timer == 0:
            led_off_timer = now_ms
        elif time.ticks_diff(now_ms, led_off_timer) > LED_OFF_DELAY_MS:
            led.value(0)
            led_off_timer = 0
    else:
        led_off_timer = 0
    
    time.sleep(0.05)

