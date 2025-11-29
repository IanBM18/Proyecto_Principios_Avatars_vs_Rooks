# juego/rook_manager.py
import pygame
import time

class RookManager:
    def __init__(self, game, rows, cols, cell_size, margin, left_offset=None, top_offset=None):
        self.game = game
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.margin = margin

        # offsets (usar los proporcionados o los del game)
        self.left_offset = left_offset if left_offset is not None else getattr(game, "left_offset", 0)
        self.top_offset = top_offset if top_offset is not None else getattr(game, "top_offset", 100)

        # Lista de torres
        self.rooks = []  # {'col','row','hp','last_attack'}
        self.invalid_pos = None
        self.shots = []  # efectos de disparo

        # Cargar sprite de torre (mantén la ruta que tengas en assets)
        image_path = "assets/sprites/torreMagica.png"
        try:
            self.rook_img = pygame.image.load(image_path).convert_alpha()
        except Exception:
            # fallback si no existe
            self.rook_img = pygame.Surface((self.cell_size - 10, self.cell_size - 10), pygame.SRCALPHA)
            pygame.draw.rect(self.rook_img, (150, 100, 200), self.rook_img.get_rect())

        self.rook_img = pygame.transform.scale(self.rook_img, (cell_size - 10, cell_size - 10))

    def place_rook(self, pos, coin_manager):
        mouse_x, mouse_y = pos

        left_offset = self.left_offset
        y_offset = self.top_offset

        # Verificar monedas
        if coin_manager.collected < 50:
            print("❌ No tienes suficientes monedas para colocar la torre")
            return False

        for row in range(self.rows):
            for col in range(self.cols):
                cell_x = left_offset + self.margin + col * (self.cell_size + self.margin)
                cell_y = y_offset + self.margin + row * (self.cell_size + self.margin)
                rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)

                if rect.collidepoint(mouse_x, mouse_y):
                    # Colocar torre si la celda está libre
                    if not any(r['col'] == col and r['row'] == row for r in self.rooks):
                        self.rooks.append({
                            'col': col,
                            'row': row,
                            'hp': 3,
                            'last_attack': 0
                        })
                        coin_manager.collected -= 50
                        self.invalid_pos = None
                        print(f"🧱 Torre colocada en ({col}, {row}) - cell topleft=({cell_x},{cell_y}), mouse=({mouse_x},{mouse_y})")
                        return True
                    else:
                        self.invalid_pos = (col, row)
                        print("⚠️ Ya hay una torre aquí.")
                        return False
        return False

    def update(self, dt, enemies):
        attack_interval = 4.0  # debe atacar cada 4 segundos
        damage = 2

        for rook in self.rooks[:]:
            now = time.time()

            if now - rook['last_attack'] >= attack_interval:
                rook['last_attack'] = now

                # Buscar enemigos ABAJO de la torre
                target = None
                highest_row = 9999  # buscamos el más cercano hacia abajo (fila más alta)

                for enemy in enemies:
                    if enemy['col'] == rook['col'] and enemy['row'] > rook['row']:
                        # enemigo está debajo → candidato
                        if enemy['row'] < highest_row:
                            highest_row = enemy['row']
                            target = enemy

                # Si hay objetivo → atacar
                if target:
                    target['hp'] -= damage

                    # registrar disparo visual
                    self.shots.append({
                        'start': (rook['col'], rook['row']),
                        'end': (target['col'], target['row']),
                        'time': now
                    })

            # eliminar torre si hp <= 0
            if rook.get('hp', 0) <= 0:
                try:
                    self.rooks.remove(rook)
                except ValueError:
                    pass

        # limpiar disparos viejos (>0.25s)
        now = time.time()
        self.shots = [s for s in self.shots if now - s['time'] < 0.25]

    def draw(self, surface, enemies, enemy_img):
        y_offset = self.top_offset
        left_offset = self.left_offset

        # Dibujar torres y HP
        for rook in self.rooks:
            col, row = rook['col'], rook['row']
            cell_x = left_offset + self.margin + col * (self.cell_size + self.margin)
            cell_y = y_offset + self.margin + row * (self.cell_size + self.margin)

            center_x = cell_x + (self.cell_size - self.rook_img.get_width()) // 2
            center_y = cell_y + (self.cell_size - self.rook_img.get_height()) // 2

            surface.blit(self.rook_img, (center_x, center_y))

            # Mostrar HP de la torre
            font = pygame.font.SysFont(None, 20)
            hp_text = font.render(f"HP:{rook['hp']}", True, (0, 255, 0))
            surface.blit(hp_text, (center_x, center_y - 12))

        # Dibujar disparos estilo “rayo/flecha”
        for s in self.shots:
            start_pos = (
                left_offset + s['start'][0] * (self.cell_size + self.margin) + self.cell_size // 2,
                y_offset + s['start'][1] * (self.cell_size + self.margin) + self.cell_size // 2
            )

            enemy = next((e for e in enemies if e['col'] == s['end'][0] and e['row'] == s['end'][1]), None)
            if not enemy:
                continue

            end_pos = (
                enemy['x'] + enemy_img.get_width() // 2,
                enemy['y'] + enemy_img.get_height() // 2
            )

            pygame.draw.line(surface, (0, 255, 255), start_pos, end_pos, 3)

        # Casilla inválida
        if self.invalid_pos:
            col, row = self.invalid_pos
            cell_x = left_offset + self.margin + col * (self.cell_size + self.margin)
            cell_y = y_offset + self.margin + row * (self.cell_size + self.margin)
            pygame.draw.rect(surface, (255, 0, 0), (cell_x, cell_y, self.cell_size, self.cell_size), 4)
