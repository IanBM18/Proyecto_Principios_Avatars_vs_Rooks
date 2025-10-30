# juego/main_game.py
import pygame
import os
import json

pygame.init()

# Configuración
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


class GameWindow:
    def __init__(self, jugador, rol):
        self.jugador = jugador
        self.rol = rol
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Avatars VS Rooks - Partida")

        self.run_game()

    def dibujar_grid(self):
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
        font = pygame.font.SysFont(None, 28)
        text = font.render(f"Jugador: {self.jugador} ({self.rol}) — Matriz 9x5 [ESC para salir]", True, BLANCO)
        self.pantalla.blit(text, (10, 10))
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

            self.dibujar_grid()
            self.draw_hud(clock.get_fps())
            pygame.display.flip()

        pygame.quit()

        # 🔹 Importamos aquí para evitar el ciclo
        from gui.menu_principal import MainMenu
        MainMenu(self.jugador, self.rol)
