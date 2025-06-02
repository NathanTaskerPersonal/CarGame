import pygame
import math
from CarGame_Background_v7 import Background
from CarGame_PlayerCar_v7 import Car as PlayerCar
from CarGame_TitleScreen_v7 import TitleScreen
from CarGame_GameOverScreen_v7 import GameOverScreen
from CarGame_ObstacleManager_v7 import ObstacleManager

# --- Game States ---
STATE_TITLE = "TITLE"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"

# --- Camera Speed Constants ---
CAMERA_SPEED_ASYMPTOTE_FACTOR = 0.95
CAMERA_SPEED_APPROACH_RATE = 0.05


def run_game():
    pygame.init()
    pygame.font.init()

    try:
        game_icon = pygame.image.load('assets/images/game_icon.png')
        pygame.display.set_icon(game_icon)
    except pygame.error as e:
        print(f"Warning: Error loading game icon: {e}")

    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Car Game")
    clock = pygame.time.Clock()
    fps = 60

    world_unit_scale = 100.0

    try:
        # Ensure CAR_MAX_SPEED_FORWARD is at module level in your Car file
        from CarGame_PlayerCar_v7 import \
            CAR_MAX_SPEED_FORWARD as PLAYER_CAR_MAX_SPEED_FORWARD_WORLD  # Match your PlayerCar file version
    except ImportError:
        print(
            "Error: Could not import CAR_MAX_SPEED_FORWARD. Using fallback.")
        PLAYER_CAR_MAX_SPEED_FORWARD_WORLD = 5.0

    max_camera_speed_world_units = PLAYER_CAR_MAX_SPEED_FORWARD_WORLD * CAMERA_SPEED_ASYMPTOTE_FACTOR
    max_camera_speed_pixels_sec = max_camera_speed_world_units * world_unit_scale

    grass_pixel_size_const = 10
    grass_colours_const = [
        pygame.Color("#3F692B"), pygame.Color("#578A3A"),
        pygame.Color("#72A74C"), pygame.Color("#4A7733"),
        pygame.Color("#649841")
    ]

    current_game_state = STATE_TITLE
    title_screen_handler = TitleScreen(screen_width, screen_height)
    game_over_screen_handler = GameOverScreen(screen_width,
                                              screen_height)
    obstacle_manager = ObstacleManager(screen_width, screen_height,
                                       world_unit_scale)

    player_car = None
    game_background = None
    total_elapsed_time_playing = 0.0
    game_camera_world_y = 0.0

    car_off_screen_timer = 0.0
    CAR_OFF_SCREEN_LIMIT_SECONDS = 3.0
    screen_bounds_rect = screen.get_rect()

    is_running = True
    while is_running:
        delta_time = clock.tick(fps) / 1000.0
        if delta_time > (1.0 / 20.0):
            delta_time = (1.0 / 20.0)

        keys_pressed = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        if current_game_state == STATE_TITLE:
            title_screen_handler.update(delta_time, keys_pressed)
            title_screen_handler.draw(screen)

            if title_screen_handler.should_start_game():
                current_game_state = STATE_PLAYING
                total_elapsed_time_playing = 0.0
                game_camera_world_y = 0.0
                obstacle_manager.last_camera_y_for_spawn_check = 0.0
                car_off_screen_timer = 0.0

                game_background = Background(screen_width,
                                             screen_height,
                                             grass_pixel_size_const,
                                             grass_colours_const)
                car_initial_world_x = (
                                                  screen_width / 2.0) / world_unit_scale
                car_initial_world_y = ((
                                                   screen_height * 0.75) / world_unit_scale) + game_camera_world_y
                player_car = PlayerCar(car_initial_world_x,
                                       car_initial_world_y)

                obstacle_manager.reset()
                title_screen_handler.reset()

        elif current_game_state == STATE_PLAYING:
            if player_car is None:
                current_game_state = STATE_TITLE;
                continue

            player_car.update(delta_time, keys_pressed)
            # Update both visual and collision rects
            player_car.update_screen_rects(game_camera_world_y,
                                           world_unit_scale)  # Use the new method name

            current_camera_speed_pixels_sec = max_camera_speed_pixels_sec * \
                                              (1 - math.exp(
                                                  -CAMERA_SPEED_APPROACH_RATE * total_elapsed_time_playing))
            camera_y_pixel_change_on_screen = -current_camera_speed_pixels_sec * delta_time
            game_camera_world_y += camera_y_pixel_change_on_screen / world_unit_scale
            total_elapsed_time_playing += delta_time

            obstacle_manager.update_spawning_and_culling(
                game_camera_world_y)

            game_over_reason = None
            # Use player_car.collision_rect for off-screen check
            if not player_car.collision_rect.colliderect(
                    screen_bounds_rect):
                car_off_screen_timer += delta_time
                if car_off_screen_timer >= CAR_OFF_SCREEN_LIMIT_SECONDS:
                    game_over_reason = "You strayed too far off course!"
            else:
                car_off_screen_timer = 0.0

            if not game_over_reason:
                # Pass player_car.collision_rect to check_collisions if ObstacleManager expects a rect.
                # Or, modify ObstacleManager to expect a Car object and access car.collision_rect internally.
                # For now, assuming ObstacleManager's check_collisions needs the car object to access its collision_rect.
                # The existing obstacle_manager.check_collisions(player_car, ...) already uses player_car.rect (which we want to change to collision_rect).
                # Let's refine this:
                # In ObstacleManager, change player_car.rect.colliderect(obs.rect) to player_car.collision_rect.colliderect(obs.rect)
                if obstacle_manager.check_collisions(player_car,
                                                     game_camera_world_y,
                                                     world_unit_scale):
                    game_over_reason = "Collided with an obstacle!"

            if game_over_reason:
                current_game_state = STATE_GAME_OVER
                game_over_screen_handler.set_messages(
                    reason_msg=game_over_reason)
                game_over_screen_handler.reset()

            screen.fill(pygame.Color("black"))
            game_background.draw(screen, game_camera_world_y,
                                 world_unit_scale)
            obstacle_manager.draw_all(screen, game_camera_world_y,
                                      world_unit_scale)
            player_car.draw(screen, game_camera_world_y,
                            world_unit_scale)


        elif current_game_state == STATE_GAME_OVER:
            game_over_screen_handler.update(delta_time, keys_pressed)
            game_over_screen_handler.draw(screen)

            if game_over_screen_handler.should_restart_game():
                current_game_state = STATE_TITLE
                title_screen_handler.reset()
                game_over_screen_handler.reset()

        pygame.display.flip()

    pygame.font.quit()
    pygame.quit()


if __name__ == '__main__':
    run_game()