import pygame
print(pygame.ver)
import sys
import math
import random
from pygame.locals import *

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galactic Star Collector")

# Colors
BACKGROUND = (10, 10, 30)
STAR_COLOR = (255, 255, 200)
PLAYER_COLOR = (70, 130, 255)
ENEMY_COLOR = (220, 60, 60)
BULLET_COLOR = (0, 255, 150)
EXPLOSION_COLORS = [(255, 200, 0), (255, 100, 0), (255, 50, 0)]
PLANET_COLORS = [
    (255, 200, 100),  # Yellow
    (150, 200, 255),  # Blue
    (255, 150, 100),  # Orange
    (200, 255, 150),  # Green
    (255, 100, 150),  # Pink
    (200, 150, 255),  # Purple
    (100, 255, 200),  # Teal
    (255, 200, 200),  # Light red
    (200, 255, 255),  # Light blue
    (255, 255, 150)   # Light yellow
]
TEXT_COLOR = (220, 220, 255)
BUTTON_COLOR = (70, 130, 200)
BUTTON_HOVER_COLOR = (100, 160, 230)

# Game constants
FPS = 60
PLAYER_SPEED = 8
STAR_SPEED = 0.3
ENEMY_SPEED_MIN = 3
ENEMY_SPEED_MAX = 6
LEVEL_CHANGE_DELAY = 120  # frames
PLAYER_BULLET_SPEED = 12
BULLET_COOLDOWN = 15  # frames between shots

# Fonts
title_font = pygame.font.SysFont("arial", 64, bold=True)
font_large = pygame.font.SysFont("arial", 36)
font_medium = pygame.font.SysFont("arial", 28)
font_small = pygame.font.SysFont("arial", 22)

class Player:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.width = 60
        self.height = 40
        self.speed = PLAYER_SPEED
        self.score = 0
        self.collected_stars = 0
        self.missed_stars = 0
        self.bullets = []
        self.shoot_cooldown = 0
        
    def draw(self, surface):
        # Draw the spaceship
        points = [
            (self.x, self.y - self.height//2),  # Top
            (self.x - self.width//2, self.y + self.height//2),  # Bottom left
            (self.x + self.width//2, self.y + self.height//2)   # Bottom right
        ]
        pygame.draw.polygon(surface, PLAYER_COLOR, points)
        
        # Draw cockpit
        pygame.draw.circle(surface, (180, 230, 255), (self.x, self.y - 5), 10)
        
        # Draw engines
        pygame.draw.rect(surface, (200, 200, 100), (self.x-15, self.y+15, 10, 15))
        pygame.draw.rect(surface, (200, 200, 100), (self.x+5, self.y+15, 10, 15))
        
        # Draw engine flames
        flame_length = random.randint(5, 15)
        pygame.draw.polygon(surface, (255, 150, 0), [
            (self.x-10, self.y+30),
            (self.x-15, self.y+30+flame_length),
            (self.x-5, self.y+30)
        ])
        pygame.draw.polygon(surface, (255, 150, 0), [
            (self.x+10, self.y+30),
            (self.x+15, self.y+30+flame_length),
            (self.x+5, self.y+30)
        ])
        
        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(surface, BULLET_COLOR, (bullet[0], bullet[1]), 4)
        
    def move(self, direction):
        if direction == "left" and self.x - self.width//2 > 0:
            self.x -= self.speed
        if direction == "right" and self.x + self.width//2 < WIDTH:
            self.x += self.speed
        # Add vertical movement
        if direction == "up" and self.y - self.height//2 > 0:
            self.y -= self.speed
        if direction == "down" and self.y + self.height//2 < HEIGHT:
            self.y += self.speed
            
    def shoot(self):
        if self.shoot_cooldown <= 0:
            self.bullets.append([self.x, self.y - self.height//2])
            self.shoot_cooldown = BULLET_COOLDOWN
            
    def update(self):
        # Update bullets
        for bullet in self.bullets[:]:
            bullet[1] -= PLAYER_BULLET_SPEED
            if bullet[1] < 0:
                self.bullets.remove(bullet)
                
        # Update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

class Star:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.x = random.randint(30, WIDTH - 30)
        self.y = random.randint(-100, -20)
        self.speed = STAR_SPEED + random.random() * 0.1  # Reduced variation
        self.size = random.randint(8, 15)
        self.collected = False
        self.glow_timer = 0
        
    def update(self):
        self.y += self.speed
        self.glow_timer = (self.glow_timer + 1) % 60
        
    def draw(self, surface):
        if not self.collected:
            # Draw glow effect
            glow_size = self.size * (1.5 + 0.5 * math.sin(self.glow_timer * 0.1))
            glow_surface = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 255, 200, 100), (glow_size, glow_size), glow_size)
            surface.blit(glow_surface, (self.x - glow_size, self.y - glow_size))
            
            # Draw the star
            pygame.draw.circle(surface, STAR_COLOR, (self.x, self.y), self.size)
            
    def is_off_screen(self):
        return self.y > HEIGHT + 20

class Enemy:
    def __init__(self, speed_factor):
        self.reset(speed_factor)
        
    def reset(self, speed_factor):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(-200, -50)
        base_speed = ENEMY_SPEED_MIN + (ENEMY_SPEED_MAX - ENEMY_SPEED_MIN) * 0.5
        self.speed = base_speed * speed_factor
        self.width = 50
        self.height = 30
        self.shoot_timer = random.randint(60, 120)
        self.bullets = []
        self.hit_timer = 0
        self.alive = True
        
    def update(self):
        if not self.alive:
            return
            
        self.y += self.speed
        self.shoot_timer -= 1
        
        # Update hit timer
        if self.hit_timer > 0:
            self.hit_timer -= 1
            
        # Update bullets
        for bullet in self.bullets[:]:
            bullet[1] += 7  # Bullet speed
            if bullet[1] > HEIGHT:
                self.bullets.remove(bullet)
                
    def draw(self, surface):
        if not self.alive:
            return
            
        # Draw enemy ship
        color = ENEMY_COLOR
        if self.hit_timer > 0:
            # Flash when hit
            color = (255, 100, 100) if self.hit_timer % 4 < 2 else ENEMY_COLOR
            
        pygame.draw.polygon(surface, color, [
            (self.x, self.y + self.height//2),  # Bottom
            (self.x - self.width//2, self.y - self.height//2),  # Top left
            (self.x + self.width//2, self.y - self.height//2)   # Top right
        ])
        
        # Draw cockpit
        pygame.draw.circle(surface, (255, 150, 150), (self.x, self.y), 8)
        
        # Draw wings
        pygame.draw.polygon(surface, (180, 50, 50), [
            (self.x - self.width//2, self.y),
            (self.x - self.width//2 - 15, self.y + 15),
            (self.x - self.width//2, self.y + 10)
        ])
        pygame.draw.polygon(surface, (180, 50, 50), [
            (self.x + self.width//2, self.y),
            (self.x + self.width//2 + 15, self.y + 15),
            (self.x + self.width//2, self.y + 10)
        ])
        
        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(surface, (255, 100, 100), (bullet[0], bullet[1]), 4)
            
    def shoot(self):
        if self.shoot_timer <= 0:
            self.bullets.append([self.x, self.y + self.height//2])
            self.shoot_timer = random.randint(60, 120)
            
    def is_off_screen(self):
        return self.y > HEIGHT + 50
        
    def hit(self):
        self.hit_timer = 5
        return True

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles = []
        self.lifetime = 30
        self.create_particles()
        
    def create_particles(self):
        # Create explosion particles
        for _ in range(30):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 5)
            size = random.randint(2, 8)
            lifetime = random.randint(20, 40)
            self.particles.append({
                'x': self.x,
                'y': self.y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': size,
                'lifetime': lifetime,
                'color': random.choice(EXPLOSION_COLORS)
            })
            
    def update(self):
        self.lifetime -= 1
        for p in self.particles:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['lifetime'] -= 1
            p['dy'] += 0.1  # Gravity effect
            
    def draw(self, surface):
        for p in self.particles:
            if p['lifetime'] > 0:
                alpha = min(255, p['lifetime'] * 8)
                color = p['color']
                pygame.draw.circle(surface, color, (int(p['x']), int(p['y'])), p['size'])
                
    def is_finished(self):
        return self.lifetime <= 0

class Planet:
    def __init__(self, level):
        self.level = level
        self.size = 80 + level * 10
        self.x = random.randint(self.size, WIDTH - self.size)
        self.y = random.randint(self.size, HEIGHT - self.size)
        self.color = PLANET_COLORS[level % len(PLANET_COLORS)]
        self.rotation = 0
        self.ring = level % 3 == 0  # Some planets have rings
        
    def update(self):
        self.rotation = (self.rotation + 0.002) % (2 * math.pi)
        
    def draw(self, surface):
        # Draw planet
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.size)
        
        # Draw planet details
        for i in range(5):
            detail_size = self.size * (0.2 + 0.1 * i)
            detail_x = self.x + math.sin(self.rotation + i) * (self.size * 0.7)
            detail_y = self.y + math.cos(self.rotation + i) * (self.size * 0.7)
            # FIXED: Add max(0, ...) to prevent negative color values
            pygame.draw.circle(surface, 
                              (max(0, min(255, self.color[0] - 30*i)), 
                               max(0, min(255, self.color[1] - 30*i)), 
                               max(0, min(255, self.color[2] - 30*i))), 
                              (detail_x, detail_y), detail_size)
        
        # Draw ring for some planets
        if self.ring:
            ring_width = 10
            ring_rect = pygame.Rect(self.x - self.size - ring_width, self.y - ring_width//2, 
                                   self.size * 2 + ring_width * 2, ring_width)
            pygame.draw.ellipse(surface, (200, 200, 220), ring_rect, 3)

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.hovered = False
        
    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, (200, 230, 255), self.rect, 3, border_radius=12)
        
        text_surf = font_medium.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class Game:
    def __init__(self):
        self.player = Player()
        self.stars = []
        self.enemies = []
        self.planets = []
        self.explosions = []
        self.level = 1
        self.state = "menu"  # menu, playing, level_complete, game_over
        self.level_change_timer = 0
        self.stars_to_generate = 0
        self.stars_generated = 0
        
        # Level configurations
        self.level_configs = [
            # Level 1: Tutorial
            {"stars_required": 8, "enemy_count": 2, "enemy_speed_factor": 0.3, 
             "star_group_size": (1, 1), "spawn_chance": 0.02, "planet_count": 1},
            
            # Level 2: Basic Challenge
            {"stars_required": 10, "enemy_count": 3, "enemy_speed_factor": 0.4, 
             "star_group_size": (1, 2), "spawn_chance": 0.018, "planet_count": 1},
            
            # Level 3: Increasing Pace
            {"stars_required": 12, "enemy_count": 4, "enemy_speed_factor": 0.5, 
             "star_group_size": (1, 2), "spawn_chance": 0.016, "planet_count": 2},
            
            # Level 4: More Enemies
            {"stars_required": 14, "enemy_count": 5, "enemy_speed_factor": 0.6, 
             "star_group_size": (1, 3), "spawn_chance": 0.015, "planet_count": 2},
            
            # Level 5: Midway Challenge
            {"stars_required": 16, "enemy_count": 6, "enemy_speed_factor": 0.7, 
             "star_group_size": (2, 3), "spawn_chance": 0.014, "planet_count": 3},
            
            # Level 6: Faster Enemies
            {"stars_required": 18, "enemy_count": 7, "enemy_speed_factor": 0.8, 
             "star_group_size": (2, 3), "spawn_chance": 0.013, "planet_count": 3},
            
            # Level 7: Precision Required
            {"stars_required": 20, "enemy_count": 8, "enemy_speed_factor": 0.9, 
             "star_group_size": (2, 4), "spawn_chance": 0.012, "planet_count": 4},
            
            # Level 8: Expert Level
            {"stars_required": 22, "enemy_count": 9, "enemy_speed_factor": 1.0, 
             "star_group_size": (3, 4), "spawn_chance": 0.011, "planet_count": 4},
            
            # Level 9: Almost There
            {"stars_required": 24, "enemy_count": 10, "enemy_speed_factor": 1.1, 
             "star_group_size": (3, 5), "spawn_chance": 0.01, "planet_count": 5},
            
            # Level 10: Final Challenge
            {"stars_required": 26, "enemy_count": 12, "enemy_speed_factor": 1.2, 
             "star_group_size": (4, 5), "spawn_chance": 0.009, "planet_count": 5}
        ]
        
        self.generate_stars()
        self.generate_enemies()
        self.generate_planets()
        
        # Create buttons
        button_width, button_height = 250, 60
        self.start_button = Button(WIDTH//2 - button_width//2, HEIGHT//2, button_width, button_height, "Start Game")
        self.retry_button = Button(WIDTH//2 - button_width//2, HEIGHT//2 + 100, button_width, button_height, "Try Again")
        
    def generate_stars(self):
        config = self.level_configs[self.level - 1]
        self.stars = []
        self.stars_to_generate = config["stars_required"]
        self.stars_generated = 0
        self.star_group_size = config["star_group_size"]
        self.star_spawn_chance = config["spawn_chance"]
        
    def generate_enemies(self):
        config = self.level_configs[self.level - 1]
        self.enemies = []
        for _ in range(config["enemy_count"]):
            self.enemies.append(Enemy(config["enemy_speed_factor"]))
            
    def generate_planets(self):
        config = self.level_configs[self.level - 1]
        self.planets = []
        for _ in range(config["planet_count"]):
            self.planets.append(Planet(self.level))
    
    def spawn_star_group(self):
        if self.stars_generated < self.stars_to_generate:
            group_size = random.randint(self.star_group_size[0], self.star_group_size[1])
            base_x = random.randint(100, WIDTH - 100)
            base_y = random.randint(-100, -20)
            
            for i in range(min(group_size, self.stars_to_generate - self.stars_generated)):
                star = Star()
                # Position stars with more spacing
                star.x = base_x + random.randint(-100, 100)
                star.y = base_y + random.randint(-40, 40)
                self.stars.append(star)
                self.stars_generated += 1
    
    def update(self):
        # Update player (for bullets)
        self.player.update()
            
        if self.state != "playing":
            return
            
        # Spawn star groups
        if random.random() < self.star_spawn_chance and self.stars_generated < self.stars_to_generate:
            self.spawn_star_group()
            
        # Update stars
        for star in self.stars:
            star.update()
            
            # Check if star is collected
            if (not star.collected and 
                abs(star.x - self.player.x) < 30 and 
                abs(star.y - self.player.y) < 30):
                star.collected = True
                self.player.collected_stars += 1
                self.player.score += 10 * self.level
                
            # Check if star is missed
            if star.is_off_screen() and not star.collected:
                self.player.missed_stars += 1
                star.collected = True  # Mark to remove
                
        # Remove collected or missed stars
        self.stars = [star for star in self.stars if not star.collected and not star.is_off_screen()]
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()
            
            # Enemy shooting
            if random.random() < 0.02 and enemy.alive:
                enemy.shoot()
                
            # Check collision with player
            if enemy.alive and (abs(enemy.x - self.player.x) < 40 and 
                abs(enemy.y - self.player.y) < 30):
                self.state = "game_over"
                
            # Check bullet collision with player
            for bullet in enemy.bullets:
                if (abs(bullet[0] - self.player.x) < 20 and 
                    abs(bullet[1] - self.player.y) < 20):
                    self.state = "game_over"
                    
        # Check player bullets hitting enemies
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                if enemy.alive and (abs(bullet[0] - enemy.x) < 25 and 
                    abs(bullet[1] - enemy.y) < 25):
                    # Remove bullet
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    # Hit enemy
                    enemy.hit()
                    # Create explosion
                    self.explosions.append(Explosion(enemy.x, enemy.y))
                    # Mark enemy as dead
                    enemy.alive = False
                    # Remove enemy
                    self.enemies.remove(enemy)
                    # Add score
                    self.player.score += 100
                    break
                    
        # Remove enemies that go off screen
        self.enemies = [enemy for enemy in self.enemies if not enemy.is_off_screen()]
        
        # Add new enemies if needed
        config = self.level_configs[self.level - 1]
        if len(self.enemies) < config["enemy_count"] and random.random() < 0.02:
            self.enemies.append(Enemy(config["enemy_speed_factor"]))
            
        # Update planets
        for planet in self.planets:
            planet.update()
            
        # Update explosions
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.is_finished():
                self.explosions.remove(explosion)
            
        # Check if level is complete
        if self.player.collected_stars >= self.stars_to_generate:
            if self.level_change_timer == 0:
                self.level_change_timer = LEVEL_CHANGE_DELAY
            else:
                self.level_change_timer -= 1
                if self.level_change_timer <= 0:
                    self.level += 1
                    if self.level > len(self.level_configs):
                        self.state = "game_over"  # Game completed
                    else:
                        self.generate_stars()
                        self.generate_enemies()
                        self.generate_planets()
                        self.player.collected_stars = 0
                        self.player.missed_stars = 0
                        self.level_change_timer = 0
                        
        # Check if game is lost
        if self.player.missed_stars > 0:
            self.state = "game_over"
    
    def draw_background(self, surface):
        # Draw space background
        surface.fill(BACKGROUND)
        
        # Draw stars in background
        for i in range(100):
            x = (i * 17) % WIDTH
            y = (i * 23) % HEIGHT
            size = 1 + (i % 3)
            brightness = 150 + 105 * math.sin(pygame.time.get_ticks() * 0.0001 + i)
            pygame.draw.circle(surface, (brightness, brightness, brightness), (x, y), size)
        
        # Draw nebula effects
        for i in range(3):
            alpha = 30
            color = (50 + i*40, 50, 100 + i*50, alpha)
            x = WIDTH * 0.2 + i * 200
            y = HEIGHT * 0.3 + i * 100
            radius = 150 + i * 50
            nebula_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(nebula_surf, color, (radius, radius), radius)
            surface.blit(nebula_surf, (x - radius, y - radius))
    
    def draw(self, surface):
        self.draw_background(surface)
        
        # Draw planets
        for planet in self.planets:
            planet.draw(surface)
            
        # Draw stars
        for star in self.stars:
            star.draw(surface)
            
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(surface)
            
        # Draw explosions
        for explosion in self.explosions:
            explosion.draw(surface)
            
        # Draw player
        self.player.draw(surface)
        
        # Draw UI
        # Draw score and level
        score_text = font_small.render(f"Score: {self.player.score}", True, TEXT_COLOR)
        level_text = font_small.render(f"Level: {self.level}/10", True, TEXT_COLOR)
        stars_text = font_small.render(f"Stars: {self.player.collected_stars}/{self.stars_to_generate}", True, TEXT_COLOR)
        
        surface.blit(score_text, (20, 20))
        surface.blit(level_text, (20, 50))
        surface.blit(stars_text, (20, 80))
        
        # Draw progress bar for stars
        pygame.draw.rect(surface, (40, 40, 80), (WIDTH - 220, 20, 200, 20), border_radius=10)
        progress_width = 196 * (self.player.collected_stars / self.stars_to_generate)
        pygame.draw.rect(surface, (100, 200, 255), (WIDTH - 218, 22, progress_width, 16), border_radius=8)
        
        # Draw game state overlays
        if self.state == "menu":
            self.draw_menu(surface)
        elif self.state == "game_over":
            self.draw_game_over(surface)
        elif self.state == "level_complete":
            self.draw_level_complete(surface)
            
        # Draw level transition
        if self.level_change_timer > 0:
            alpha = min(255, (LEVEL_CHANGE_DELAY - self.level_change_timer) * 4)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, alpha))
            surface.blit(overlay, (0, 0))
            
            level_text = font_large.render(f"Level {self.level} Complete!", True, (255, 255, 200))
            surface.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2 - 50))
            
            if self.level < 10:
                next_text = font_medium.render(f"Preparing for Level {self.level + 1}...", True, TEXT_COLOR)
                surface.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2 + 20))
    
    def draw_menu(self, surface):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 20, 200))
        surface.blit(overlay, (0, 0))
        
        # Draw title
        title_text = title_font.render("GALACTIC STAR COLLECTOR", True, (255, 255, 200))
        surface.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4))
        
        # Draw subtitle
        subtitle_text = font_medium.render("Collect stars per level while avoiding enemy ships", True, TEXT_COLOR)
        surface.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, HEIGHT//4 + 80))
        
        # Draw instructions
        instructions = [
            "CONTROLS:",
            "- Use LEFT and RIGHT arrow keys to move horizontally",
            "- Use UP and DOWN arrow keys to move vertically",
            "- Press SPACE to shoot enemy ships",
            "- Collect stars before they leave the screen",
            "- Avoid enemy ships and their bullets",
            "",
            f"Complete all 10 levels to win the game!"
        ]
        
        for i, line in enumerate(instructions):
            text = font_small.render(line, True, TEXT_COLOR)
            surface.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + 20 + i*35))
        
        # Draw button
        self.start_button.draw(surface)
    
    def draw_game_over(self, surface):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # Draw game over text
        if self.level > 10:
            title_text = font_large.render("CONGRATULATIONS!", True, (100, 255, 150))
            subtitle_text = font_medium.render("You've completed all 10 levels!", True, TEXT_COLOR)
        else:
            title_text = font_large.render("GAME OVER", True, (255, 100, 100))
            if self.player.missed_stars > 0:
                subtitle_text = font_medium.render("You missed a star!", True, TEXT_COLOR)
            else:
                subtitle_text = font_medium.render("You were destroyed by an enemy!", True, TEXT_COLOR)
        
        surface.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//3))
        surface.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, HEIGHT//3 + 60))
        
        # Draw score
        score_text = font_medium.render(f"Final Score: {self.player.score}", True, (255, 255, 200))
        level_text = font_medium.render(f"Level Reached: {self.level}/10", True, TEXT_COLOR)
        surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        surface.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2 + 50))
        
        # Draw button
        self.retry_button.draw(surface)
    
    def reset_game(self):
        self.player.reset()
        self.stars = []
        self.enemies = []
        self.planets = []
        self.explosions = []
        self.level = 1
        self.state = "playing"
        self.level_change_timer = 0
        self.generate_stars()
        self.generate_enemies()
        self.generate_planets()

# Create game instance
game = Game()
clock = pygame.time.Clock()

# Main game loop
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            
        # Handle button clicks
        if game.state == "menu":
            game.start_button.check_hover(mouse_pos)
            if game.start_button.is_clicked(mouse_pos, event):
                game.reset_game()
                
        elif game.state == "game_over":
            game.retry_button.check_hover(mouse_pos)
            if game.retry_button.is_clicked(mouse_pos, event):
                game.reset_game()
    
    # Handle player input
    keys = pygame.key.get_pressed()
    if game.state == "playing":
        if keys[K_LEFT]:
            game.player.move("left")
        if keys[K_RIGHT]:
            game.player.move("right")
        # Add vertical movement controls
        if keys[K_UP]:
            game.player.move("up")
        if keys[K_DOWN]:
            game.player.move("down")
        if keys[K_SPACE]:
            game.player.shoot()
    
    # Update game state
    game.update()
    
    # Draw everything
    game.draw(screen)
    
    # Update the display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()