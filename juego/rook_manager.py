# juego/rook_manager.py
import pygame
import time

class RookManager:
    def __init__(self, rows, cols, cell_size, margin, screen_width):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.margin = margin
        self.screen_width = screen_width
        self.rooks = []  # [{'col': int, 'row': int, 'hp': int, 'last_attack': float}]
        self.invalid_pos = None
        self.shots = []  # para dibujar ataques

        image_path = "assets/sprites/torreMagica.png"
        self.rook_img = pygame.image.load(image_path).convert_alpha()
        self.rook_img = pygame.transform.scale(self.rook_img, (cell_size - 10, cell_size - 10))

    def place_rook(self, pos, coin_manager):
        mouse_x, mouse_y = pos
        y_offset = 100
        left_offset = (self.screen_width - (self.cols * (self.cell_size + self.margin) + self.margin)) // 2

        # 💰 Verificar monedas
        if coin_manager.collected < 50:
            print("❌ No tienes suficientes monedas para colocar la torre")
            return False

        for row in range(self.rows):
            for col in range(self.cols):
                cell_x = left_offset + self.margin + col * (self.cell_size + self.margin)
                cell_y = y_offset + self.margin + row * (self.cell_size + self.margin)
                rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)

                if rect.collidepoint(mouse_x, mouse_y):
                    # ✅ Colocar torre si la celda está libre
                    if not any(r['col'] == col and r['row'] == row for r in self.rooks):
                        self.rooks.append({
                            'col': col,
                            'row': row,
                            'hp': 3,
                            'last_attack': 0
                        })
                        coin_manager.collected -= 50
                        self.invalid_pos = None
                        print(f"🧱 Torre colocada en ({col}, {row})")
                        return True
                    else:
                        self.invalid_pos = (col, row)
                        print("⚠️ Ya hay una torre aquí.")
                        return False
        return False

    def update(self, dt, enemies):
        """Hace que las torres ataquen automáticamente a los enemigos."""
        attack_interval = 4  # segundos
        damage = 2

        for rook in self.rooks[:]:
            now = time.time()
            if now - rook['last_attack'] >= attack_interval:
                rook['last_attack'] = now

                # Buscar el enemigo más cercano en la misma columna
                target = None
                for enemy in enemies:
                    if enemy['col'] == rook['col']:
                        target = enemy
                        break

                # 💥 Atacar
                if target:
                    target['hp'] -= damage
                    print(f"💥 Torre ({rook['col']},{rook['row']}) golpea enemigo en ({target['col']},{target['row']}) - HP enemigo: {target['hp']}")
                    if target['hp'] <= 0:
                        enemies.remove(target)
                        print("☠️ Enemigo destruido")

                    # Registrar disparo para efecto visual
                    self.shots.append({
                        'start': (rook['col'], rook['row']),
                        'end': (target['col'], target['row']),
                        'time': now
                    })

            # 🩸 Eliminar torre si su HP llega a 0 (cuando implementemos ataques enemigos)
            if rook['hp'] <= 0:
                self.rooks.remove(rook)

        # Limpiar disparos viejos (>0.2s)
        self.shots = [s for s in self.shots if any(e['col'] == s['end'][0] and e['row'] == s['end'][1] for e in enemies) and time.time() - s['time'] < 0.2]

    def draw(self, surface, enemies, enemy_img):
        """Dibuja todas las torres, HP y disparos."""
        y_offset = 100
        left_offset = (self.screen_width - (self.cols * (self.cell_size + self.margin) + self.margin)) // 2

        # 🔹 Dibujar torres y HP
        for rook in self.rooks:
            col, row = rook['col'], rook['row']
            cell_x = left_offset + self.margin + col * (self.cell_size + self.margin)
            cell_y = y_offset + self.margin + row * (self.cell_size + self.margin)

            center_x = cell_x + (self.cell_size - self.rook_img.get_width()) // 2
            center_y = cell_y + (self.cell_size - self.rook_img.get_height()) // 2

            surface.blit(self.rook_img, (center_x, center_y))

            # 🟢 Mostrar HP de la torre
            font = pygame.font.SysFont(None, 20)
            hp_text = font.render(f"HP:{rook['hp']}", True, (0, 255, 0))
            surface.blit(hp_text, (center_x, center_y - 12))

        # 🔹 Dibujar disparos estilo “rayo/flecha”
        for s in self.shots:
            # torre inicial
            start_pos = (
                left_offset + s['start'][0] * (self.cell_size + self.margin) + self.cell_size // 2,
                y_offset + s['start'][1] * (self.cell_size + self.margin) + self.cell_size // 2
            )

            # enemigo final
            enemy = next((e for e in enemies if e['col'] == s['end'][0] and e['row'] == s['end'][1]), None)
            if not enemy:
                continue  # enemigo ya muerto

            end_pos = (
                enemy['x'] + enemy_img.get_width() // 2,
                enemy['y'] + enemy_img.get_height() // 2
            )

            pygame.draw.line(surface, (0, 255, 255), start_pos, end_pos, 3)

        # 🔴 Casilla inválida
        if self.invalid_pos:
            col, row = self.invalid_pos
            cell_x = left_offset + self.margin + col * (self.cell_size + self.margin)
            cell_y = y_offset + self.margin + row * (self.cell_size + self.margin)
            pygame.draw.rect(surface, (255, 0, 0), 
                             (cell_x, cell_y, self.cell_size, self.cell_size), 4)