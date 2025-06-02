import pygame
import math
import random

# Assuming PlayerCar's constants are accessible or passed if needed for reference
# For now, BotCar will define its own relevant limits.
BOT_CAR_IMAGE_PATHS = [
    'assets/images/car_2.png',
    'assets/images/car_3.png',
    'assets/images/car_4.png',
    'assets/images/car_5.png',
    'assets/images/car_6.png',
]

# Relative to player car's max speed (PLAYER_CAR_MAX_SPEED_FORWARD from PlayerCar module)
MAX_BOT_SPEED_FACTOR = 0.85  # Bots won't exceed 85% of player's max forward speed
MIN_BOT_SPEED_FACTOR = 0.1  # Minimum speed if moving

# Scale variation relative to player's car scale factor
MIN_BOT_SCALE_FACTOR_REL = 0.9
MAX_BOT_SCALE_FACTOR_REL = 1.1


class BotCar:
    def __init__(self, world_x, world_y, world_unit_scale,
                 player_max_speed_world, base_player_scale_factor):
        self.world_x = float(world_x)
        self.world_y = float(world_y)
        self.world_unit_scale = world_unit_scale
        self.angle = 0.0  # Visually always pointing "up" like player car's default

        # --- Randomized Properties ---
        # Image and Scale
        image_path = random.choice(BOT_CAR_IMAGE_PATHS)
        scale_multiplier = random.uniform(MIN_BOT_SCALE_FACTOR_REL,
                                          MAX_BOT_SCALE_FACTOR_REL)
        self.current_scale_factor = base_player_scale_factor * scale_multiplier

        try:
            unscaled_image = pygame.image.load(
                image_path).convert_alpha()
        except pygame.error as e:
            print(f"Error loading bot car image: {image_path}")
            # Fallback to a simple color if image fails
            unscaled_image = pygame.Surface(
                (50, 100))  # Arbitrary size
            unscaled_image.fill(pygame.Color("purple"))
            self.current_scale_factor = base_player_scale_factor  # Use base scale for fallback

        width = int(
            unscaled_image.get_width() * self.current_scale_factor)
        height = int(
            unscaled_image.get_height() * self.current_scale_factor)
        self.image_original = pygame.transform.scale(unscaled_image,
                                                     (width, height))
        self.image = self.image_original  # No rotation needed for image itself if always visually "up"

        self.image_rect = self.image.get_rect()
        # Collision rect scaled similarly to player car, but using its own image_rect
        # For simplicity, let's use a fixed collision scale factor for bots for now.
        # Or, reuse the player's collision scale factor if passed or defined globally.
        bot_collision_rect_scale = 0.80  # Bots might have slightly different effective hitboxes
        self.collision_rect = self.image_rect.copy()
        self._update_collision_rect_from_image_rect(
            bot_collision_rect_scale)

        # Movement Type and Parameters
        self.movement_type = random.choice(
            ['stationary_y', 'straight_down', 'sine_speed_down',
             'sine_steer_down'])

        self.velocity_y_world = 0.0  # Speed along the world's Y-axis (positive is "downwards")
        self.velocity_x_world = 0.0  # Speed along the world's X-axis

        self.time_alive = 0.0
        self.sine_freq = random.uniform(0.5, 2.0)
        self.sine_amp_speed = 0.0
        self.sine_amp_steer_world = 0.0
        self.base_speed_y_world = 0.0

        max_bot_speed_world = player_max_speed_world * MAX_BOT_SPEED_FACTOR
        min_bot_speed_world = player_max_speed_world * MIN_BOT_SPEED_FACTOR

        if self.movement_type == 'stationary_y':
            self.velocity_y_world = 0.0  # Truly stationary in Y
            # Could add slight X drift later if desired
        elif self.movement_type == 'straight_down':
            self.velocity_y_world = random.uniform(
                min_bot_speed_world, max_bot_speed_world)
        elif self.movement_type == 'sine_speed_down':
            self.base_speed_y_world = random.uniform(
                min_bot_speed_world, max_bot_speed_world * 0.7)
            self.sine_amp_speed = self.base_speed_y_world * random.uniform(
                0.3, 0.7)  # Amplitude relative to base
            self.velocity_y_world = self.base_speed_y_world
        elif self.movement_type == 'sine_steer_down':
            self.velocity_y_world = random.uniform(
                min_bot_speed_world, max_bot_speed_world)
            # Sine amplitude for X steering in world units
            self.sine_amp_steer_world = random.uniform(0.5,
                                                       2.0) / self.world_unit_scale  # Small world unit X shift
            self.initial_world_x = self.world_x  # Base for sine steering

        self.passed_by_player = False  # For scoring

    def _update_collision_rect_from_image_rect(self, scale_factor):
        new_width = int(self.image_rect.width * scale_factor)
        new_height = int(self.image_rect.height * scale_factor)
        self.collision_rect.width = new_width
        self.collision_rect.height = new_height
        self.collision_rect.center = self.image_rect.center

    def update_screen_rects(self, camera_world_y):
        screen_center_x = round(self.world_x * self.world_unit_scale)
        screen_center_y = round(
            (self.world_y - camera_world_y) * self.world_unit_scale)

        self.image_rect = self.image.get_rect(
            center=(screen_center_x, screen_center_y))
        # Assuming a fixed collision scale factor for bots defined in __init__ or globally
        bot_collision_rect_scale = 0.80  # Example
        self._update_collision_rect_from_image_rect(
            bot_collision_rect_scale)

    def update(self, delta_time):
        self.time_alive += delta_time

        current_vx = 0.0
        current_vy = self.velocity_y_world  # Base Y velocity

        if self.movement_type == 'sine_speed_down':
            current_vy = self.base_speed_y_world + self.sine_amp_speed * math.sin(
                self.sine_freq * self.time_alive)
            current_vy = max(0,
                             current_vy)  # Ensure doesn't move backwards due to sine

        elif self.movement_type == 'sine_steer_down':
            # Lateral X movement based on sine wave
            self.world_x = self.initial_world_x + self.sine_amp_steer_world * math.sin(
                self.sine_freq * self.time_alive)
            # Y movement is constant for this type
            current_vy = self.velocity_y_world

        # Bots always move "down" the world (Y increases) or are stationary in Y
        self.world_y += current_vy * delta_time
        # X movement only for sine_steer_down for now, or if current_vx was set.

        # No visual rotation needed as image is top-down and angle is fixed at 0
        # self.image remains self.image_original

    def draw(self, surface, camera_world_y):
        self.update_screen_rects(
            camera_world_y)  # Ensure rects are updated before drawing

        # Basic culling for drawing (same as stationary obstacle)
        if self.image_rect.bottom > 0 and self.image_rect.top < surface.get_height():
            surface.blit(self.image, self.image_rect.topleft)

            # --- Optional: Debug draw collision rect for bots ---
            # pygame.draw.rect(surface, (0, 0, 255), self.collision_rect, 1)