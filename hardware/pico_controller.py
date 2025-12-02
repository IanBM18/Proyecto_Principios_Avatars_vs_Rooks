import json
import os
import queue
import threading
import time
from typing import Callable, Optional

try:
    import serial  # type: ignore
    from serial import Serial, SerialException  # type: ignore
except ImportError:  # pragma: no cover - pyserial not installed
    serial = None  # type: ignore
    Serial = object  # type: ignore

    class SerialException(Exception):  # type: ignore
        """Fallback SerialException when pyserial is unavailable."""


CONFIG_PATH = os.path.join("DATA", "controller_config.json")

DEFAULT_CONFIG = {
    "enabled": True,
    "serial_port": "COM3",
    "baudrate": 115200,
    "retry_interval": 2.0,
}

# Map raw strings coming from the Pico firmware to normalized events.
# Configuración según especificaciones:
# - Joystick solo navega (UP/DOWN/LEFT/RIGHT) - eventos con prefijo "JOY_"
# - Botón ABAJO (GP5) o botón JOYSTICK (GP28) = SELECT
# - Botón DERECHA (GP4) = BACK
LINE_EVENT_MAP = {
    # Botones físicos
    "ARRIBA": "UP",
    "ABAJO": "SELECT",  # GP5 = Seleccionar
    "IZQUIERDA": "LEFT",
    "DERECHA": "BACK",  # GP4 = Regresar
    # Joystick navegación (solo movimiento)
    "JOY_ARRIBA": "UP",
    "JOY_ABAJO": "DOWN",
    "JOY_IZQUIERDA": "LEFT",
    "JOY_DERECHA": "RIGHT",
    # Botón del joystick
    "JOYSTICK": "SELECT",  # GP28 = Seleccionar
    # Eventos adicionales
    "BTN_OK": "SELECT",
    "BTN_CANCEL": "BACK",
    "BTN_EXIT": "BACK",
    "BTN_MENU": "START",
    "BTN_RESET": "RESET",
}


class PicoController:
    """
    Listens for events published by a Raspberry Pi Pico W over USB serial.

    The Pico firmware should emit short text messages (one per line)
    describing the button/joystick actions. Those messages are translated
    into high-level events that the GUI can consume.
    """

    def __init__(
        self,
        event_queue: queue.Queue[str],
        config_path: str = CONFIG_PATH,
        on_status: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.event_queue = event_queue
        self.config_path = config_path
        self.on_status = on_status
        self.config = self._load_config()
        self.serial: Optional[Serial] = None
        self.thread: Optional[threading.Thread] = None
        self.running = False

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def start(self) -> None:
        """Start background thread if controller is enabled."""
        if not self.config.get("enabled", True):
            self._report("PicoController disabled via config.")
            return

        if serial is None:
            self._report(
                "pyserial is not installed. Run `pip install pyserial` "
                "to enable Pico controller support."
            )
            return

        if self.thread and self.thread.is_alive():
            return

        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self._report("PicoController thread started.")

    def stop(self) -> None:
        """Terminate the background thread and close the serial port."""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.5)
        self.thread = None
        self._close_serial()
        self._report("PicoController stopped.")

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _load_config(self) -> dict:
        config = DEFAULT_CONFIG.copy()
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as cfg:
                    config.update(json.load(cfg))
            except (OSError, json.JSONDecodeError) as exc:
                self._report(f"Unable to read controller config: {exc}")
        else:
            # Persist default config as a convenience for the user.
            try:
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, "w", encoding="utf-8") as cfg:
                    json.dump(config, cfg, indent=2)
            except OSError as exc:
                self._report(f"Unable to create default config: {exc}")
        return config

    def _run(self) -> None:
        """Attempt to connect and dispatch events until stopped."""
        retry_interval = float(self.config.get("retry_interval", 2.0))
        last_error_time = 0.0
        error_cooldown = 5.0  # Solo mostrar el mismo error cada 5 segundos
        
        while self.running:
            if not self.serial or not self.serial.is_open:
                if not self._open_serial():
                    time.sleep(retry_interval)
                    continue
            try:
                self._listen_loop()
            except SerialException as exc:
                self._report(f"Serial error: {exc}. Reconnecting...")
                self._close_serial()
                time.sleep(retry_interval)
            except Exception as exc:
                # Manejar otros errores (como PermissionError)
                now = time.time()
                if now - last_error_time >= error_cooldown:
                    self._handle_connection_error(exc)
                    last_error_time = now
                self._close_serial()
                time.sleep(retry_interval)

    def _open_serial(self) -> bool:
        port = self.config.get("serial_port")
        baudrate = int(self.config.get("baudrate", 115200))
        if not port:
            self._report(
                "No serial port specified for PicoController. "
                "Update DATA/controller_config.json with the correct COM port."
            )
            return False

        try:
            # Intentar cerrar el puerto si está abierto (por si otro proceso lo dejó abierto)
            try:
                temp_serial = serial.Serial(port, baudrate=baudrate, timeout=0.05)
                temp_serial.close()
                time.sleep(0.2)  # Pequeña pausa para que el sistema libere el puerto
            except:
                pass  # Ignorar si no se puede cerrar
            
            self.serial = serial.Serial(port, baudrate=baudrate, timeout=0.05)
            self._report(f"✅ Connected to Pico controller on {port}.")
            # Give the Pico a moment to finish its reset splash log.
            time.sleep(1)
            return True
        except PermissionError as exc:
            self._report(
                f"⚠️  COM port {port} está siendo usado por otro programa.\n"
                f"   Cierra Thonny, monitor serial u otro programa que use {port}.\n"
                f"   Error: {exc}"
            )
            self.serial = None
            return False
        except SerialException as exc:
            error_msg = str(exc).lower()
            if "permission" in error_msg or "acceso denegado" in error_msg:
                self._report(
                    f"⚠️  COM port {port} está bloqueado.\n"
                    f"   Cierra Thonny, monitor serial u otro programa que use {port}."
                )
            else:
                self._report(f"Unable to open {port}: {exc}")
            self.serial = None
            return False
        except Exception as exc:
            self._report(f"Unexpected error opening {port}: {exc}")
            self.serial = None
            return False
    
    def _handle_connection_error(self, exc: Exception) -> None:
        """Maneja errores de conexión con mensajes útiles."""
        error_str = str(exc).lower()
        port = self.config.get("serial_port", "COM?")
        
        if "permission" in error_str or "acceso denegado" in error_str:
            self._report(
                f"⚠️  COM port {port} está siendo usado por otro programa.\n"
                f"   SOLUCIÓN: Cierra Thonny, monitor serial u otro programa que use {port}."
            )
        elif "file not found" in error_str or "no se puede encontrar" in error_str:
            self._report(
                f"⚠️  COM port {port} no existe.\n"
                f"   SOLUCIÓN: Verifica que la Pico esté conectada y el puerto correcto en DATA/controller_config.json"
            )
        else:
            self._report(f"Error de conexión con {port}: {exc}")

    def _close_serial(self) -> None:
        if self.serial and self.serial.is_open:
            try:
                self.serial.close()
            except SerialException:
                pass
        self.serial = None

    def _listen_loop(self) -> None:
        """Continuously read lines and push events to the queue."""
        assert self.serial is not None
        while self.running and self.serial.is_open:
            raw = self.serial.readline()
            if not raw:
                continue
            try:
                line = raw.decode("utf-8", errors="ignore").strip()
            except UnicodeDecodeError:
                continue
            if not line:
                continue
            event = self._translate_line(line)
            if event:
                self.event_queue.put(event)

    def _translate_line(self, line: str) -> Optional[str]:
        """Convert device output to a normalized event name."""
        # Filtrar líneas vacías o que no sean eventos válidos
        normalized = line.strip().upper()
        if not normalized or len(normalized) == 0:
            return None
        
        # Ignorar mensajes de debug o inicialización del firmware
        if normalized.startswith("🎮") or "CONTROLLER" in normalized or "LISTO" in normalized:
            return None
        
        for key, event in LINE_EVENT_MAP.items():
            if key in normalized:
                return event

        if normalized.startswith("BTN_"):
            # Allow arbitrary BTN_<NAME> events coming from firmware.
            return normalized.replace("BTN_", "", 1)

        return None

    def _report(self, message: str) -> None:
        if self.on_status:
            self.on_status(message)
        else:
            print(f"[PicoController] {message}")

