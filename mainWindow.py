# import the pygame module
import pygame
import sys

# Define the background colour
# using RGB color coding.
background_colour = (255, 255, 255)

# Define the dimensions of
# screen object(width,height)
screen = pygame.display.set_mode((500, 500))

# Set the caption of the screen
pygame.display.set_caption('Dopple')

# Circle class to manage expanding circles
class ExpandingCircle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 1
        self.max_radius = 500
        self.expansion_rate = 2
        self.colorA = (200, 200, 255)  # Blueish White
        self.colorB = (235, 235, 235)  # Light Gray
        self.alpha = 255  # Transparency
        self.colorAlt = True
        
    def update(self):
        # Expand the circle
        self.radius += self.expansion_rate
        
        # Fade out as it expands
        fade_ratio = 1 - (self.radius / self.max_radius)
        self.alpha = max(0, int(255 * fade_ratio))

        self.colorAlt = not self.colorAlt
        
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

# Fill the background colour to the screen
screen.fill(background_colour)

for circle in circles:
    circle.draw(screen)

# Update the display using flip
pygame.display.flip()

# Variable to keep our game loop running
running = True

# game loop
while running:
  
# for loop through the event queue  
    for event in pygame.event.get():
        mouse_x, mouse_y = pygame.mouse.get_pos()
        circles.append(ExpandingCircle(mouse_x, mouse_y))

        circles = [circle for circle in circles if not circle.update()]

        clock.tick(60)
        
        # Check for QUIT event      
        if event.type == pygame.QUIT:
            running = False
