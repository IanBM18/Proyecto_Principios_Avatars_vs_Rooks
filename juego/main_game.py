import pygame
import os
import json
from juego.coin_manager import CoinManager  # 👈 Importamos la clase de monedas
from juego.enemy_manager import EnemyManager 

pygame.init()

# -------------------------------
# 🔹 CONFIGURACIÓN DEL TABLERO
# -------------------------------
COLUMNS = 9
ROWS = 5
CELL_SIZE = 64
MARGIN = 2

ANCHO = COLUMNS * (CELL_SIZE + MARGIN) + MARGIN
ALTO = ROWS * (CELL_SIZE + MARGIN) + 120

NEGRO = (0, 0, 0)
GRIS = (40, 40, 40)
BLANCO = (255, 255, 255)
CELDA = (70, 130, 180)

clock = pygame.time.Clock()
FPS = 30


# -------------------------------
# 🔹 CLASE PRINCIPAL DEL JUEGO
# -------------------------------
class GameWindow:
    def __init__(self, jugador, rol):
        self.jugador = jugador
        self.rol = rol

        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Avatars VS Rooks - Partida")

        # 🪙 Inicializar el manejador de monedas
        self.coin_manager = CoinManager(ROWS, COLUMNS, CELL_SIZE, MARGIN)
        # ❌ Ya no se llama spawn_coins() directamente: el CoinManager maneja su propio cooldown
        self.enemy_manager = EnemyManager(ROWS, COLUMNS, CELL_SIZE, MARGIN)

        self.run_game()

    def dibujar_grid(self):
        """Dibuja la cuadrícula del campo de juego."""
        self.pantalla.fill(GRIS)
        y_offset = 80
        for row in range(ROWS):
            for col in range(COLUMNS):
                x = MARGIN + col * (CELL_SIZE + MARGIN)
                y = y_offset + MARGIN + row * (CELL_SIZE + MARGIN)
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.pantalla, CELDA, rect)
                pygame.draw.rect(self.pantalla, NEGRO, rect, 2)

    def draw_hud(self, fps):
        """Dibuja la barra superior con info del jugador y monedas."""
        font = pygame.font.SysFont(None, 28)

        # Texto jugador
        text = font.render(f"Jugador: {self.jugador} ({self.rol}) — [ESC para salir]", True, BLANCO)
        self.pantalla.blit(text, (10, 10))

        # 💰 Contador de monedas
        coins_text = font.render(f"Monedas: {self.coin_manager.collected}", True, (255, 215, 0))
        self.pantalla.blit(coins_text, (10, 40))

        # FPS
        fps_text = font.render(f"FPS: {int(fps)}", True, BLANCO)
        self.pantalla.blit(fps_text, (ANCHO - 100, 10))

    def run_game(self):
        running = True
        while running:
            dt = clock.tick(FPS)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    running = False
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    running = False
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    self.coin_manager.check_collect(evento.pos)

        # Actualizar lógica
            self.coin_manager.update()
            self.enemy_manager.update()

        # Dibujar
            self.dibujar_grid()
            self.coin_manager.draw(self.pantalla)
            self.enemy_manager.draw(self.pantalla)
            self.draw_hud(clock.get_fps())
            pygame.display.flip()

        pygame.quit()

        from gui.menu_principal import MainMenu
        MainMenu(self.jugador, self.rol)
