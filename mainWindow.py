# import the pygame module
import pygame
import sys

# Initialize pygame
pygame.init()

# Define the background colour using RGB color coding
background_colour = (255, 255, 255)

# Define the dimensions of screen object(width,height)
screen = pygame.display.set_mode((500, 500))

# Set the caption of the screen
pygame.display.set_caption('Dopple')

# Initialize clock for frame rate control
clock = pygame.time.Clock()

# Initialize circles list
circles = []

# Circle class to manage expanding circles
class ExpandingCircle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 1
        self.max_radius = 200
        self.expansion_rate = 2
        self.colorA = (200, 200, 255)  # Blueish White
        self.colorB = (235, 235, 235)  # Light Gray
        self.alpha = 255  # Transparency
        self.colorAlt = True
        
    @property
    def color(self):
        return self.colorA if self.colorAlt else self.colorB
        
    def update(self):
        # Expand the circle
        self.radius += self.expansion_rate
        
        # Fade out as it expands
        fade_ratio = 1 - (self.radius / self.max_radius)
        self.alpha = max(0, int(255 * fade_ratio))
        
        # Return True if circle should be removed
        return self.radius >= self.max_radius
    
    def draw(self, surface):
        if self.alpha > 0:
            # Create a surface for the circle with alpha
            circle_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, self.alpha)
            pygame.draw.circle(circle_surface, color_with_alpha, (self.radius, self.radius), self.radius)
            
            # Draw the circle surface to the main surface
            surface.blit(circle_surface, (self.x - self.radius, self.y - self.radius))

# Variable to keep our game loop running
running = True

# Game loop
while running:

    mouse_x, mouse_y = pygame.mouse.get_pos() # create new circle at mouse position
    circles.append(ExpandingCircle(mouse_x, mouse_y))
    
    # Handle events
    for event in pygame.event.get():
        # Check for QUIT event      
        if event.type == pygame.QUIT:
            running = False
        # Check for mouse clicks
        #elif event.type == pygame.MOUSEBUTTONDOWN:
        #    mouse_x, mouse_y = pygame.mouse.get_pos()
        #    circles.append(ExpandingCircle(mouse_x, mouse_y))
    
    # Update circles and remove completed ones
    circles = [circle for circle in circles if not circle.update()]
    
    # Fill the background colour to the screen
    screen.fill(background_colour)
    
    # Draw all circles
    for circle in circles:
        circle.draw(screen)
    
    # Update the display using flip
    pygame.display.flip()
    
    # Control frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()
