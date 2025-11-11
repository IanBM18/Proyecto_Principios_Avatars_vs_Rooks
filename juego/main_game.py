#juego.main_game.py
import pygame
import os
import json
import time
from juego.coin_manager import CoinManager
from juego.enemy_manager import EnemyManager
from assets.MusicManager import MusicManager
from juego.rook_manager import RookManager
from juego.victoria import mostrar_victoria
from juego.derrota import mostrar_derrota
from gui.salon_fama import HallOfFameWindow

pygame.init()

# -------------------------------
# 🔹 CONFIGURACIÓN DEL TABLERO (VERTICAL)
# -------------------------------
COLUMNS = 5   # columnas
ROWS = 9      # filas
CELL_SIZE = 50
MARGIN = 2

GRID_WIDTH = COLUMNS * (CELL_SIZE + MARGIN) + MARGIN
GRID_HEIGHT = ROWS * (CELL_SIZE + MARGIN) + MARGIN

ANCHO = GRID_WIDTH + 400
ALTO = GRID_HEIGHT + 150

NEGRO = (0, 0, 0)
GRIS = (30, 30, 30)
BLANCO = (255, 255, 255)
CELDA = (70, 130, 180)
BTN_COLOR = (50, 50, 50)
BTN_HOVER = (70, 70, 70)
TXT_COLOR = (220, 220, 220)
VERDE = (60, 160, 60)
ROJO = (180, 50, 50)

clock = pygame.time.Clock()
FPS = 30


class GameWindow:
    def __init__(self, usuario, rol):
        self.usuario = usuario
        self.rol = rol

        self.start_time = time.time()  # 🔹 Guardar inicio del nivel

        os.environ["SDL_VIDEO_CENTERED"] = "1"

        # 🎵 Música de fondo
        self.music = MusicManager()
        if not self.music.playing:
            self.music.play(soundtrack_index=1, volume=0.5)

        # 🪟 Ventana
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Avatars VS Rooks - Partida")

        # 🟡 Managers
        self.left_offset = (ANCHO - GRID_WIDTH) // 2
        self.coin_manager = CoinManager(ROWS, COLUMNS, CELL_SIZE, MARGIN, GRID_WIDTH, ANCHO)
        self.enemy_manager = EnemyManager(ROWS, COLUMNS, CELL_SIZE, MARGIN, ANCHO)
        self.rook_manager = RookManager(ROWS, COLUMNS, CELL_SIZE, MARGIN, ANCHO)

        self.game_over = False
        self.score = 0

        
        

        # 🔘 Botón “Salir al menú”
        self.btn_width = 180
        self.btn_height = 36
        self.btn_x = ANCHO - self.btn_width - 12
        self.btn_y = 12
        self.btn_rect = pygame.Rect(self.btn_x, self.btn_y, self.btn_width, self.btn_height)

        # ▶️ Iniciar loop
        self.run_game()

    # -------------------------------
    # 🔸 GUARDAR PUNTAJE
    # -------------------------------
    def guardar_puntaje(self):
        try:
            os.makedirs("data", exist_ok=True)
            path = os.path.join("data", "salon_fama.json")

            entry = {
                "usuario": self.usuario,
                "rol": self.rol,
                "score": int(self.coin_manager.collected),
                "timestamp": int(time.time())
            }

            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        if not isinstance(data, list):
                            data = []
                    except Exception:
                        data = []
            else:
                data = []

            data.append(entry)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"[INFO] Puntaje guardado: {entry}")
        except Exception as e:
            print(f"[ERROR] No se pudo guardar el puntaje: {e}")

    # -------------------------------
    # 🔸 INTERFAZ DEL JUEGO
    # -------------------------------
    def dibujar_grid(self):
        """Dibuja la cuadrícula del campo de juego centrada horizontalmente."""
        self.pantalla.fill(GRIS)
        y_offset = 100

        for row in range(ROWS):
            for col in range(COLUMNS):
                x = self.left_offset + MARGIN + col * (CELL_SIZE + MARGIN)
                y = y_offset + MARGIN + row * (CELL_SIZE + MARGIN)
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.pantalla, CELDA, rect)
                pygame.draw.rect(self.pantalla, NEGRO, rect, 2)

    def draw_hud(self, fps):
        """Dibuja la barra superior con info del jugador y monedas."""
        font = pygame.font.SysFont(None, 26)
        texto = f"Jugador: {self.usuario} ({self.rol})"
        text_surf = font.render(texto, True, TXT_COLOR)
        self.pantalla.blit(text_surf, (10, 12))

        hint_surf = font.render("Usa el botón 'Salir al menú' para salir", True, TXT_COLOR)
        self.pantalla.blit(hint_surf, (10, 40))

        coins_text = font.render(f"Monedas: {self.coin_manager.collected}", True, (255, 215, 0))
        self.pantalla.blit(coins_text, (10, 72))

        fps_text = font.render(f"FPS: {int(fps)}", True, TXT_COLOR)
        self.pantalla.blit(fps_text, (ANCHO - 110, 12))

        # Botón "Salir al menú"
        mouse_pos = pygame.mouse.get_pos()
        hover = self.btn_rect.collidepoint(mouse_pos)
        color = BTN_HOVER if hover else BTN_COLOR
        pygame.draw.rect(self.pantalla, color, self.btn_rect, border_radius=6)

        btn_font = pygame.font.SysFont(None, 22)
        btn_text = btn_font.render("Salir al menú", True, TXT_COLOR)
        tx = self.btn_x + (self.btn_width - btn_text.get_width()) // 2
        ty = self.btn_y + (self.btn_height - btn_text.get_height()) // 2
        self.pantalla.blit(btn_text, (tx, ty))

    # -------------------------------
    # 🔸 CONFIRMACIÓN DE SALIDA
    # -------------------------------
    def mostrar_confirmacion(self):
        """Muestra un cuadro de confirmación para salir y guardar puntaje."""
        ancho, alto = 420, 160
        x = (ANCHO - ancho) // 2
        y = (ALTO - alto) // 2
        rect = pygame.Rect(x, y, ancho, alto)

        fuente = pygame.font.SysFont(None, 28)
        texto = fuente.render("¿Deseas salir y guardar tu progreso?", True, BLANCO)

        # Botones
        btn_si = pygame.Rect(x + 60, y + 90, 120, 40)
        btn_no = pygame.Rect(x + 240, y + 90, 120, 40)

        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return False
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if btn_si.collidepoint(e.pos):
                        return True
                    elif btn_no.collidepoint(e.pos):
                        return False

            pygame.draw.rect(self.pantalla, (20, 20, 20), rect, border_radius=10)
            pygame.draw.rect(self.pantalla, BLANCO, rect, 2)

            self.pantalla.blit(texto, (x + 35, y + 30))

            mouse = pygame.mouse.get_pos()
            pygame.draw.rect(self.pantalla, VERDE if btn_si.collidepoint(mouse) else BTN_COLOR, btn_si, border_radius=8)
            pygame.draw.rect(self.pantalla, ROJO if btn_no.collidepoint(mouse) else BTN_COLOR, btn_no, border_radius=8)

            texto_si = fuente.render("Sí", True, BLANCO)
            texto_no = fuente.render("No", True, BLANCO)
            self.pantalla.blit(texto_si, (btn_si.centerx - texto_si.get_width() // 2, btn_si.centery - texto_si.get_height() // 2))
            self.pantalla.blit(texto_no, (btn_no.centerx - texto_no.get_width() // 2, btn_no.centery - texto_no.get_height() // 2))

            pygame.display.flip()
            clock.tick(30)

    # -------------------------------
    # 🔸 LOOP PRINCIPAL
    # -------------------------------
    def run_game(self):
        running = True
        self.placing_rook = False  # bandera para modo colocar torres

        # Botón “Colocar torre”
        self.btn_rook_width = 180
        self.btn_rook_height = 36
        self.btn_rook_x = ANCHO - self.btn_rook_width - 12
        self.btn_rook_y = self.btn_y + self.btn_height + 10
        self.btn_rook_rect = pygame.Rect(self.btn_rook_x, self.btn_rook_y, self.btn_rook_width, self.btn_rook_height)

        font = pygame.font.SysFont(None, 26)

        while running:
            dt = clock.tick(FPS) / 1000
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    if self.confirmar_salida():
                        running = False
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    mouse_pos = evento.pos

                    # 1️⃣ Clic en botón salir
                    if self.btn_rect.collidepoint(mouse_pos):
                        if self.confirmar_salida():
                            running = False

                    # 2️⃣ Clic en botón colocar torre
                    elif self.btn_rook_rect.collidepoint(mouse_pos):
                        self.placing_rook = not self.placing_rook

                    # 3️⃣ Clic en grilla para colocar torre
                    elif self.placing_rook:
                        placed = self.rook_manager.place_rook(mouse_pos, self.coin_manager)
                        if placed:
                            self.placing_rook = False

                    # 4️⃣ Clic normal: recoger monedas
                    else:
                        self.coin_manager.check_collect(mouse_pos)

            # -------------------------------
            # Actualizar lógica
            # -------------------------------
            self.coin_manager.update()
            self.enemy_manager.update(dt, self.rook_manager)
            self.rook_manager.update(dt, self.enemy_manager.enemies)

            # -------------------------------
            # Verificar victoria
            # -------------------------------
            if self.enemy_manager.finished:
                tiempo_total = time.time() - self.start_time  # ⏱ Calcular duración
                # Registrar tiempo en el salón de la fama
                HallOfFameWindow.registrar_tiempo(self.usuario, nivel=1, tiempo=tiempo_total)
                # Mostrar pantalla de victoria
                mostrar_victoria(self.pantalla, self.usuario, clock)
                running = False

            # -------------------------------
            # Dibujar todo
            # -------------------------------
            self.dibujar_grid()
            self.coin_manager.draw(self.pantalla)
            self.enemy_manager.draw(self.pantalla)
            self.rook_manager.draw(self.pantalla, self.enemy_manager.enemies, self.enemy_manager.enemy_img)

            # Dibujar HUD y botones
            self.draw_hud(clock.get_fps())

            # Dibujar botón colocar torre
            hover_rook = self.btn_rook_rect.collidepoint(pygame.mouse.get_pos())
            color_rook = BTN_HOVER if hover_rook else BTN_COLOR
            pygame.draw.rect(self.pantalla, color_rook, self.btn_rook_rect, border_radius=6)
            btn_text_rook = pygame.font.SysFont(None, 22).render("Colocar torre", True, TXT_COLOR)
            tx_rook = self.btn_rook_x + (self.btn_rook_width - btn_text_rook.get_width()) // 2
            ty_rook = self.btn_rook_y + (self.btn_rook_height - btn_text_rook.get_height()) // 2
            self.pantalla.blit(btn_text_rook, (tx_rook, ty_rook))

            # Mensaje indicador de modo torre activo
            if self.placing_rook:
                text_surf = font.render("Modo colocar torre activo", True, (255, 255, 0))
                self.pantalla.blit(text_surf, (10, 100))

           # Mostrar enemigos restantes correctamente
            enemies_left = len(self.enemy_manager.enemies) + (self.enemy_manager.max_enemies - self.enemy_manager.spawned_count)
            text_surf2 = font.render(f"Enemigos restantes: {enemies_left}", True, (255, 255, 0))
            self.pantalla.blit(text_surf2, (10, 170))

            pygame.display.flip()

        # -------------------------------
        # Limpiar y volver al menú
        # -------------------------------
        self.cleanup_and_return()

    # -------------------------------
    # 🔸 CONFIRMAR SALIDA
    # -------------------------------
    def confirmar_salida(self):
        confirmar = self.mostrar_confirmacion()
        if confirmar:
            if not getattr(self, "game_over", False):
                self.guardar_puntaje()
            return True
        return False

    # -------------------------------
    # 🔸 CIERRE Y RETORNO AL MENÚ
    # -------------------------------
    def cleanup_and_return(self):
        try:
            pygame.display.quit()
        except Exception:
            pass

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            print(f"[WARN] No se pudo reiniciar mixer: {e}")

        from gui.menu_principal import MainMenu
        MainMenu(self.usuario, self.rol)
