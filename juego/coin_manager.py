# juego/coin_manager.py
import random
import pygame
import time

class CoinManager:
    def __init__(self, rows, cols, cell_size, margin, grid_width, screen_width, max_coins=5):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.margin = margin
        self.max_coins = max_coins
        self.active_coins = []  # [(col, row, tipo), ...]
        self.collected = 0

        # Calcular offset para centrar en pantalla
        self.left_offset = (screen_width - grid_width) // 2
        self.y_offset = 100  # igual que tu dibujar_grid()

        # Temporizador para spawn
        self.last_spawn_time = time.time()
        self.spawn_delay = 5.0  # 5 segundos fijos (feedback)

        # Cargar imágenes de monedas (fallbacks si faltan)
        def load_safe(path, size):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, size)
            except Exception:
                surf = pygame.Surface(size, pygame.SRCALPHA)
                pygame.draw.circle(surf, (255, 215, 0), (size[0]//2, size[1]//2), min(size)//2)
                return surf

        self.coins_tipo = [
            {"imagen": load_safe("assets/sprites/coin_25.png", (cell_size - 10, cell_size - 10)), "valor": 25},
            {"imagen": load_safe("assets/sprites/coin_50.png", (cell_size - 10, cell_size - 10)), "valor": 50},
            {"imagen": load_safe("assets/sprites/coin_100.png", (cell_size - 10, cell_size - 10)), "valor": 100},
        ]

    def spawn_coin(self):
        """Genera UNA moneda aleatoria en una posición libre dentro de la grilla."""
        ocupadas = [(c[0], c[1]) for c in self.active_coins]
        posibles = [(x, y) for x in range(self.cols) for y in range(self.rows) if (x, y) not in ocupadas]
        if posibles:
            col, row = random.choice(posibles)
            tipo = random.choice(self.coins_tipo)  # elige tipo aleatorio
            self.active_coins.append((col, row, tipo))

    def update(self):
        """Controla el spawn cada spawn_delay segundos."""
        now = time.time()
        if len(self.active_coins) < self.max_coins and now - self.last_spawn_time >= self.spawn_delay:
            self.spawn_coin()
            self.last_spawn_time = now

    def draw(self, surface):
        """Dibuja las monedas activas centradas correctamente."""
        for (col, row, tipo) in self.active_coins:
            x = self.left_offset + self.margin + col * (self.cell_size + self.margin)
            y = self.y_offset + self.margin + row * (self.cell_size + self.margin)
            surface.blit(tipo["imagen"], (x + 5, y + 5))

    def check_collect(self, mouse_pos):
        """Verifica si se hace clic sobre una moneda y la recoge."""
        mx, my = mouse_pos
        for coin in self.active_coins[:]:
            cx = self.left_offset + self.margin + coin[0] * (self.cell_size + self.margin)
            cy = self.y_offset + self.margin + coin[1] * (self.cell_size + self.margin)
            rect = pygame.Rect(cx, cy, self.cell_size, self.cell_size)
            if rect.collidepoint(mx, my):
                self.active_coins.remove(coin)
                self.collected += coin[2]["valor"]  # suma el valor correcto
                print(f"💰 Moneda recogida! Valor: {coin[2]['valor']} Total: {self.collected}")
                break