import pygame
import math

# Constants for Car (These should be at module level)
CAR_IMAGE_PATH = 'assets/images/car_1.png'
CAR_SCALE_FACTOR = 0.2  # Player's base scale factor
# Player's max forward speed in world units/sec
CAR_MAX_SPEED_FORWARD = 5.0
CAR_MAX_SPEED_REVERSE = 1.0
CAR_ACCELERATION = 3.0
CAR_DECELERATION = 2.0
CAR_BRAKE_DECELERATION = 10.0
CAR_MIN_SPEED_FOR_STEERING = 0.5
CAR_MAX_ROTATION_SPEED = 120.0
CAR_ROTATION_ACCELERATION = 200.0
CAR_ROTATION_DECELERATION = 300.0
CAR_BRAKE_ROTATION_DECELERATION = 400.0
CAR_COLLISION_RECT_SCALE_FACTOR = 0.75


class Car:
    def __init__(self, world_x, world_y):
        self.world_x = float(world_x)
        self.world_y = float(world_y)

        try:
            unscaled_image = pygame.image.load(
                CAR_IMAGE_PATH
            ).convert_alpha()
        except pygame.error as e:
            print(f"Error loading car image: {CAR_IMAGE_PATH}")
            raise SystemExit(e)

        width = int(unscaled_image.get_width() * CAR_SCALE_FACTOR)
        height = int(unscaled_image.get_height() * CAR_SCALE_FACTOR)
        self.image_original = pygame.transform.scale(
            unscaled_image, (width, height)
        )
        self.image = self.image_original

        self.image_rect = self.image.get_rect()
        self.collision_rect = self.image_rect.copy()
        self._update_collision_rect_from_image_rect()

        self.angle = 0.0
        self.velocity = 0.0
        self.angular_velocity = 0.0

    def _decelerate_value(self, value, rate, delta_time):
        if value == 0:
            return 0.0
        sign = 1.0 if value > 0 else -1.0
        magnitude_change = rate * delta_time
        new_value = value - sign * magnitude_change
        if ((sign == 1.0 and new_value < 0) or
                (sign == -1.0 and new_value > 0)):
            return 0.0
        return new_value

    def _update_collision_rect_from_image_rect(self):
        new_width = int(
            self.image_rect.width * CAR_COLLISION_RECT_SCALE_FACTOR
        )
        new_height = int(
            self.image_rect.height * CAR_COLLISION_RECT_SCALE_FACTOR
        )
        self.collision_rect.width = new_width
        self.collision_rect.height = new_height
        self.collision_rect.center = self.image_rect.center

    def update_screen_rects(self, camera_world_y, world_unit_scale):
        screen_center_x = round(self.world_x * world_unit_scale)
        screen_center_y = round(
            (self.world_y - camera_world_y) * world_unit_scale
        )
        self.image_rect = self.image.get_rect(
            center=(screen_center_x, screen_center_y)
        )
        self._update_collision_rect_from_image_rect()

    def update(self, delta_time, keys_pressed):
        is_braking = (keys_pressed[pygame.K_LSHIFT] or
                      keys_pressed[pygame.K_RSHIFT])
        if is_braking:
            self.velocity = self._decelerate_value(
                self.velocity, CAR_BRAKE_DECELERATION, delta_time
            )
            self.angular_velocity = self._decelerate_value(
                self.angular_velocity,
                CAR_BRAKE_ROTATION_DECELERATION, delta_time
            )
        else:
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
                self.velocity = self._decelerate_value(
                    self.velocity, CAR_DECELERATION, delta_time
                )

            can_steer = abs(
                self.velocity
            ) >= CAR_MIN_SPEED_FOR_STEERING
            is_steering_left = keys_pressed[pygame.K_a]
            is_steering_right = keys_pressed[pygame.K_d]
            if can_steer:
                if is_steering_left:
                    self.angular_velocity -= (
                        CAR_ROTATION_ACCELERATION * delta_time
                    )
                    self.angular_velocity = max(
                        self.angular_velocity, -CAR_MAX_ROTATION_SPEED
                    )
                elif is_steering_right:
                    self.angular_velocity += (
                        CAR_ROTATION_ACCELERATION * delta_time
                    )
                    self.angular_velocity = min(
                        self.angular_velocity, CAR_MAX_ROTATION_SPEED
                    )
                else:
                    self.angular_velocity = self._decelerate_value(
                        self.angular_velocity,
                        CAR_ROTATION_DECELERATION, delta_time
                    )
            else:
                self.angular_velocity = self._decelerate_value(
                    self.angular_velocity, CAR_ROTATION_DECELERATION,
                    delta_time
                )

        self.angle += self.angular_velocity * delta_time
        self.angle %= 360
        angle_rad = math.radians(self.angle)
        self.world_x += math.sin(
            angle_rad
        ) * self.velocity * delta_time
        self.world_y -= math.cos(
            angle_rad
        ) * self.velocity * delta_time
        self.image = pygame.transform.rotozoom(
            self.image_original, -self.angle, 1.0
        )

    def draw(self, surface, camera_world_y, world_unit_scale):
        screen_center_x = round(self.world_x * world_unit_scale)
        screen_center_y = round(
            (self.world_y - camera_world_y) * world_unit_scale
        )
        self.image_rect = self.image.get_rect(
            center=(screen_center_x, screen_center_y)
        )

        # Optional Debug Collision Rect (ensure
        # _update_collision_rect_from_image_rect has been called
        # via update_screen_rects)
        # if hasattr(self, 'collision_rect'):
        #    pygame.draw.rect(surface, (255, 0, 0),
        #                     self.collision_rect, 1)
        surface.blit(self.image, self.image_rect.topleft)
