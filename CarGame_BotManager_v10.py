import random
from CarGame_BotCar_v10 import BotCar

# Further ahead for more reaction time
BOT_SPAWN_DISTANCE_AHEAD_FACTOR = 0.7
BOT_SPAWN_ZONE_DEPTH_FACTOR = 2.0
BOT_CULL_DISTANCE_BEHIND_FACTOR = 0.6
TARGET_BOTS_PER_Y_WORLD_DISTANCE = 12.0  # Spawn a bit more


class BotManager:
    def __init__(self, screen_width_pixels, screen_height_pixels,
                 world_unit_scale,
                 player_max_speed_world, player_car_scale_factor):
        self.bot_cars = []
        self.screen_width_pixels = screen_width_pixels
        self.screen_height_pixels = screen_height_pixels
        self.world_unit_scale = world_unit_scale

        self.screen_width_world = (
            screen_width_pixels / world_unit_scale
        )
        self.screen_height_world = (
            screen_height_pixels / world_unit_scale
        )

        self.player_max_speed_world = player_max_speed_world
        self.player_car_scale_factor = player_car_scale_factor

        self.last_camera_y_for_spawn_check = 0.0
        self.accumulated_camera_dy_world = 0.0

    def reset(self):
        self.bot_cars = []
        self.last_camera_y_for_spawn_check = 0.0
        self.accumulated_camera_dy_world = 0.0

    def _spawn_bot_car(self, target_world_y):
        # Default spawn X to be somewhat central, BotCar init can
        # override for specific types
        # A bit narrower for general spawn
        spawnable_track_width_world = self.screen_width_world * 0.80
        half_track_width_world = spawnable_track_width_world / 2.0
        center_screen_world_x = self.screen_width_world / 2.0

        min_x = center_screen_world_x - half_track_width_world
        max_x = center_screen_world_x + half_track_width_world
        world_x = random.uniform(min_x, max_x)

        # Pass screen_width_world to BotCar so it can make
        # informed decisions about its initial_x
        new_bot = BotCar(
            world_x, target_world_y,
            self.world_unit_scale,
            self.player_max_speed_world,
            self.player_car_scale_factor,
            self.screen_width_world  # Added screen_width_world
        )
        self.bot_cars.append(new_bot)

    def update_bots(self, delta_time, camera_world_y,
                    player_car_world_y_center):
        for bot in self.bot_cars:
            bot.update(delta_time)

        if (self.last_camera_y_for_spawn_check == 0.0 and
                camera_world_y != 0.0):
            self.last_camera_y_for_spawn_check = camera_world_y
        elif (self.last_camera_y_for_spawn_check == 0.0 and
              camera_world_y == 0.0):
            self.last_camera_y_for_spawn_check = 0.0001

        delta_camera_y_scrolled_up_world = (
            self.last_camera_y_for_spawn_check - camera_world_y
        )
        if delta_camera_y_scrolled_up_world > 0:
            self.accumulated_camera_dy_world += (
                delta_camera_y_scrolled_up_world
            )
        self.last_camera_y_for_spawn_check = camera_world_y

        score_increment = 0
        target_dist = TARGET_BOTS_PER_Y_WORLD_DISTANCE
        if self.accumulated_camera_dy_world >= target_dist:
            num_to_spawn_events = int(
                self.accumulated_camera_dy_world / target_dist
            )
            for _ in range(num_to_spawn_events):
                spawn_offset_base = (
                    self.screen_height_world *
                    BOT_SPAWN_DISTANCE_AHEAD_FACTOR
                )
                random_depth_offset = random.uniform(
                    0, self.screen_height_world *
                    BOT_SPAWN_ZONE_DEPTH_FACTOR
                )
                spawn_y_offset = spawn_offset_base + random_depth_offset
                actual_spawn_y = camera_world_y - spawn_y_offset
                self._spawn_bot_car(actual_spawn_y)
            self.accumulated_camera_dy_world %= target_dist

        active_bots = []
        for bot in self.bot_cars:
            if (not bot.passed_by_player and
                    player_car_world_y_center < bot.world_y):
                bot.passed_by_player = True
                score_increment += 1

            bot_img_h = bot.image_original_scaled.get_height()
            bot_visual_height_world = bot_img_h / self.world_unit_scale

            cull_offset = (
                self.screen_height_world *
                BOT_CULL_DISTANCE_BEHIND_FACTOR
            )
            cull_line_world_y = (
                camera_world_y + self.screen_height_world +
                cull_offset
            )
            bot_top_y = bot.world_y - bot_visual_height_world / 2.0
            if bot_top_y < cull_line_world_y:
                active_bots.append(bot)
        self.bot_cars = active_bots

        return score_increment

    def check_player_collision(self, player_car, camera_world_y):
        if not player_car:
            return False
        for bot in self.bot_cars:
            bot.update_screen_rects(camera_world_y)
            if player_car.collision_rect.colliderect(
                    bot.collision_rect):
                return True
        return False

    def draw_all(self, surface, camera_world_y):
        for bot in self.bot_cars:
            bot.draw(surface, camera_world_y)
