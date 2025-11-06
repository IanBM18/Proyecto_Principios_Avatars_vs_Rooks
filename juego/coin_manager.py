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
        self.active_coins = []  # [(x, y, tipo), ...]
        self.collected = 0

        # Calcular offset para centrar en pantalla
        self.left_offset = (screen_width - grid_width) // 2
        self.y_offset = 100  # igual que tu dibujar_grid()

        # Temporizador para spawn
        self.last_spawn_time = time.time()
        self.spawn_delay = 5  # 5 segundos fijos

        # Cargar imágenes de monedas
        self.coins_tipo = [
            {"imagen": pygame.image.load("assets/sprites/coin_25.png"), "valor": 25},
            {"imagen": pygame.image.load("assets/sprites/coin_50.png"), "valor": 50},
            {"imagen": pygame.image.load("assets/sprites/coin_100.png"), "valor": 100},
        ]
        # Escalar todas al tamaño de celda
        for coin in self.coins_tipo:
            coin["imagen"] = pygame.transform.scale(coin["imagen"], (cell_size - 10, cell_size - 10))

    def spawn_coin(self):
        """Genera UNA moneda aleatoria en una posición libre dentro de la grilla."""
        posibles = [(x, y) for x in range(self.cols) for y in range(self.rows)
                    if (x, y) not in [(c[0], c[1]) for c in self.active_coins]]
        if posibles:
            x, y = random.choice(posibles)
            tipo = random.choice(self.coins_tipo)  # elige tipo aleatorio
            self.active_coins.append((x, y, tipo))

    def update(self):
        """Controla el spawn cada 5 segundos."""
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