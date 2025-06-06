import pygame
import math
import sys
import numpy as np

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Constants
WIDTH, HEIGHT = 1000, 600
FPS = 60
BACKGROUND_COLOR = (20, 20, 40)
SOURCE_COLOR = (255, 100, 100)
OBSERVER_COLOR = (100, 255, 100)
WAVE_COLOR = (100, 200, 255)
TEXT_COLOR = (255, 255, 255)

# Physics constants
SOUND_SPEED = 300  # pixels per second (scaled for visualization)
BASE_FREQUENCY = 440  # Hz (A4 note)
WAVE_FREQUENCY = 2  # visual waves per second
WAVE_LIFETIME = 3000  # milliseconds


class SoundGenerator:
    def __init__(self):
        self.sample_rate = 44100
        self.base_freq = BASE_FREQUENCY
        self.current_freq = BASE_FREQUENCY
        self.phase = 0
        self.is_playing = False

    def generate_tone(self, frequency, duration_ms=100):
        """Generate a sine wave tone at the specified frequency"""
        frames = int(duration_ms * self.sample_rate / 1000)
        arr = np.zeros((frames, 2))  # Stereo

        for i in range(frames):
            # Simple sine wave
            sample = np.sin(2 * np.pi * frequency * i / self.sample_rate) * 0.3
            arr[i] = [sample, sample]

        return (arr * 32767).astype(np.int16)

    def update_frequency(self, new_freq):
        """Update the frequency for the Doppler effect"""
        self.current_freq = max(50, min(2000, new_freq))  # Clamp frequency

    def play_continuous_tone(self):
        """Play a continuous tone that can be updated"""
        if not self.is_playing:
            # Generate a short tone buffer
            tone_data = self.generate_tone(self.current_freq, 200)
            sound = pygame.sndarray.make_sound(tone_data)
            sound.play(-1)  # Loop indefinitely
            self.is_playing = True
            return sound
        return None

    def stop(self):
        """Stop all sounds"""
        pygame.mixer.stop()
        self.is_playing = False


class SoundWave:
    def __init__(self, x, y, birth_time):
        self.center_x = x
        self.center_y = y
        self.birth_time = birth_time
        self.radius = 0

    def update(self, current_time):
        age = current_time - self.birth_time
        self.radius = (age / 1000.0) * SOUND_SPEED

    def is_alive(self, current_time):
        return (current_time - self.birth_time) < WAVE_LIFETIME

    def draw(self, screen, current_time):
        if self.is_alive(current_time) and self.radius > 0:
            # Fade out as wave gets older
            age = current_time - self.birth_time
            alpha = max(0, 255 - (age / WAVE_LIFETIME) * 255)

            # Create a surface for the wave circle with alpha
            wave_surface = pygame.Surface((self.radius * 2 + 4, self.radius * 2 + 4), pygame.SRCALPHA)
            color_with_alpha = (*WAVE_COLOR, int(alpha))

            if self.radius > 2:
                pygame.draw.circle(wave_surface, color_with_alpha,
                                   (self.radius + 2, self.radius + 2), int(self.radius), 2)
                screen.blit(wave_surface, (self.center_x - self.radius - 2,
                                           self.center_y - self.radius - 2))


class DopplerSimulation:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Interactive Doppler Effect - Move your mouse!")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # Source properties (follows cursor)
        self.source_x = WIDTH // 2
        self.source_y = HEIGHT // 2
        self.prev_source_x = self.source_x
        self.prev_source_y = self.source_y
        self.source_velocity_x = 0
        self.source_velocity_y = 0

        # Observer position (stationary)
        self.observer_x = WIDTH - 150
        self.observer_y = HEIGHT // 2

        # Wave management
        self.waves = []
        self.last_wave_time = 0
        self.wave_interval = 1000 / WAVE_FREQUENCY  # milliseconds between waves

        # Sound management
        self.sound_generator = SoundGenerator()
        self.current_sound = None
        self.last_sound_update = 0
        self.sound_update_interval = 50  # Update sound every 50ms

        # Frequency calculation
        self.observed_frequency = BASE_FREQUENCY
        self.sound_enabled = True

    def update_source_position(self, dt):
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Calculate velocity based on position change
        self.source_velocity_x = (mouse_x - self.prev_source_x) / dt if dt > 0 else 0
        self.source_velocity_y = (mouse_y - self.prev_source_y) / dt if dt > 0 else 0

        # Update position
        self.prev_source_x = self.source_x
        self.prev_source_y = self.source_y
        self.source_x = mouse_x
        self.source_y = mouse_y

    def calculate_observed_frequency(self):
        # Calculate distance and relative velocity toward observer
        dx = self.observer_x - self.source_x
        dy = self.observer_y - self.source_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            # Unit vector from source to observer
            ux = dx / distance
            uy = dy / distance

            # Component of source velocity toward observer (dot product)
            relative_velocity = self.source_velocity_x * ux + self.source_velocity_y * uy

            # Apply Doppler formula: f' = f * (v_sound) / (v_sound - v_source)
            denominator = SOUND_SPEED - relative_velocity
            if abs(denominator) > 0.1:  # Avoid division by zero
                self.observed_frequency = BASE_FREQUENCY * SOUND_SPEED / denominator
            else:
                self.observed_frequency = BASE_FREQUENCY * 10  # Very high frequency

            # Clamp to reasonable range
            self.observed_frequency = max(100, min(1000, self.observed_frequency))
        else:
            self.observed_frequency = BASE_FREQUENCY

    def update_sound(self, current_time):
        if self.sound_enabled and current_time - self.last_sound_update > self.sound_update_interval:
            # Stop current sound and start new one with updated frequency
            self.sound_generator.stop()
            self.sound_generator.update_frequency(self.observed_frequency)
            self.current_sound = self.sound_generator.play_continuous_tone()
            self.last_sound_update = current_time

    def emit_wave(self, current_time):
        if current_time - self.last_wave_time >= self.wave_interval:
            self.waves.append(SoundWave(self.source_x, self.source_y, current_time))
            self.last_wave_time = current_time

    def update_waves(self, current_time):
        # Update existing waves
        for wave in self.waves[:]:
            wave.update(current_time)
            if not wave.is_alive(current_time):
                self.waves.remove(wave)

    def draw_info(self):
        # Instructions
        instructions = [
            "Interactive Doppler Effect Visualization",
            "Move your mouse to control the sound source!",
            "",
            "Red circle: Sound source (follows cursor)",
            "Green circle: Observer (stationary)",
            "Blue rings: Sound waves",
            "",
            f"Base frequency: {BASE_FREQUENCY:.1f} Hz",
            f"Observed frequency: {self.observed_frequency:.1f} Hz",
            f"Source speed: {math.sqrt(self.source_velocity_x ** 2 + self.source_velocity_y ** 2):.1f} px/s",
            "",
            "Controls:",
            "S - Toggle sound on/off",
            "R - Reset observer position",
            "ESC - Exit",
        ]

        y_offset = 10
        for line in instructions:
            if line:  # Skip empty lines
                text = self.small_font.render(line, True, TEXT_COLOR)
                self.screen.blit(text, (10, y_offset))
            y_offset += 18

        # Show sound status
        sound_status = "Sound: ON" if self.sound_enabled else "Sound: OFF"
        sound_color = (100, 255, 100) if self.sound_enabled else (255, 100, 100)
        sound_surface = self.font.render(sound_status, True, sound_color)
        self.screen.blit(sound_surface, (10, HEIGHT - 60))

        # Show Doppler effect explanation
        freq_diff = self.observed_frequency - BASE_FREQUENCY
        if freq_diff > 10:
            effect_text = f"Higher pitch (+{freq_diff:.1f} Hz)"
            color = (255, 150, 150)
        elif freq_diff < -10:
            effect_text = f"Lower pitch ({freq_diff:.1f} Hz)"
            color = (150, 150, 255)
        else:
            effect_text = "Normal pitch"
            color = TEXT_COLOR

        effect_surface = self.font.render(effect_text, True, color)
        self.screen.blit(effect_surface, (10, HEIGHT - 30))

    def draw(self, current_time):
        self.screen.fill(BACKGROUND_COLOR)

        # Draw waves
        for wave in self.waves:
            wave.draw(self.screen, current_time)

        # Draw line between source and observer
        pygame.draw.line(self.screen, (80, 80, 80),
                         (int(self.source_x), int(self.source_y)),
                         (int(self.observer_x), int(self.observer_y)), 1)

        # Draw distance text
        distance = math.sqrt((self.observer_x - self.source_x) ** 2 + (self.observer_y - self.source_y) ** 2)
        dist_text = f"{distance:.0f}px"
        text_surface = self.small_font.render(dist_text, True, (150, 150, 150))
        mid_x = (self.source_x + self.observer_x) // 2
        mid_y = (self.source_y + self.observer_y) // 2
        self.screen.blit(text_surface, (mid_x - 20, mid_y - 20))

        # Draw source (follows cursor)
        pygame.draw.circle(self.screen, SOURCE_COLOR,
                           (int(self.source_x), int(self.source_y)), 15)
        pygame.draw.circle(self.screen, (255, 255, 255),
                           (int(self.source_x), int(self.source_y)), 15, 2)

        # Draw velocity vector
        if math.sqrt(self.source_velocity_x ** 2 + self.source_velocity_y ** 2) > 10:
            end_x = self.source_x + self.source_velocity_x * 0.1
            end_y = self.source_y + self.source_velocity_y * 0.1
            pygame.draw.line(self.screen, (255, 200, 100),
                             (int(self.source_x), int(self.source_y)),
                             (int(end_x), int(end_y)), 3)

        # Draw observer (stationary)
        pygame.draw.circle(self.screen, OBSERVER_COLOR,
                           (int(self.observer_x), int(self.observer_y)), 12)
        pygame.draw.circle(self.screen, (255, 255, 255),
                           (int(self.observer_x), int(self.observer_y)), 12, 2)

        # Draw info
        self.draw_info()

        pygame.display.flip()

    def run(self):
        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            current_time = pygame.time.get_ticks()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_s:
                        # Toggle sound
                        self.sound_enabled = not self.sound_enabled
                        if not self.sound_enabled:
                            self.sound_generator.stop()
                    elif event.key == pygame.K_r:
                        # Reset observer position
                        self.observer_x = WIDTH - 150
                        self.observer_y = HEIGHT // 2
                    elif event.key == pygame.K_SPACE:
                        # Reset simulation
                        self.waves.clear()
                        self.sound_generator.stop()

            # Update simulation
            self.update_source_position(dt)
            self.calculate_observed_frequency()
            self.update_sound(current_time)
            self.emit_wave(current_time)
            self.update_waves(current_time)

            # Draw everything
            self.draw(current_time)

        # Cleanup
        self.sound_generator.stop()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    simulation = DopplerSimulation()
    simulation.run()
