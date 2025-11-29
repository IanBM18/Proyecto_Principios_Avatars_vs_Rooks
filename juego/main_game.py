# juego/main_game.py
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
FPS = 60  # más fluidez


class GameWindow:
    def __init__(self, usuario, rol):

        # ---------------------------
        # COORDENADAS OFICIALES DEL GRID
        # ---------------------------
        self.rows = ROWS
        self.cols = COLUMNS
        self.cell_size = CELL_SIZE
        self.margin = MARGIN

        self.left_offset = (ANCHO - GRID_WIDTH) // 2
        self.top_offset = 100  # donde inicia el grid verticalmente
        self.screen_width = ANCHO

        # usuario / rol
        self.usuario = usuario
        self.rol = rol

        self.start_time = time.time()

        os.environ["SDL_VIDEO_CENTERED"] = "1"

        # 🎵 Música
        self.music = MusicManager()
        if not self.music.playing:
            self.music.play(soundtrack_index=1, volume=0.5)

        # 🪟 Ventana (inicializar antes de cargar imágenes de pygame en managers)
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Avatars VS Rooks - Partida")

        # ---------------------------
        # MANAGERS (TODOS USANDO MISMAS COORDENADAS)
        # ---------------------------
        self.coin_manager = CoinManager(
            self.rows,
            self.cols,
            self.cell_size,
            self.margin,
            GRID_WIDTH,
            ANCHO
        )

        self.enemy_manager = EnemyManager(
            game=self,
            rows=self.rows,
            cols=self.cols,
            cell_size=self.cell_size,
            margin=self.margin,
            screen_width=ANCHO,
            max_enemies=10
        )

        self.rook_manager = RookManager(
            game=self,
            rows=self.rows,
            cols=self.cols,
            cell_size=self.cell_size,
            margin=self.margin
            # rook_manager toma offsets desde game por defecto
        )

        self.game_over = False
        self.score = 0

        # botón salir
        self.btn_width = 180
        self.btn_height = 36
        self.btn_x = ANCHO - self.btn_width - 12
        self.btn_y = 12
        self.btn_rect = pygame.Rect(self.btn_x, self.btn_y, self.btn_width, self.btn_height)

        # iniciar loop
        self.run_game()

    # ------------------------------------------------------------------
    # 🔹 GUARDAR PUNTAJE
    # ------------------------------------------------------------------
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
                    except:
                        data = []
            else:
                data = []

            data.append(entry)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"[ERROR] No se pudo guardar el puntaje: {e}")

    # ------------------------------------------------------------------
    # 🔹 DIBUJAR GRID
    # ------------------------------------------------------------------
    def dibujar_grid(self):
        self.pantalla.fill(GRIS)

        for row in range(self.rows):
            for col in range(self.cols):
                x = self.left_offset + self.margin + col * (self.cell_size + self.margin)
                y = self.top_offset + self.margin + row * (self.cell_size + self.margin)

                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                pygame.draw.rect(self.pantalla, CELDA, rect)
                pygame.draw.rect(self.pantalla, NEGRO, rect, 2)

    # ------------------------------------------------------------------
    # 🔹 HUD
    # ------------------------------------------------------------------
    def draw_hud(self, fps):
        font = pygame.font.SysFont(None, 26)

        texto = f"Jugador: {self.usuario} ({self.rol})"
        self.pantalla.blit(font.render(texto, True, TXT_COLOR), (10, 12))

        self.pantalla.blit(font.render("Monedas: " + str(self.coin_manager.collected),
                                       True, (255, 215, 0)), (10, 72))

        fps_text = font.render(f"FPS: {int(fps)}", True, TXT_COLOR)
        self.pantalla.blit(fps_text, (ANCHO - 110, 12))

        # botón salir
        mouse_pos = pygame.mouse.get_pos()
        hover = self.btn_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.pantalla, BTN_HOVER if hover else BTN_COLOR, self.btn_rect, border_radius=6)

        btn_font = pygame.font.SysFont(None, 22)
        tx = self.btn_x + (self.btn_width - btn_font.size("Salir al menú")[0]) // 2
        ty = self.btn_y + (self.btn_height - btn_font.size("Salir al menú")[1]) // 2
        self.pantalla.blit(btn_font.render("Salir al menú", True, TXT_COLOR), (tx, ty))

    # ------------------------------------------------------------------
    # 🔹 CONFIRMAR SALIDA
    # ------------------------------------------------------------------
    def mostrar_confirmacion(self):
        ancho, alto = 420, 180
        x = (ANCHO - ancho) // 2
        y = (ALTO - alto) // 2
        rect = pygame.Rect(x, y, ancho, alto)

        fuente = pygame.font.SysFont(None, 28)
        texto = fuente.render("¿Deseas guardar y salir al menú?", True, BLANCO)

        btn_si = pygame.Rect(x + 40, y + 100, 150, 40)
        btn_no = pygame.Rect(x + 230, y + 100, 150, 40)

        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return False
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if btn_si.collidepoint(e.pos):
                        return True  # guardar y salir
                    elif btn_no.collidepoint(e.pos):
                        return False  # seguir jugando

            pygame.draw.rect(self.pantalla, (25, 25, 25), rect, border_radius=12)
            pygame.draw.rect(self.pantalla, BLANCO, rect, 2)

            self.pantalla.blit(texto, (x + 35, y + 35))

            pygame.draw.rect(self.pantalla, VERDE, btn_si, border_radius=10)
            pygame.draw.rect(self.pantalla, ROJO, btn_no, border_radius=10)

            self.pantalla.blit(fuente.render("Guardar y salir", True, BLANCO), (btn_si.x + 10, btn_si.y + 10))
            self.pantalla.blit(fuente.render("Seguir jugando", True, BLANCO), (btn_no.x + 10, btn_no.y + 10))

            pygame.display.flip()
            clock.tick(30)

    # ------------------------------------------------------------------
    # 🔹 LOOP PRINCIPAL
    # ------------------------------------------------------------------
    def run_game(self):
        running = True
        self.placing_rook = False

        self.btn_rook_width = 180
        self.btn_rook_height = 36
        self.btn_rook_x = ANCHO - self.btn_rook_width - 12
        self.btn_rook_y = self.btn_y + self.btn_height + 10
        self.btn_rook_rect = pygame.Rect(self.btn_rook_x, self.btn_rook_y,
                                         self.btn_rook_width, self.btn_rook_height)

        font = pygame.font.SysFont(None, 26)

        while running:
            dt = clock.tick(FPS) / 1000

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    if self.confirmar_salida():
                        running = False

                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    pos = evento.pos

                    if self.btn_rect.collidepoint(pos):
                        if self.confirmar_salida():
                            running = False

                    elif self.btn_rook_rect.collidepoint(pos):
                        self.placing_rook = not self.placing_rook

                    elif self.placing_rook:
                        placed = self.rook_manager.place_rook(pos, self.coin_manager)
                        if placed:
                            self.placing_rook = False
                    else:
                        self.coin_manager.check_collect(pos)

            # actualizar lógica
            self.coin_manager.update()
            self.enemy_manager.update(dt, self.rook_manager)
            self.rook_manager.update(dt, self.enemy_manager.enemies)

            # victoria
            if self.enemy_manager.finished:
                tiempo_total = time.time() - self.start_time
                HallOfFameWindow.registrar_tiempo(self.usuario, tiempo_total)
                mostrar_victoria(self.pantalla, self.usuario, clock)
                running = False

            # dibujar
            self.dibujar_grid()
            self.coin_manager.draw(self.pantalla)
            self.enemy_manager.draw(self.pantalla)
            self.rook_manager.draw(self.pantalla, self.enemy_manager.enemies,
                                   self.enemy_manager.enemy_img)

            self.draw_hud(clock.get_fps())

            # botón torres
            hover = self.btn_rook_rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(self.pantalla, BTN_HOVER if hover else BTN_COLOR,
                             self.btn_rook_rect, border_radius=6)
            self.pantalla.blit(pygame.font.SysFont(None, 22).render(
                "Colocar torre", True, TXT_COLOR
            ), (self.btn_rook_x + 20, self.btn_rook_y + 7))

            # mensaje modo torre
            if self.placing_rook:
                txt = font.render("Modo colocar torre activo", True, (255, 255, 0))
                self.pantalla.blit(txt, (10, 100))
                # --- Mostrar enemigos restantes ---
                enemies_left = self.enemy_manager.remaining_enemies()
                txt_enemigos = font.render(f"Enemigos restantes: {enemies_left}", True, (255, 255, 255))
                self.pantalla.blit(txt_enemigos, (10, 130))

            pygame.display.flip()

        self.cleanup_and_return()

    def confirmar_salida(self):
        confirmar = self.mostrar_confirmacion()
        if confirmar:
            self.guardar_puntaje()
            return True
        return False

    def cleanup_and_return(self):
        try:
            pygame.display.quit()
        except:
            pass

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except:
            pass

        from gui.menu_principal import MainMenu
        MainMenu(self.usuario, self.rol)
