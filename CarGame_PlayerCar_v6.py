import pygame
import math


# Constants for Car
CAR_IMAGE_PATH = 'assets/images/car_1.png'
CAR_SCALE_FACTOR = 0.2  # Adjust this to scale the car image appropriately
# Car physics constants (world units)
CAR_MAX_SPEED_FORWARD = 5.0  # world units / sec
CAR_MAX_SPEED_REVERSE = 1.0  # world units / sec
CAR_ACCELERATION = 3.0  # world units / sec^2
CAR_DECELERATION = 2.0  # world units / sec^2 (natural drag when not accelerating)
CAR_BRAKE_DECELERATION = 10.0  # world units / sec^2
CAR_MIN_SPEED_FOR_STEERING = 0.5  # world units / sec (absolute speed)

CAR_MAX_ROTATION_SPEED = 120.0  # degrees / sec
CAR_ROTATION_ACCELERATION = 200.0  # degrees / sec^2
CAR_ROTATION_DECELERATION = 300.0  # degrees / sec^2 (natural drag for steering wheel centering)
CAR_BRAKE_ROTATION_DECELERATION = 400.0  # degrees/sec^2 (rate at which angular speed reduces when braking)


class Car:
    def __init__(self, world_x, world_y):
        self.world_x = float(world_x)
        self.world_y = float(world_y)

        # Load and scale the original car image
        try:
            unscaled_image = pygame.image.load(
                CAR_IMAGE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Error loading car image: {CAR_IMAGE_PATH}")
            raise SystemExit(e)

        width = int(unscaled_image.get_width() * CAR_SCALE_FACTOR)
        height = int(unscaled_image.get_height() * CAR_SCALE_FACTOR)
        self.image_original = pygame.transform.scale(unscaled_image,
                                                     (width, height))

        self.image = self.image_original  # Current image to draw (rotated)
        # Initialize rect. Its position will be updated by update_screen_rect() or draw().
        self.rect = self.image.get_rect()

        # Car's state
        self.angle = 0.0  # Degrees. 0 = facing screen top. Positive angle for clockwise.
        self.velocity = 0.0  # world units / sec (positive for forward, negative for reverse)
        self.angular_velocity = 0.0  # degrees / sec (positive for clockwise)

    def _decelerate_value(self, value, rate, delta_time):
        """Helper to decelerate a numeric value towards zero."""
        if value == 0:
            return 0.0

        sign = 1.0 if value > 0 else -1.0
        magnitude_change = rate * delta_time

        new_value = value - sign * magnitude_change
        if (sign == 1.0 and new_value < 0) or (
                sign == -1.0 and new_value > 0):
            return 0.0
        return new_value

    def update_screen_rect(self, camera_world_y, world_unit_scale):
        """
        Updates self.rect to reflect the car's current screen position and rotation.
        This should be called after self.update() if game logic needs the screen rect.
        The self.image (rotated) must be up-to-date before calling this.
        """
        # self.image is updated at the end of self.update()
        screen_center_x = round(self.world_x * world_unit_scale)
        screen_center_y = round(
            (self.world_y - camera_world_y) * world_unit_scale)
        # Get rect for the *current* (potentially rotated) image
        self.rect = self.image.get_rect(
            center=(screen_center_x, screen_center_y))

    def update(self, delta_time, keys_pressed):
        # --- Braking ---
        is_braking = keys_pressed[pygame.K_LSHIFT] or keys_pressed[
            pygame.K_RSHIFT]

        if is_braking:
            self.velocity = self._decelerate_value(self.velocity,
                                                   CAR_BRAKE_DECELERATION,
                                                   delta_time)
            self.angular_velocity = self._decelerate_value(
                self.angular_velocity,
                CAR_BRAKE_ROTATION_DECELERATION, delta_time)
        else:
            # --- Acceleration / Deceleration (Forward/Backward) ---
            is_accelerating_forward = keys_pressed[pygame.K_w]
            is_accelerating_reverse = keys_pressed[pygame.K_s]

            if is_accelerating_forward:
                self.velocity += CAR_ACCELERATION * delta_time
                self.velocity = min(self.velocity,
                                    CAR_MAX_SPEED_FORWARD)
            elif is_accelerating_reverse:
                self.velocity -= CAR_ACCELERATION * delta_time
                self.velocity = max(self.velocity,
                                    -CAR_MAX_SPEED_REVERSE)
            else:
                self.velocity = self._decelerate_value(self.velocity,
                                                       CAR_DECELERATION,
                                                       delta_time)

            # --- Steering (Rotation) ---
            can_steer = abs(
                self.velocity) >= CAR_MIN_SPEED_FOR_STEERING

            is_steering_left = keys_pressed[pygame.K_a]
            is_steering_right = keys_pressed[pygame.K_d]

            if can_steer:
                if is_steering_left:  # Anticlockwise
                    self.angular_velocity -= CAR_ROTATION_ACCELERATION * delta_time
                    self.angular_velocity = max(self.angular_velocity,
                                                -CAR_MAX_ROTATION_SPEED)
                elif is_steering_right:  # Clockwise
                    self.angular_velocity += CAR_ROTATION_ACCELERATION * delta_time
                    self.angular_velocity = min(self.angular_velocity,
                                                CAR_MAX_ROTATION_SPEED)
                else:
                    self.angular_velocity = self._decelerate_value(
                        self.angular_velocity,
                        CAR_ROTATION_DECELERATION, delta_time)
            else:
                self.angular_velocity = self._decelerate_value(
                    self.angular_velocity, CAR_ROTATION_DECELERATION,
                    delta_time)

        # --- Update position and angle based on velocities ---
        self.angle += self.angular_velocity * delta_time
        self.angle %= 360

        angle_rad = math.radians(self.angle)
        self.world_x += math.sin(
            angle_rad) * self.velocity * delta_time
        self.world_y -= math.cos(
            angle_rad) * self.velocity * delta_time

        # Update the display image (rotation)
        # pygame.transform.rotozoom rotates CCW. Our angle is CW positive, so pass -angle.
        self.image = pygame.transform.rotozoom(self.image_original,
                                               -self.angle, 1.0)
        # self.rect is NOT directly updated here anymore.
        # It's updated by update_screen_rect() when needed for game logic,
        # or by draw() for rendering.

    def draw(self, surface, camera_world_y, world_unit_scale):
        # Ensure self.rect is up-to-date for drawing, based on the current self.image.
        # This calculation is the same as in update_screen_rect().
        screen_center_x = round(self.world_x * world_unit_scale)
        screen_center_y = round(
            (self.world_y - camera_world_y) * world_unit_scale)
        self.rect = self.image.get_rect(
            center=(screen_center_x, screen_center_y))

        surface.blit(self.image, self.rect.topleft)