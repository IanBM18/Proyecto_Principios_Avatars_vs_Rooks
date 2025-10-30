# juego/main_game.py
import pygame
import sys
import subprocess
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
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Avatars VS Rooks - Partida")

NEGRO = (0, 0, 0)
GRIS = (40, 40, 40)
BLANCO = (255, 255, 255)
CELDA = (70, 130, 180)

clock = pygame.time.Clock()
FPS = 30

def dibujar_grid(screen):
    screen.fill(GRIS)
    y_offset = 80
    for row in range(ROWS):
        for col in range(COLUMNS):
            x = MARGIN + col * (CELL_SIZE + MARGIN)
            y = y_offset + MARGIN + row * (CELL_SIZE + MARGIN)
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, CELDA, rect)
            pygame.draw.rect(screen, NEGRO, rect, 2)

def draw_hud(screen, fps, jugador, rol):
    font = pygame.font.SysFont(None, 28)
    text = font.render(f"Jugador: {jugador} ({rol})  —  Matriz 9x5  [Esc para salir]", True, BLANCO)
    screen.blit(text, (10, 10))
    fps_text = font.render(f"FPS: {int(fps)}", True, BLANCO)
    screen.blit(fps_text, (ANCHO - 100, 10))

def cargar_sesion():
    ruta_sesion = os.path.join(os.path.dirname(__file__), "..", "data", "sesion_actual.json")
    if os.path.exists(ruta_sesion):
        try:
            with open(ruta_sesion, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"usuario": "Invitado", "rol": "player"}
    return {"usuario": "Invitado", "rol": "player"}

def run_game():
    sesion = cargar_sesion()
    jugador = sesion.get("usuario", "Invitado")
    rol = sesion.get("rol", "player")

    running = True
    while running:
        dt = clock.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                running = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    running = False

        dibujar_grid(pantalla)
        draw_hud(pantalla, clock.get_fps(), jugador, rol)
        pygame.display.flip()

    pygame.quit()

    # Volver al menú principal con los datos del jugador
    ruta_menu = os.path.join(os.path.dirname(__file__), "..", "gui", "menu_principal.py")
    python_exe = sys.executable
    try:
        subprocess.run([python_exe, ruta_menu])
    except Exception as e:
        print("No se pudo lanzar el menú principal:", e)
        sys.exit()

if __name__ == "__main__":
    run_game()
