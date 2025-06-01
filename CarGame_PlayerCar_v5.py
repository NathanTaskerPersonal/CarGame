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
        self.rect = self.image.get_rect()  # Screen rect, center updated in draw method

        # Car's state
        self.angle = 0.0  # Degrees. 0 = facing screen top (along negative Y in typical math coords).
        # Positive angle for clockwise rotation.
        self.velocity = 0.0  # world units / sec (positive for forward, negative for reverse)
        self.angular_velocity = 0.0  # degrees / sec (positive for clockwise)

    def _decelerate_value(self, value, rate, delta_time):
        """Helper to decelerate a numeric value towards zero."""
        if value == 0:
            return 0.0

        sign = 1.0 if value > 0 else -1.0
        magnitude_change = rate * delta_time

        new_value = value - sign * magnitude_change
        # Check if deceleration caused the value to overshoot zero
        if (sign == 1.0 and new_value < 0) or (
                sign == -1.0 and new_value > 0):
            return 0.0
        return new_value

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
            # When braking, ignore other movement input for acceleration/steering
        else:
            # --- Acceleration / Deceleration (Forward/Backward) ---
            is_accelerating_forward = keys_pressed[pygame.K_w]
            is_accelerating_reverse = keys_pressed[pygame.K_s]

            if is_accelerating_forward:
                self.velocity += CAR_ACCELERATION * delta_time
                self.velocity = min(self.velocity,
                                    CAR_MAX_SPEED_FORWARD)
            elif is_accelerating_reverse:
                self.velocity -= CAR_ACCELERATION * delta_time  # Using same accel rate for simplicity
                self.velocity = max(self.velocity,
                                    -CAR_MAX_SPEED_REVERSE)
            else:
                # Natural deceleration if no acceleration input
                self.velocity = self._decelerate_value(self.velocity,
                                                       CAR_DECELERATION,
                                                       delta_time)

            # --- Steering (Rotation) ---
            # Steering is allowed if the car is moving above a minimum speed.
            # "if car is stationary, steering doesn't work."
            # "when steering, if not already, forward velocity must accelerate above a minimum value"
            # This implies that to start steering from stationary, you need to accelerate (W/S)
            # until min_speed is reached.
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
                    # Natural angular deceleration (steering wheel centering effect)
                    self.angular_velocity = self._decelerate_value(
                        self.angular_velocity,
                        CAR_ROTATION_DECELERATION, delta_time)
            else:
                # If can't steer (too slow or stationary), angular velocity naturally decelerates
                self.angular_velocity = self._decelerate_value(
                    self.angular_velocity, CAR_ROTATION_DECELERATION,
                    delta_time)

        # --- Update position and angle based on velocities ---
        self.angle += self.angular_velocity * delta_time
        self.angle %= 360  # Normalize angle to 0-359 degrees

        # Movement vector based on angle.
        # Angle: 0 degrees = car's nose points towards top of screen (negative Y in world if Y grows down).
        # math.sin/cos expect radians.
        angle_rad = math.radians(self.angle)

        # dx = sin(angle) * velocity (if angle 0 is right)
        # dy = cos(angle) * velocity (if angle 0 is right, Y positive up)
        # For 0 = UP: dx = sin(angle) * vel; dy = -cos(angle) * vel (Pygame Y is positive down)
        self.world_x += math.sin(
            angle_rad) * self.velocity * delta_time
        self.world_y -= math.cos(
            angle_rad) * self.velocity * delta_time

        # Update the display image (rotation)
        # pygame.transform.rotozoom rotates CCW. If our angle is CW positive, pass -angle.
        self.image = pygame.transform.rotozoom(self.image_original,
                                               -self.angle, 1.0)
        # The self.rect will be updated with screen coordinates in the draw() method.

    def draw(self, surface, camera_world_y, world_unit_scale):
        # Convert car's world coordinates to screen coordinates
        # Explicitly round to nearest int for screen coordinates
        screen_center_x = round(self.world_x * world_unit_scale)
        screen_center_y = round(
            (self.world_y - camera_world_y) * world_unit_scale)

        # Update the car's screen rectangle position for blitting
        self.rect = self.image.get_rect(
            center=(screen_center_x, screen_center_y))

        surface.blit(self.image, self.rect.topleft)