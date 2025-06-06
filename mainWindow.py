# import the pygame module
import pygame
import sys
import math

# Initialize pygame
pygame.init()

# Define constants
BACKGROUND_COLOR = (255, 255, 255)
SCREEN_SIZE = (500, 500)
BLUE_COLOR = (100, 149, 237)  # CornflowerBlue
LIGHT_BLUE_COLOR = (173, 216, 230)  # LightBlue
MENU_BG_COLOR = (240, 240, 240)
MENU_TEXT_COLOR = (50, 50, 50)
TEXTBOX_COLOR = (255, 255, 255)
TEXTBOX_BORDER_COLOR = (100, 100, 100)
TEXTBOX_ACTIVE_COLOR = (200, 230, 255)
BUTTON_COLOR = (70, 130, 180)
BUTTON_TEXT_COLOR = (255, 255, 255)
TRIANGLE_COLOR = (120, 120, 120)  # Grey color for triangle
INTERFERENCE_CONSTRUCTIVE = (255, 100, 100)  # Red for constructive
INTERFERENCE_DESTRUCTIVE = (100, 100, 255)   # Blue for destructive

# Initialize screen and clock
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('Dopple')
clock = pygame.time.Clock()
font = pygame.font.Font(None, 20)
title_font = pygame.font.Font(None, 36)
ui_font = pygame.font.Font(None, 18)

# Game parameters (configurable via menu)
game_params = {
    'frame_rate': 20,
    'spawn_rate': 10,
    'expansion_rate': 2,
    'max_radius': 200,
    'speed_threshold': 2
}

class TextBox:
    def __init__(self, x, y, width, height, label, initial_value, min_val=1, max_val=1000):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.text = str(initial_value)
        self.active = False
        self.min_val = min_val
        self.max_val = max_val
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                self.active = False
                # Validate input
                try:
                    val = int(self.text)
                    val = max(self.min_val, min(self.max_val, val))
                    self.text = str(val)
                except ValueError:
                    self.text = str(self.min_val)
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit():
                self.text += event.unicode
    
    def update(self):
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def get_value(self):
        try:
            return int(self.text) if self.text else self.min_val
        except ValueError:
            return self.min_val
    
    def draw(self, surface):
        color = TEXTBOX_ACTIVE_COLOR if self.active else TEXTBOX_COLOR
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, TEXTBOX_BORDER_COLOR, self.rect, 2)
        
        # Draw label above textbox
        label_text = font.render(self.label, True, MENU_TEXT_COLOR)
        surface.blit(label_text, (self.rect.x, self.rect.y - 25))
        
        # Draw text
        text_surface = font.render(self.text, True, MENU_TEXT_COLOR)
        surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        
        # Draw cursor
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 5 + text_surface.get_width()
            pygame.draw.line(surface, MENU_TEXT_COLOR, 
                           (cursor_x, self.rect.y + 5), 
                           (cursor_x, self.rect.y + self.rect.height - 5), 2)

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.action()
    
    def draw(self, surface):
        color = (90, 150, 200) if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, MENU_TEXT_COLOR, self.rect, 2)
        
        text_surface = font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class MenuState:
    def __init__(self):
        # Properly spaced layout
        center_x = SCREEN_SIZE[0] // 2
        start_y = 100
        spacing = 55
        textbox_width = 120
        
        self.textboxes = [
            TextBox(center_x - textbox_width//2, start_y, textbox_width, 30, 
                   "Frame Rate (10-60)", game_params['frame_rate'], 10, 60),
            TextBox(center_x - textbox_width//2, start_y + spacing, textbox_width, 30, 
                   "Spawn Rate (5-30)", game_params['spawn_rate'], 5, 30),
            TextBox(center_x - textbox_width//2, start_y + spacing * 2, textbox_width, 30, 
                   "Expansion Rate (1-10)", game_params['expansion_rate'], 1, 10),
            TextBox(center_x - textbox_width//2, start_y + spacing * 3, textbox_width, 30, 
                   "Max Radius (50-500)", game_params['max_radius'], 50, 500),
            TextBox(center_x - textbox_width//2, start_y + spacing * 4, textbox_width, 30, 
                   "Speed Threshold (1-20)", game_params['speed_threshold'], 1, 20)
        ]
        
        self.start_button = Button(center_x - 50, start_y + spacing * 5 + 20, 
                                 100, 40, "START", self.start_game)
        self.running = True
    
    def start_game(self):
        for i, param_key in enumerate(['frame_rate', 'spawn_rate', 'expansion_rate', 
                                     'max_radius', 'speed_threshold']):
            game_params[param_key] = self.textboxes[i].get_value()
        self.running = False
    
    def handle_event(self, event):
        for textbox in self.textboxes:
            textbox.handle_event(event)
        self.start_button.handle_event(event)
    
    def update(self):
        for textbox in self.textboxes:
            textbox.update()
    
    def draw(self, surface):
        surface.fill(MENU_BG_COLOR)
        
        # Title
        title_text = title_font.render("DOPPLE", True, MENU_TEXT_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_SIZE[0]//2, 40))
        surface.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = font.render("Wave Interference Simulator", True, MENU_TEXT_COLOR)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_SIZE[0]//2, 65))
        surface.blit(subtitle_text, subtitle_rect)
        
        for textbox in self.textboxes:
            textbox.draw(surface)
        self.start_button.draw(surface)

class ExpandingCircle:
    __slots__ = ['x', 'y', 'radius', 'alpha', 'color', 'max_radius']
    
    def __init__(self, x, y, use_blue=True):
        self.x = x
        self.y = y
        self.radius = 1
        self.alpha = 255
        self.color = BLUE_COLOR if use_blue else LIGHT_BLUE_COLOR
        self.max_radius = game_params['max_radius']
    
    def update(self):
        self.radius += game_params['expansion_rate']
        
        if self.radius >= self.max_radius:
            return True
        
        fade_ratio = 1.0 - (self.radius / self.max_radius)
        self.alpha = max(0, int(255 * fade_ratio))
        return False
    
    def draw(self, surface):
        if self.alpha > 10:  # Skip nearly invisible circles
            diameter = self.radius * 2
            circle_surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
            color_with_alpha = (*self.color, self.alpha)
            pygame.draw.circle(circle_surface, color_with_alpha, (self.radius, self.radius), self.radius)
            surface.blit(circle_surface, (self.x - self.radius, self.y - self.radius))
    
    def get_distance_to_point(self, x, y):
        dx = self.x - x
        dy = self.y - y
        return math.sqrt(dx * dx + dy * dy)
    
    def is_colliding_with_point(self, x, y):
        return self.get_distance_to_point(x, y) <= self.radius

class CollisionDetector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collision_history = []
        self.current_collisions_per_second = 0.0
        self.colliding_circles = set()
        self.size = 10
    
    def check_collision(self, circle, circle_id):
        current_time = pygame.time.get_ticks()
        is_colliding = circle.is_colliding_with_point(self.x, self.y)
        
        if is_colliding and circle_id not in self.colliding_circles:
            self.collision_history.append(current_time)
            self.colliding_circles.add(circle_id)
        elif not is_colliding and circle_id in self.colliding_circles:
            self.colliding_circles.discard(circle_id)
    
    def update(self):
        current_time = pygame.time.get_ticks()
        cutoff_time = current_time - 1000
        self.collision_history = [t for t in self.collision_history if t > cutoff_time]
        self.current_collisions_per_second = len(self.collision_history)
    
    def get_collisions_per_second(self):
        return self.current_collisions_per_second
    
    def draw(self, surface):
        detector_color = (255, 50, 50)
        outline_color = (150, 0, 0)
        
        detector_rect = pygame.Rect(self.x - self.size//2, self.y - self.size//2, 
                                  self.size, self.size)
        pygame.draw.rect(surface, detector_color, detector_rect)
        pygame.draw.rect(surface, outline_color, detector_rect, 2)
        
        # Center cross
        pygame.draw.line(surface, outline_color,
                        (self.x - 3, self.y), (self.x + 3, self.y), 1)
        pygame.draw.line(surface, outline_color,
                        (self.x, self.y - 3), (self.x, self.y + 3), 1)

class InterferencePoint:
    def __init__(self, x, y, interference_type, intensity):
        self.x = x
        self.y = y
        self.type = interference_type  # 'constructive' or 'destructive'
        self.intensity = intensity
        self.life_timer = 30  # Frames to display
    
    def update(self):
        self.life_timer -= 1
        return self.life_timer <= 0
    
    def draw(self, surface):
        if self.life_timer > 0:
            alpha = int(255 * (self.life_timer / 30))
            color = INTERFERENCE_CONSTRUCTIVE if self.type == 'constructive' else INTERFERENCE_DESTRUCTIVE
            
            # Draw small circle
            size = int(4 + self.intensity * 3)
            circle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color_with_alpha = (*color, alpha)
            pygame.draw.circle(circle_surface, color_with_alpha, (size, size), size)
            surface.blit(circle_surface, (self.x - size, self.y - size))

def draw_cutting_triangle(surface, x, y, dx, dy, intensity=1.0):
    """Draw single large grey triangle pointing in movement direction"""
    if dx == 0 and dy == 0:
        return
    
    angle = math.atan2(dy, dx)
    size = 25 * intensity
    
    # Triangle points
    tip_x = x + math.cos(angle) * size
    tip_y = y + math.sin(angle) * size
    
    perp_angle = angle + math.pi / 2
    base_width = size * 0.8
    
    base1_x = x + math.cos(perp_angle) * base_width
    base1_y = y + math.sin(perp_angle) * base_width
    base2_x = x - math.cos(perp_angle) * base_width
    base2_y = y - math.sin(perp_angle) * base_width
    
    alpha = max(100, int(200 * intensity))
    triangle_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
    
    center = size * 1.5
    points = [
        (tip_x - x + center, tip_y - y + center),
        (base1_x - x + center, base1_y - y + center),
        (base2_x - x + center, base2_y - y + center)
    ]
    
    color_with_alpha = (*TRIANGLE_COLOR, alpha)
    pygame.draw.polygon(triangle_surface, color_with_alpha, points)
    pygame.draw.polygon(triangle_surface, (80, 80, 80, alpha), points, 2)
    
    surface.blit(triangle_surface, (x - center, y - center))

def detect_wave_interference(circles):
    """Detect constructive and destructive interference points"""
    interference_points = []
    
    # Check interference between circle pairs
    for i in range(len(circles)):
        for j in range(i + 1, len(circles)):
            circle1, circle2 = circles[i], circles[j]
            
            # Skip if circles are too far apart
            distance = circle1.get_distance_to_point(circle2.x, circle2.y)
            if distance > circle1.radius + circle2.radius + 50:
                continue
            
            # Check for interference along the line between circle centers
            for t in [0.3, 0.5, 0.7]:  # Sample points along the line
                test_x = circle1.x + t * (circle2.x - circle1.x)
                test_y = circle1.y + t * (circle2.y - circle1.y)
                
                dist1 = circle1.get_distance_to_point(test_x, test_y)
                dist2 = circle2.get_distance_to_point(test_x, test_y)
                
                # Check if both circles affect this point
                if (abs(dist1 - circle1.radius) < 20 and abs(dist2 - circle2.radius) < 20):
                    # Determine interference type
                    phase_diff = abs(dist1 - dist2) % (2 * math.pi)
                    
                    if phase_diff < math.pi / 2 or phase_diff > 3 * math.pi / 2:
                        # Constructive interference
                        intensity = (circle1.alpha + circle2.alpha) / 510.0
                        interference_points.append(InterferencePoint(test_x, test_y, 'constructive', intensity))
                    else:
                        # Destructive interference
                        intensity = abs(circle1.alpha - circle2.alpha) / 255.0
                        interference_points.append(InterferencePoint(test_x, test_y, 'destructive', intensity))
    
    return interference_points

def run_menu():
    menu = MenuState()
    
    while menu.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            menu.handle_event(event)
        
        menu.update()
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(30)

def run_game():
    circles = []
    circle_count = 0
    previous_mouse_pos = pygame.mouse.get_pos()
    mouse_held = False
    circle_spawn_timer = 0
    show_cutting_effect = False
    mouse_dx = 0
    mouse_dy = 0
    collision_detectors = []
    interference_points = []
    
    running = True
    while running:
        current_mouse_pos = pygame.mouse.get_pos()
        
        # Calculate mouse movement
        mouse_dx = current_mouse_pos[0] - previous_mouse_pos[0]
        mouse_dy = current_mouse_pos[1] - previous_mouse_pos[1]
        mouse_speed_squared = mouse_dx * mouse_dx + mouse_dy * mouse_dy
        threshold_squared = game_params['speed_threshold'] * game_params['speed_threshold']
        
        show_cutting_effect = mouse_speed_squared > threshold_squared
        previous_mouse_pos = current_mouse_pos
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_held = True
                    circle_spawn_timer = 0
                elif event.button == 3:  # Right click
                    collision_detectors.append(CollisionDetector(current_mouse_pos[0], current_mouse_pos[1]))
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_held = False
        
        # Spawn circles
        if mouse_held:
            circle_spawn_timer += 1
            if circle_spawn_timer >= game_params['spawn_rate']:
                use_blue = (circle_count & 1) == 0
                circles.append(ExpandingCircle(current_mouse_pos[0], current_mouse_pos[1], use_blue))
                circle_count += 1
                circle_spawn_timer = 0
        
        # Update circles and check collisions
        updated_circles = []
        for i, circle in enumerate(circles):
            if not circle.update():
                updated_circles.append(circle)
                
                for detector in collision_detectors:
                    detector.check_collision(circle, i + circle_count * 1000)
        
        circles = updated_circles
        
        # Update detectors
        for detector in collision_detectors:
            detector.update()
        
        # Detect wave interference (limit frequency for performance)
        if len(circles) > 1 and pygame.time.get_ticks() % 5 == 0:  # Every 5 frames
            new_interference = detect_wave_interference(circles)
            interference_points.extend(new_interference)
        
        # Update interference points
        interference_points[:] = [point for point in interference_points if not point.update()]
        
        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        
        # Draw circles
        for circle in circles:
            circle.draw(screen)
        
        # Draw interference points
        for point in interference_points:
            point.draw(screen)
        
        # Draw collision detectors
        for detector in collision_detectors:
            detector.draw(screen)
        
        # Draw cutting triangle
        if show_cutting_effect:
            intensity = min(1.0, math.sqrt(mouse_speed_squared) / (game_params['speed_threshold'] * 3))
            draw_cutting_triangle(screen, current_mouse_pos[0], current_mouse_pos[1], 
                                mouse_dx, mouse_dy, intensity)
        
        # Draw UI
        y_offset = 10
        ui_text = ui_font.render("ESC: Menu | Left: Spawn | Right: Detector", True, (100, 100, 100))
        screen.blit(ui_text, (10, y_offset))
        
        # Display collision frequencies
        if collision_detectors:
            y_offset += 20
            for i, detector in enumerate(collision_detectors):
                freq_text = ui_font.render(f"Detector {i+1}: {detector.get_collisions_per_second():.1f} Hz", 
                                         True, (255, 50, 50))
                screen.blit(freq_text, (10, y_offset))
                y_offset += 18
        
        # Display interference count
        if interference_points:
            constructive = sum(1 for p in interference_points if p.type == 'constructive')
            destructive = sum(1 for p in interference_points if p.type == 'destructive')
            interference_text = ui_font.render(f"Interference - Constructive: {constructive} | Destructive: {destructive}", 
                                             True, (50, 50, 50))
            screen.blit(interference_text, (10, y_offset))
        
        pygame.display.flip()
        clock.tick(game_params['frame_rate'])
    
    return False

# Main program loop
while True:
    run_menu()
    should_continue = run_game()
    if not should_continue:
        break

pygame.quit()
sys.exit()