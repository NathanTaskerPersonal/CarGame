import pygame
import math
import random

BOT_CAR_IMAGE_PATHS = [
    'assets/images/car_2.png', 'assets/images/car_3.png',
    'assets/images/car_4.png', 'assets/images/car_5.png',
    'assets/images/car_6.png',
]

MAX_BOT_SPEED_FACTOR = 0.90  # Can be a bit faster now
MIN_BOT_SPEED_FACTOR = 0.2  # Minimum forward speed if moving

MIN_BOT_SCALE_FACTOR_REL = 0.9
MAX_BOT_SCALE_FACTOR_REL = 1.1

# Movement behavior parameters
SINE_STEER_MAX_AMPLITUDE_WORLD = 1.5  # Max sideways distance for sine steering
CURVE_STEER_MAX_RATE_WORLD_PER_SEC = 0.3  # Max sideways drift per second for simple curve
DONUT_RADIUS_WORLD_MIN = 0.5
DONUT_RADIUS_WORLD_MAX = 1.5
DONUT_ANGULAR_SPEED_RAD_PER_SEC_MIN = math.pi / 2  # 90 deg/sec
DONUT_ANGULAR_SPEED_RAD_PER_SEC_MAX = math.pi  # 180 deg/sec


class BotCar:
    def __init__(self, world_x, world_y, world_unit_scale,
                 player_max_speed_world, base_player_scale_factor,
                 screen_width_world):
        self.world_x = float(world_x)
        self.world_y = float(world_y)
        self.initial_world_x = self.world_x  # Store for relative movements
        self.initial_world_y = self.world_y
        self.world_unit_scale = world_unit_scale
        self.angle_visual = 0.0  # For visual rotation if doing donuts/curves

        image_path = random.choice(BOT_CAR_IMAGE_PATHS)
        scale_multiplier = random.uniform(MIN_BOT_SCALE_FACTOR_REL,
                                          MAX_BOT_SCALE_FACTOR_REL)
        self.current_scale_factor = base_player_scale_factor * scale_multiplier

        try:
            self.image_unrotated_original = pygame.image.load(
                image_path).convert_alpha()
        except pygame.error as e:
            print(
                f"Error loading bot car image: {image_path}, using fallback.")
            self.image_unrotated_original = pygame.Surface((50, 100))
            self.image_unrotated_original.fill(pygame.Color("purple"))
            self.current_scale_factor = base_player_scale_factor

        width = int(
            self.image_unrotated_original.get_width() * self.current_scale_factor)
        height = int(
            self.image_unrotated_original.get_height() * self.current_scale_factor)
        self.image_original_scaled = pygame.transform.scale(
            self.image_unrotated_original, (width, height))
        self.image = self.image_original_scaled  # Current image to draw

        self.image_rect = self.image.get_rect()
        bot_collision_rect_scale = 0.75  # Adjusted for potentially better feel
        self.collision_rect = self.image_rect.copy()
        self._update_collision_rect_from_image_rect(
            bot_collision_rect_scale)

        self.movement_type = random.choice([
            'straight_slow', 'straight_medium', 'straight_fast',
            'sine_speed', 'sine_steer_gentle', 'sine_steer_moderate',
            'curve_left', 'curve_right', 'donut'
        ])

        # Ensure bots generally move "down" the screen or are slow enough to be passed
        self.base_y_velocity_world = 0.0
        self.current_y_velocity_world = 0.0
        self.current_x_velocity_world = 0.0  # For direct X velocity if needed

        self.time_alive = 0.0
        self.sine_freq = random.uniform(0.3,
                                        1.5)  # Adjusted frequency range
        self.sine_amp_speed_factor = 0.0  # Factor of base_y_velocity
        self.sine_amp_steer_world = 0.0  # Sideways amplitude

        self.curve_steer_rate_world = 0.0  # Sideways drift for curving

        # Donut specific
        self.donut_center_x_world = self.world_x
        self.donut_center_y_world = self.world_y  # Donut center will also drift down
        self.donut_radius_world = 0
        self.donut_angular_speed = 0  # rad/s
        self.donut_current_angle = random.uniform(0,
                                                  2 * math.pi)  # Start at random point in circle
        self.donut_drift_y_speed_world = 0

        max_bot_abs_speed_world = player_max_speed_world * MAX_BOT_SPEED_FACTOR
        min_bot_abs_speed_world = player_max_speed_world * MIN_BOT_SPEED_FACTOR

        if 'straight' in self.movement_type:
            if 'slow' in self.movement_type:
                self.base_y_velocity_world = random.uniform(
                    min_bot_abs_speed_world,
                    max_bot_abs_speed_world * 0.33)
            elif 'medium' in self.movement_type:
                self.base_y_velocity_world = random.uniform(
                    max_bot_abs_speed_world * 0.33,
                    max_bot_abs_speed_world * 0.66)
            else:  # fast
                self.base_y_velocity_world = random.uniform(
                    max_bot_abs_speed_world * 0.66,
                    max_bot_abs_speed_world)
        elif self.movement_type == 'sine_speed':
            self.base_y_velocity_world = random.uniform(
                min_bot_abs_speed_world,
                max_bot_abs_speed_world * 0.7)
            self.sine_amp_speed_factor = random.uniform(0.4,
                                                        0.9)  # Speed variation
        elif 'sine_steer' in self.movement_type:
            self.base_y_velocity_world = random.uniform(
                min_bot_abs_speed_world,
                max_bot_abs_speed_world * 0.8)
            amplitude_factor = 0.3 if 'gentle' in self.movement_type else 0.7
            self.sine_amp_steer_world = SINE_STEER_MAX_AMPLITUDE_WORLD * amplitude_factor
            # Ensure spawn X is near center for sine steerers
            self.initial_world_x = screen_width_world / 2 + random.uniform(
                -screen_width_world * 0.1, screen_width_world * 0.1)
            self.world_x = self.initial_world_x
        elif 'curve' in self.movement_type:
            self.base_y_velocity_world = random.uniform(
                min_bot_abs_speed_world,
                max_bot_abs_speed_world * 0.75)
            self.curve_steer_rate_world = CURVE_STEER_MAX_RATE_WORLD_PER_SEC * random.uniform(
                0.5, 1.0)
            if 'left' in self.movement_type:
                self.curve_steer_rate_world *= -1
            # Spawn curvers more centrally
            self.world_x = screen_width_world / 2 + random.uniform(
                -screen_width_world * 0.2, screen_width_world * 0.2)
        elif self.movement_type == 'donut':
            self.donut_drift_y_speed_world = random.uniform(
                min_bot_abs_speed_world * 0.5,
                max_bot_abs_speed_world * 0.5)  # Slow overall downward drift
            self.base_y_velocity_world = self.donut_drift_y_speed_world  # For y movement of donut center
            self.donut_radius_world = random.uniform(
                DONUT_RADIUS_WORLD_MIN, DONUT_RADIUS_WORLD_MAX)
            self.donut_angular_speed = random.uniform(
                DONUT_ANGULAR_SPEED_RAD_PER_SEC_MIN,
                DONUT_ANGULAR_SPEED_RAD_PER_SEC_MAX)
            if random.choice([True,
                              False]): self.donut_angular_speed *= -1  # Random direction
            # Spawn donuts near center
            self.donut_center_x_world = screen_width_world / 2 + random.uniform(
                -screen_width_world * 0.15, screen_width_world * 0.15)
            self.world_x = self.donut_center_x_world + self.donut_radius_world * math.cos(
                self.donut_current_angle)
            self.initial_world_y = world_y  # Donut Y center starts where spawned
            self.donut_center_y_world = self.initial_world_y

        self.current_y_velocity_world = self.base_y_velocity_world
        self.passed_by_player = False

    def _update_collision_rect_from_image_rect(self, scale_factor):
        # Use the current (potentially rotated) image's rect for dimensions
        ref_rect = self.image.get_rect()  # Get rect of the current self.image
        new_width = int(ref_rect.width * scale_factor)
        new_height = int(ref_rect.height * scale_factor)
        self.collision_rect.width = new_width
        self.collision_rect.height = new_height
        self.collision_rect.center = ref_rect.center

    def update_screen_rects(self, camera_world_y):
        screen_center_x = round(self.world_x * self.world_unit_scale)
        screen_center_y = round(
            (self.world_y - camera_world_y) * self.world_unit_scale)

        # Update image_rect using the center of the current (possibly rotated) image
        self.image_rect = self.image.get_rect(
            center=(screen_center_x, screen_center_y))

        # Update collision_rect based on the new image_rect
        # self.image is already rotated, so image_rect has correct rotated bounds
        # self.collision_rect center should align with image_rect.center
        self._update_collision_rect_from_image_rect(
            0.75)  # Use the defined scale factor

    def update(self, delta_time):
        self.time_alive += delta_time
        self.current_y_velocity_world = self.base_y_velocity_world  # Start with base

        # Visual angle update for donuts/curves
        previous_world_x = self.world_x
        previous_world_y = self.world_y

        if self.movement_type == 'sine_speed':
            speed_offset = (
                                       self.base_y_velocity_world * self.sine_amp_speed_factor) * math.sin(
                self.sine_freq * self.time_alive)
            self.current_y_velocity_world = self.base_y_velocity_world + speed_offset
            self.current_y_velocity_world = max(0,
                                                self.current_y_velocity_world)  # No reversing
        elif 'sine_steer' in self.movement_type:
            self.world_x = self.initial_world_x + self.sine_amp_steer_world * math.sin(
                self.sine_freq * self.time_alive)
        elif 'curve' in self.movement_type:
            self.world_x += self.curve_steer_rate_world * delta_time
        elif self.movement_type == 'donut':
            self.donut_current_angle += self.donut_angular_speed * delta_time
            self.donut_center_y_world += self.donut_drift_y_speed_world * delta_time  # Donut formation drifts down

            self.world_x = self.donut_center_x_world + self.donut_radius_world * math.cos(
                self.donut_current_angle)
            self.world_y = self.donut_center_y_world + self.donut_radius_world * math.sin(
                self.donut_current_angle)
            self.current_y_velocity_world = self.donut_drift_y_speed_world  # This is for the center; individual points vary

        # For all non-donut types, apply Y velocity (donut Y is set directly)
        if self.movement_type != 'donut':
            self.world_y += self.current_y_velocity_world * delta_time

        # --- Visual Rotation ---
        dx = self.world_x - previous_world_x
        dy = self.world_y - previous_world_y  # Positive dy means moving "down"

        if abs(dx) > 0.001 or abs(dy) > 0.001:  # If moving
            # Angle of movement vector (0 is right, positive is CCW for atan2)
            # Pygame's Y is inverted, so dy needs to be negated for standard math angle
            movement_angle_rad = math.atan2(-dy, dx)
            # Convert to degrees, 0 facing right. We want 0 facing up.
            # Sprite is drawn facing up (0 degrees in Pygame usually top).
            # rotozoom rotates CCW.
            # If sprite is designed facing UP: angle for rotozoom = -degrees_from_up_vector_CW
            # Angle from UP vector (0, -1) to (dx, dy)
            # target_angle_deg = math.degrees(math.atan2(dx, -dy)) # dx for X, -dy for Y if 0 is UP

            # More direct: angle of (dx, dy) where positive Y is down.
            # Angle from positive Y axis (0,1) to (dx, dy)
            # If car image points UP (0 degrees), and we want it to align with (dx, dy) where dy is positive down:
            target_angle_deg = math.degrees(math.atan2(dx,
                                                       dy))  # atan2(x,y) -> angle from positive Y axis
            self.angle_visual = target_angle_deg  # This angle makes sprite point in (dx,dy) if image faces +Y
            # Our image faces UP (-Y in math). So we need to adjust.
            # Angle relative to UP (0, -1) vector
            # If (dx, dy) is movement vector.
            # Angle to point from (0,-1) to (dx, dy)
            angle_from_up_rad = math.atan2(dx,
                                           -dy)  # -dy because our Y increases downwards
            self.angle_visual = math.degrees(angle_from_up_rad)

        # Apply visual rotation (rotozoom rotates CCW, so pass negative of CW angle)
        self.image = pygame.transform.rotozoom(
            self.image_original_scaled, -self.angle_visual, 1.0)

    def draw(self, surface, camera_world_y):
        self.update_screen_rects(camera_world_y)
        if self.image_rect.bottom > 0 and self.image_rect.top < surface.get_height():
            surface.blit(self.image, self.image_rect.topleft)
            # pygame.draw.rect(surface, (0, 0, 255), self.collision_rect, 1) # Debug collision