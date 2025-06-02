import pygame


class Obstacle:
    def __init__(self, world_x, world_y, width_world, height_world,
                 color):
        self.world_x = float(world_x)  # Center x in world units
        self.world_y = float(world_y)  # Center y in world units
        self.width_world = float(width_world)
        self.height_world = float(height_world)
        self.color = color

        # Screen rect, updated by ObstacleManager or before drawing
        # Dimensions will be calculated from world units and scale
        self.rect = pygame.Rect(0, 0, 0, 0)

    def update_screen_rect(self, camera_world_y, world_unit_scale):
        """
        Updates self.rect to reflect the obstacle's current screen position.
        """
        screen_center_x = round(self.world_x * world_unit_scale)
        screen_center_y = round(
            (self.world_y - camera_world_y) * world_unit_scale)

        screen_width = round(self.width_world * world_unit_scale)
        screen_height = round(self.height_world * world_unit_scale)

        self.rect = pygame.Rect(0, 0, screen_width, screen_height)
        self.rect.center = (screen_center_x, screen_center_y)

    def draw(self, surface, camera_world_y, world_unit_scale):
        """
        Draws the obstacle on the given surface.
        Ensures screen_rect is updated before drawing.
        """
        self.update_screen_rect(camera_world_y, world_unit_scale)

        # Only draw if the obstacle is potentially visible (simple check)
        # A more robust check would involve checking intersection with screen bounds
        if self.rect.bottom > 0 and self.rect.top < surface.get_height():
            pygame.draw.rect(surface, self.color, self.rect)