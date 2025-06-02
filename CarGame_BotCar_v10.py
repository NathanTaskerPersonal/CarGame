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
# Max sideways distance for sine steering
SINE_STEER_MAX_AMPLITUDE_WORLD = 1.5
# Max sideways drift per second for simple curve
CURVE_STEER_MAX_RATE_WORLD_PER_SEC = 0.3
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
        self.angle_visual = 0.0  # For visual rotation

        image_path = random.choice(BOT_CAR_IMAGE_PATHS)
        scale_multiplier = random.uniform(
            MIN_BOT_SCALE_FACTOR_REL, MAX_BOT_SCALE_FACTOR_REL
        )
        self.current_scale_factor = (
            base_player_scale_factor * scale_multiplier
        )

        try:
            self.image_unrotated_original = pygame.image.load(
                image_path
            ).convert_alpha()
        except pygame.error as e:
            print(
                f"Error loading bot car image: {image_path}, "
                "using fallback."
            )
            self.image_unrotated_original = pygame.Surface((50, 100))
            self.image_unrotated_original.fill(pygame.Color("purple"))
            self.current_scale_factor = base_player_scale_factor

        img_w = self.image_unrotated_original.get_width()
        img_h = self.image_unrotated_original.get_height()
        width = int(img_w * self.current_scale_factor)
        height = int(img_h * self.current_scale_factor)

        self.image_original_scaled = pygame.transform.scale(
            self.image_unrotated_original, (width, height)
        )
        self.image = self.image_original_scaled  # Current image to draw

        self.image_rect = self.image.get_rect()
        # Note: The scale factor for collision rect is hardcoded here
        self.bot_collision_rect_scale_factor = 0.75
        self.collision_rect = self.image_rect.copy()
        # Initial call to _update_collision_rect_from_image_rect
        # might be redundant as update_screen_rects will be called
        # before first collision check. However, good for completeness
        # if rect is accessed before first update_screen_rects.
        self._update_collision_rect_from_image_rect()

        self.movement_type = random.choice([
            'straight_slow', 'straight_medium', 'straight_fast',
            'sine_speed', 'sine_steer_gentle', 'sine_steer_moderate',
            'curve_left', 'curve_right', 'donut'
        ])

        self.base_y_velocity_world = 0.0
        self.current_y_velocity_world = 0.0
        self.current_x_velocity_world = 0.0

        self.time_alive = 0.0
        self.sine_freq = random.uniform(0.3, 1.5)
        self.sine_amp_speed_factor = 0.0
        self.sine_amp_steer_world = 0.0
        self.curve_steer_rate_world = 0.0

        self.donut_center_x_world = self.world_x
        self.donut_center_y_world = self.world_y
        self.donut_radius_world = 0
        self.donut_angular_speed = 0
        self.donut_current_angle = random.uniform(0, 2 * math.pi)
        self.donut_drift_y_speed_world = 0

        max_bot_abs_speed_world = (
            player_max_speed_world * MAX_BOT_SPEED_FACTOR
        )
        min_bot_abs_speed_world = (
            player_max_speed_world * MIN_BOT_SPEED_FACTOR
        )

        if 'straight' in self.movement_type:
            if 'slow' in self.movement_type:
                min_s = min_bot_abs_speed_world
                max_s = max_bot_abs_speed_world * 0.33
                self.base_y_velocity_world = random.uniform(min_s, max_s)
            elif 'medium' in self.movement_type:
                min_s = max_bot_abs_speed_world * 0.33
                max_s = max_bot_abs_speed_world * 0.66
                self.base_y_velocity_world = random.uniform(min_s, max_s)
            else:  # fast
                min_s = max_bot_abs_speed_world * 0.66
                max_s = max_bot_abs_speed_world
                self.base_y_velocity_world = random.uniform(min_s, max_s)
        elif self.movement_type == 'sine_speed':
            min_s = min_bot_abs_speed_world
            max_s = max_bot_abs_speed_world * 0.7
            self.base_y_velocity_world = random.uniform(min_s, max_s)
            self.sine_amp_speed_factor = random.uniform(0.4, 0.9)
        elif 'sine_steer' in self.movement_type:
            min_s = min_bot_abs_speed_world
            max_s = max_bot_abs_speed_world * 0.8
            self.base_y_velocity_world = random.uniform(min_s, max_s)
            amp_factor = 0.3 if 'gentle' in self.movement_type else 0.7
            self.sine_amp_steer_world = (
                SINE_STEER_MAX_AMPLITUDE_WORLD * amp_factor
            )
            min_off = -screen_width_world * 0.1
            max_off = screen_width_world * 0.1
            rand_offset = random.uniform(min_off, max_off)
            self.initial_world_x = (
                screen_width_world / 2 + rand_offset
            )
            self.world_x = self.initial_world_x
        elif 'curve' in self.movement_type:
            min_s = min_bot_abs_speed_world
            max_s = max_bot_abs_speed_world * 0.75
            self.base_y_velocity_world = random.uniform(min_s, max_s)
            rate_factor = random.uniform(0.5, 1.0)
            self.curve_steer_rate_world = (
                CURVE_STEER_MAX_RATE_WORLD_PER_SEC * rate_factor
            )
            if 'left' in self.movement_type:
                self.curve_steer_rate_world *= -1
            min_off = -screen_width_world * 0.2
            max_off = screen_width_world * 0.2
            rand_offset = random.uniform(min_off, max_off)
            self.world_x = screen_width_world / 2 + rand_offset
        elif self.movement_type == 'donut':
            min_drift = min_bot_abs_speed_world * 0.5
            max_drift = max_bot_abs_speed_world * 0.5
            self.donut_drift_y_speed_world = random.uniform(
                min_drift, max_drift
            )
            self.base_y_velocity_world = self.donut_drift_y_speed_world
            self.donut_radius_world = random.uniform(
                DONUT_RADIUS_WORLD_MIN, DONUT_RADIUS_WORLD_MAX
            )
            self.donut_angular_speed = random.uniform(
                DONUT_ANGULAR_SPEED_RAD_PER_SEC_MIN,
                DONUT_ANGULAR_SPEED_RAD_PER_SEC_MAX
            )
            if random.choice([True, False]):
                self.donut_angular_speed *= -1

            min_off = -screen_width_world * 0.15
            max_off = screen_width_world * 0.15
            rand_offset = random.uniform(min_off, max_off)
            self.donut_center_x_world = (
                screen_width_world / 2 + rand_offset
            )
            cos_angle = math.cos(self.donut_current_angle)
            self.world_x = (
                self.donut_center_x_world +
                self.donut_radius_world * cos_angle
            )
            self.initial_world_y = world_y
            self.donut_center_y_world = self.initial_world_y

        self.current_y_velocity_world = self.base_y_velocity_world
        self.passed_by_player = False

    def _update_collision_rect_from_image_rect(self):
        # This method uses self.image_rect (already positioned)
        # and self.bot_collision_rect_scale_factor.
        new_width = int(
            self.image_rect.width *
            self.bot_collision_rect_scale_factor
        )
        new_height = int(
            self.image_rect.height *
            self.bot_collision_rect_scale_factor
        )
        self.collision_rect.width = new_width
        self.collision_rect.height = new_height
        # Correctly use the positioned image_rect's center
        self.collision_rect.center = self.image_rect.center

    def update_screen_rects(self, camera_world_y):
        screen_center_x = round(self.world_x * self.world_unit_scale)
        screen_center_y = round(
            (self.world_y - camera_world_y) * self.world_unit_scale
        )

        # Update image_rect using the center of the current
        # (possibly rotated) image
        self.image_rect = self.image.get_rect(
            center=(screen_center_x, screen_center_y)
        )

        # Now that image_rect is correctly positioned,
        # update collision_rect based on it.
        self._update_collision_rect_from_image_rect()

    def update(self, delta_time):
        self.time_alive += delta_time
        self.current_y_velocity_world = self.base_y_velocity_world

        previous_world_x = self.world_x
        previous_world_y = self.world_y

        if self.movement_type == 'sine_speed':
            speed_factor = (
                self.base_y_velocity_world *
                self.sine_amp_speed_factor
            )
            sine_val = math.sin(self.sine_freq * self.time_alive)
            speed_offset = speed_factor * sine_val
            self.current_y_velocity_world = (
                self.base_y_velocity_world + speed_offset
            )
            self.current_y_velocity_world = max(
                0, self.current_y_velocity_world
            )
        elif 'sine_steer' in self.movement_type:
            sine_val_steer = math.sin(self.sine_freq * self.time_alive)
            self.world_x = (
                self.initial_world_x +
                self.sine_amp_steer_world * sine_val_steer
            )
        elif 'curve' in self.movement_type:
            self.world_x += self.curve_steer_rate_world * delta_time
        elif self.movement_type == 'donut':
            self.donut_current_angle += (
                self.donut_angular_speed * delta_time
            )
            self.donut_center_y_world += (
                self.donut_drift_y_speed_world * delta_time
            )
            cos_angle = math.cos(self.donut_current_angle)
            sin_angle = math.sin(self.donut_current_angle)
            self.world_x = (
                self.donut_center_x_world +
                self.donut_radius_world * cos_angle
            )
            self.world_y = (
                self.donut_center_y_world +
                self.donut_radius_world * sin_angle
            )
            self.current_y_velocity_world = (
                self.donut_drift_y_speed_world
            )

        if self.movement_type != 'donut':
            self.world_y += (
                self.current_y_velocity_world * delta_time
            )

        dx = self.world_x - previous_world_x
        dy = self.world_y - previous_world_y

        if abs(dx) > 0.001 or abs(dy) > 0.001:
            angle_from_up_rad = math.atan2(dx, -dy)
            self.angle_visual = math.degrees(angle_from_up_rad)

        self.image = pygame.transform.rotozoom(
            self.image_original_scaled, -self.angle_visual, 1.0
        )

    def draw(self, surface, camera_world_y):
        self.update_screen_rects(camera_world_y)
        if (self.image_rect.bottom > 0 and
                self.image_rect.top < surface.get_height()):
            surface.blit(self.image, self.image_rect.topleft)
            # Debug collision
            # pygame.draw.rect(surface, (0,0,255),
            #                  self.collision_rect, 1)
