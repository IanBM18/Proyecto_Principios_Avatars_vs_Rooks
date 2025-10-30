# juego/main_game.py
import pygame
import sys
import os
import json
from gui.menu_principal import MainMenu

class GameWindow:
    def __init__(self, usuario, rol):
        pygame.init()

        # Configuración
        self.COLUMNS = 9
        self.ROWS = 5
        self.CELL_SIZE = 64
        self.MARGIN = 2

        self.ANCHO = self.COLUMNS * (self.CELL_SIZE + self.MARGIN) + self.MARGIN
        self.ALTO = self.ROWS * (self.CELL_SIZE + self.MARGIN) + 120
        self.screen = pygame.display.set_mode((self.ANCHO, self.ALTO))
        pygame.display.set_caption("Avatars VS Rooks - Partida")

        # Colores
        self.NEGRO = (0, 0, 0)
        self.GRIS = (40, 40, 40)
        self.BLANCO = (255, 255, 255)
        self.CELDA = (70, 130, 180)

        # Datos del jugador
        self.usuario = usuario
        self.rol = rol

        self.clock = pygame.time.Clock()
        self.FPS = 30

        self.run_game()

    def dibujar_grid(self):
        self.screen.fill(self.GRIS)
        y_offset = 80
        for row in range(self.ROWS):
            for col in range(self.COLUMNS):
                x = self.MARGIN + col * (self.CELL_SIZE + self.MARGIN)
                y = y_offset + self.MARGIN + row * (self.CELL_SIZE + self.MARGIN)
                rect = pygame.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE)
                pygame.draw.rect(self.screen, self.CELDA, rect)
                pygame.draw.rect(self.screen, self.NEGRO, rect, 2)

    def draw_hud(self, fps):
        font = pygame.font.SysFont(None, 28)
        text = font.render(f"Jugador: {self.usuario} ({self.rol}) — Matriz 9x5 [ESC para salir]", True, self.BLANCO)
        self.screen.blit(text, (10, 10))
        fps_text = font.render(f"FPS: {int(fps)}", True, self.BLANCO)
        self.screen.blit(fps_text, (self.ANCHO - 100, 10))

    def run_game(self):
        running = True
        while running:
            dt = self.clock.tick(self.FPS)
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    running = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        running = False

            self.dibujar_grid()
            self.draw_hud(self.clock.get_fps())
            pygame.display.flip()

        pygame.quit()

        # ✅ Volver al menú principal sin cerrar el programa
        MainMenu(self.usuario, self.rol)

def cargar_sesion():
    ruta_sesion = os.path.join(os.path.dirname(__file__), "..", "data", "sesion_actual.json")
    if os.path.exists(ruta_sesion):
        try:
            with open(ruta_sesion, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"usuario": "Invitado", "rol": "player"}
    return {"usuario": "Invitado", "rol": "player"}

if __name__ == "__main__":
    sesion = cargar_sesion()
    GameWindow(sesion.get("usuario", "Invitado"), sesion.get("rol", "player"))
