import pygame
import sys
import random
import math
import os

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Star Collector")

# Colors
BACKGROUND = (5, 5, 15)  # Dark space color
BALL_COLOR = (255, 105, 180)  # Bright pink
STAR_COLOR = (255, 255, 100)  # Bright yellow
TEXT_COLOR = (230, 230, 250)  # Lavender
UI_BG = (30, 30, 60, 200)     # Semi-transparent UI background
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 160, 210)
NEBULA_COLORS = [(100, 60, 180), (180, 60, 100), (60, 100, 180)]  # Purple, pink, blue

# Game variables
clock = pygame.time.Clock()
FPS = 60
font = pygame.font.SysFont("Arial", 24, bold=True)
title_font = pygame.font.SysFont("Arial", 48, bold=True)
level = 1
stars_collected = 0
game_started = False
game_over = False
ball_dropped = False
particles = []

# Galaxy background stars
background_stars = []
for _ in range(200):
    background_stars.append({
        'x': random.randint(0, WIDTH),
        'y': random.randint(0, HEIGHT),
        'size': random.uniform(0.5, 2),
        'brightness': random.uniform(0.3, 1.0),
        'speed': random.uniform(0.1, 0.3)
    })

# Nebula positions
nebulas = []
for _ in range(5):
    nebulas.append({
        'x': random.randint(0, WIDTH),
        'y': random.randint(0, HEIGHT),
        'size': random.randint(100, 300),
        'color': random.choice(NEBULA_COLORS),
        'alpha': random.randint(10, 40)
    })

# Ball properties
ball_radius = 30
ball_x = WIDTH // 2
ball_y = 100
ball_speed = 1.0
ball_clicked = False

# Star properties
stars = []
base_stars = 4
stars_per_level = 3
stars_to_collect = base_stars + stars_per_level * (level - 1)

# Create initial stars
def create_stars():
    global stars
    stars = []
    for _ in range(stars_to_collect):
        stars.append({
            'x': random.randint(50, WIDTH - 50),
            'y': random.randint(-200, -50),
            'collected': False,
            'speed': random.uniform(1.5, 2.5),
            'size': random.randint(15, 25),
            'glow': 0,
            'angle': random.uniform(0, 2 * math.pi),
            'trail': []
        })

create_stars()

# Particle system for effects
def create_particles(x, y, color, count=10):
    for _ in range(count):
        particles.append({
            'x': x,
            'y': y,
            'color': color,
            'size': random.randint(2, 6),
            'speed_x': random.uniform(-3, 3),
            'speed_y': random.uniform(-3, 3),
            'life': 30
        })

def update_particles():
    for particle in particles[:]:
        particle['x'] += particle['speed_x']
        particle['y'] += particle['speed_y']
        particle['life'] -= 1
        if particle['life'] <= 0:
            particles.remove(particle)

# Draw a star with points
def draw_star(surface, x, y, size, color, glow=0):
    # Draw glow effect
    if glow > 0:
        glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color, int(glow * 50)), 
                          (size * 2, size * 2), size * 2)
        surface.blit(glow_surf, (x - size * 2, y - size * 2))
    
    # Draw star shape
    points = []
    for i in range(5):
        # Outer points
        angle = math.pi/2 + i * 2*math.pi/5
        points.append((x + size * math.cos(angle), 
                      y - size * math.sin(angle)))
        # Inner points
        angle += math.pi/5
        points.append((x + (size/2) * math.cos(angle), 
                      y - (size/2) * math.sin(angle)))
    
    pygame.draw.polygon(surface, color, points)

# Draw a rounded rectangle
def draw_rounded_rect(surface, rect, color, corner_radius):
    pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

# Button class for UI
class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        
    def draw(self, surface):
        color = BUTTON_HOVER if self.hovered else BUTTON_COLOR
        draw_rounded_rect(surface, self.rect, color, 10)
        
        text_surf = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()
                return True
        return False

# Button actions
def start_game():
    global game_started, ball_clicked
    game_started = True
    ball_clicked = True

def restart_game():
    global level, stars_collected, game_started, game_over, ball_dropped, ball_clicked, ball_y, stars_to_collect
    level = 1
    stars_collected = 0
    game_started = False
    game_over = False
    ball_dropped = False
    ball_clicked = False
    ball_y = 100
    stars_to_collect = base_stars + stars_per_level * (level - 1)
    particles.clear()
    create_stars()

def next_level():
    global level, stars_collected, stars_to_collect, game_started, ball_clicked, ball_dropped, ball_y
    level += 1
    stars_collected = 0
    stars_to_collect = base_stars + stars_per_level * (level - 1)
    game_started = False
    ball_clicked = False
    ball_dropped = False
    ball_y = 100
    particles.clear()
    create_stars()

# Create buttons
start_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "START GAME", start_game)
restart_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "PLAY AGAIN", restart_game)
next_level_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "NEXT LEVEL", next_level)

# Draw galaxy background
def draw_galaxy_background():
    # Draw background stars
    for star in background_stars:
        brightness = int(255 * star['brightness'])
        pygame.draw.circle(screen, (brightness, brightness, brightness), 
                          (int(star['x']), int(star['y'])), 
                          star['size'])
    
    # Draw nebula effects
    for nebula in nebulas:
        nebula_surf = pygame.Surface((nebula['size'] * 2, nebula['size'] * 2), pygame.SRCALPHA)
        pygame.draw.circle(nebula_surf, (*nebula['color'], nebula['alpha']), 
                          (nebula['size'], nebula['size']), nebula['size'])
        screen.blit(nebula_surf, (nebula['x'] - nebula['size'], nebula['y'] - nebula['size']))

# Main game loop
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Handle button clicks
        if game_over:
            if restart_button.handle_event(event):
                continue
        elif stars_collected >= stars_to_collect and level < 10:
            if next_level_button.handle_event(event):
                continue
        elif not game_started:
            if start_button.handle_event(event):
                continue
        
        if event.type == pygame.MOUSEBUTTONDOWN and not ball_clicked and game_started:
            # Check if ball is clicked
            distance = math.sqrt((mouse_pos[0] - ball_x)**2 + (mouse_pos[1] - ball_y)**2)
            if distance <= ball_radius:
                ball_clicked = True
                create_particles(ball_x, ball_y, BALL_COLOR, 20)
    
    # Update game state if game is active
    if game_started and ball_clicked and not game_over:
        # Move ball down
        ball_y += ball_speed
        
        # Move stars down and update their glow
        for star in stars:
            if not star['collected']:
                # Add position to trail (for drawing effect)
                if len(star['trail']) > 5:
                    star['trail'].pop(0)
                star['trail'].append((star['x'], star['y']))
                
                star['y'] += star['speed']
                star['angle'] += 0.05
                star['glow'] = 0.5 + 0.5 * math.sin(star['angle'] * 3)
                
                # Check if star is collected
                star_rect = pygame.Rect(star['x'] - star['size'], star['y'] - star['size'], 
                                       star['size'] * 2, star['size'] * 2)
                if star_rect.collidepoint(mouse_pos):
                    star['collected'] = True
                    stars_collected += 1
                    create_particles(star['x'], star['y'], STAR_COLOR, 15)
        
        # Check if ball reached the bottom
        if ball_y > HEIGHT - ball_radius + 10 and not ball_dropped:
            game_over = True
            ball_dropped = True
            create_particles(ball_x, HEIGHT - 20, BALL_COLOR, 30)
    
    # Update particles
    update_particles()
    
    # Update background stars for parallax effect
    for star in background_stars:
        star['y'] += star['speed'] * 0.1
        if star['y'] > HEIGHT:
            star['y'] = 0
            star['x'] = random.randint(0, WIDTH)
    
    # Update button hover states
    if game_over:
        restart_button.check_hover(mouse_pos)
    elif stars_collected >= stars_to_collect and level < 10:
        next_level_button.check_hover(mouse_pos)
    elif not game_started:
        start_button.check_hover(mouse_pos)
    
    # Drawing
    screen.fill(BACKGROUND)
    
    # Draw galaxy background
    draw_galaxy_background()
    
    # Draw star trails
    for star in stars:
        if not star['collected']:
            # Draw trail
            for i, (trail_x, trail_y) in enumerate(star['trail']):
                alpha = int(200 * (i / len(star['trail'])))
                size = star['size'] * (i / len(star['trail']))
                trail_surf = pygame.Surface((int(size * 4), int(size * 4)), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, (*STAR_COLOR, alpha), 
                                  (int(size * 2), int(size * 2)), size * 2)
                screen.blit(trail_surf, (trail_x - size * 2, trail_y - size * 2))
    
    # Draw stars
    for star in stars:
        if not star['collected']:
            draw_star(screen, star['x'], star['y'], star['size'], STAR_COLOR, star['glow'])
    
    # Draw particles
    for particle in particles:
        pygame.draw.circle(screen, particle['color'], 
                          (int(particle['x']), int(particle['y'])), 
                          particle['size'])
    
    # Draw ball
    if not ball_dropped:
        # Add glow to ball
        glow_surf = pygame.Surface((ball_radius * 4, ball_radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*BALL_COLOR, 100), 
                          (ball_radius * 2, ball_radius * 2), ball_radius * 2)
        screen.blit(glow_surf, (ball_x - ball_radius * 2, ball_y - ball_radius * 2))
        
        # Draw the ball
        pygame.draw.circle(screen, BALL_COLOR, (ball_x, ball_y), ball_radius)
        pygame.draw.circle(screen, (255, 200, 230), (ball_x, ball_y), ball_radius - 5)
        
        # Draw ball shine
        pygame.draw.circle(screen, (255, 255, 255, 150), 
                          (ball_x - ball_radius//3, ball_y - ball_radius//3), 
                          ball_radius//4)
    
    # Draw UI panel
    ui_panel = pygame.Surface((250, 120), pygame.SRCALPHA)
    draw_rounded_rect(ui_panel, (0, 0, 250, 120), UI_BG, 15)
    screen.blit(ui_panel, (WIDTH - 270, 20))
    
    # Draw star counter
    stars_text = font.render(f"Stars: {stars_collected}/{stars_to_collect}", True, TEXT_COLOR)
    screen.blit(stars_text, (WIDTH - 250, 50))
    
    # Draw level counter
    level_text = font.render(f"Level: {level}/10", True, TEXT_COLOR)
    screen.blit(level_text, (WIDTH - 250, 85))
    
    # Draw title
    if not game_started:
        title = title_font.render("GALAXY STAR COLLECTOR", True, (255, 215, 0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        subtitle = font.render("Click the ball to start collecting stars!", True, TEXT_COLOR)
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 160))
    
    # Draw game state messages
    if not ball_clicked and game_started:
        instruction = font.render("CLICK THE BALL TO DROP IT", True, (255, 100, 100))
        screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT - 100))
    
    if game_over:
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Draw game over message
        game_over_text = title_font.render("GAME OVER", True, (255, 100, 100))
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
        
        message = font.render("You lose, but you can try again!", True, TEXT_COLOR)
        screen.blit(message, (WIDTH//2 - message.get_width()//2, HEIGHT//2 - 30))
        
        restart_button.draw(screen)
    
    elif stars_collected >= stars_to_collect:
        if level < 10:
            # Draw level complete message
            level_complete = title_font.render("LEVEL COMPLETE!", True, (100, 255, 100))
            screen.blit(level_complete, (WIDTH//2 - level_complete.get_width()//2, HEIGHT//2 - 100))
            
            message = font.render(f"Get ready for level {level+1}!", True, TEXT_COLOR)
            screen.blit(message, (WIDTH//2 - message.get_width()//2, HEIGHT//2 - 30))
            
            next_level_button.draw(screen)
        else:
            # Draw game complete message
            game_complete = title_font.render("YOU WIN!", True, (100, 255, 100))
            screen.blit(game_complete, (WIDTH//2 - game_complete.get_width()//2, HEIGHT//2 - 100))
            
            message = font.render("Congratulations! You collected all stars!", True, TEXT_COLOR)
            screen.blit(message, (WIDTH//2 - message.get_width()//2, HEIGHT//2 - 30))
            
            restart_button.draw(screen)
    
    elif not game_started:
        start_button.draw(screen)
    
    # Draw cursor
    pygame.draw.circle(screen, TEXT_COLOR, mouse_pos, 8)
    pygame.draw.circle(screen, STAR_COLOR, mouse_pos, 5)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
# Save the game state to a file
def save_game_state():
    state = {
        'level': level,
        'stars_collected': stars_collected,
        'game_started': game_started,
        'game_over': game_over,
        'ball_dropped': ball_dropped,
        'ball_y': ball_y,
        'stars_to_collect': stars_to_collect,
        'stars': stars
    }
    with open('save_game.json', 'w') as f:
        json.dump(state, f)