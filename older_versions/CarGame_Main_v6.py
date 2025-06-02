import pygame
from CarGame_Background_v6 import Background
from CarGame_PlayerCar_v6 import Car
from CarGame_TitleScreen_v6 import TitleScreen
from CarGame_GameOverScreen_v6 import GameOverScreen

# --- Game States ---
STATE_TITLE = "TITLE"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"  # New state


def run_game():
    pygame.init()
    pygame.font.init()

    try:
        game_icon = pygame.image.load(
            '../assets/images/game_icon.png')
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
    camera_acceleration = 10.0  # pixels/sec^2 relative to total_elapsed_time_playing

    grass_pixel_size_const = 10
    grass_colours_const = [
        pygame.Color("#3F692B"), pygame.Color("#578A3A"),
        pygame.Color("#72A74C"), pygame.Color("#4A7733"),
        pygame.Color("#649841")
    ]

    current_game_state = STATE_TITLE
    title_screen_handler = TitleScreen(screen_width, screen_height)
    game_over_screen_handler = GameOverScreen(screen_width,
                                              screen_height)  # Instantiate

    player_car = None
    game_background = None
    total_elapsed_time_playing = 0.0
    game_camera_world_y = 0.0

    # Game Over condition variables
    car_off_screen_timer = 0.0
    CAR_OFF_SCREEN_LIMIT_SECONDS = 3.0
    # Define a margin for "off-screen". If car's rect is completely outside these bounds.
    # A simpler check: car.rect.colliderect(screen.get_rect()) == False
    # Or, more generously: if any part of the car is visible, it's not "off-screen".
    # The request was "outside of the screen by a decent amount (not visible in the camera)".
    # So, if the car's rect does NOT intersect the screen rect.
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

        # ------------------ STATE: TITLE SCREEN ------------------
        if current_game_state == STATE_TITLE:
            title_screen_handler.update(delta_time, keys_pressed)
            title_screen_handler.draw(screen)

            if title_screen_handler.should_start_game():
                current_game_state = STATE_PLAYING
                total_elapsed_time_playing = 0.0
                game_camera_world_y = 0.0
                car_off_screen_timer = 0.0  # Reset for new game

                game_background = Background(screen_width,
                                             screen_height,
                                             grass_pixel_size_const,
                                             grass_colours_const)
                car_initial_world_x = (
                                                  screen_width / 2.0) / world_unit_scale
                car_initial_world_y = ((
                                                   screen_height * 0.75) / world_unit_scale) + game_camera_world_y
                player_car = Car(car_initial_world_x,
                                 car_initial_world_y)

                title_screen_handler.reset()

        # -------------------- STATE: PLAYING ---------------------
        elif current_game_state == STATE_PLAYING:
            if player_car is None or game_background is None:  # Should not happen if logic is correct
                print(
                    "Error: Game objects not initialized. Reverting to TITLE.")
                current_game_state = STATE_TITLE
                title_screen_handler.reset()
                continue

            player_car.update(delta_time, keys_pressed)
            # Update car's screen rect for collision/bounds checks *after* its state is updated
            player_car.update_screen_rect(game_camera_world_y,
                                          world_unit_scale)

            # --- Game Over Check: Car Off-Screen ---
            if not player_car.rect.colliderect(screen_bounds_rect):
                car_off_screen_timer += delta_time
                if car_off_screen_timer >= CAR_OFF_SCREEN_LIMIT_SECONDS:
                    current_game_state = STATE_GAME_OVER
                    game_over_screen_handler.set_messages(
                        reason_msg="You drifted too far off course!"
                        # Or "Too slow to keep up!"
                    )
                    game_over_screen_handler.reset()  # Reset its internal state for display
            else:
                car_off_screen_timer = 0.0  # Reset timer if car is back on screen

            # Camera movement
            camera_speed_pixels_sec = camera_acceleration * total_elapsed_time_playing
            camera_y_pixel_change = -camera_speed_pixels_sec * delta_time
            game_camera_world_y += camera_y_pixel_change / world_unit_scale
            total_elapsed_time_playing += delta_time

            # Drawing
            screen.fill(pygame.Color("black"))
            game_background.draw(screen, game_camera_world_y,
                                 world_unit_scale)
            player_car.draw(screen, game_camera_world_y,
                            world_unit_scale)

        # ----------------- STATE: GAME OVER --------------------
        elif current_game_state == STATE_GAME_OVER:
            game_over_screen_handler.update(delta_time, keys_pressed)
            game_over_screen_handler.draw(screen)

            if game_over_screen_handler.should_restart_game():
                current_game_state = STATE_TITLE  # Go back to title screen
                title_screen_handler.reset()  # Reset title screen
                game_over_screen_handler.reset()  # Reset game over screen

        pygame.display.flip()

    pygame.font.quit()
    pygame.quit()


if __name__ == '__main__':
    run_game()