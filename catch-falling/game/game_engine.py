"""
GameEngine: owns the basket and all falling objects.

Task 1: fixed collision detection and safe object removal.
Task 2: improved basket boundaries.
Task 3: controlled object spawning.
"""

import random
import pygame

from game.basket import Basket
from game.falling_object import FallingObject
from game.collision import is_caught
from game.renderer import WIDTH, HEIGHT

# Task 3 spawning settings
MIN_SPAWN_INTERVAL_FRAMES = 35
MAX_SPAWN_INTERVAL_FRAMES = 65
MAX_OBJECTS_ON_SCREEN = 5
MIN_SPAWN_X_DISTANCE = 60

MAX_MISSES = 5


class GameEngine:
    def __init__(self):
        self.basket = Basket(x=WIDTH / 2, y=HEIGHT - 30)
        self.objects = []

        # Task 3: start with a varied spawn interval.
        self.frames_until_spawn = random.randint(
            MIN_SPAWN_INTERVAL_FRAMES,
            MAX_SPAWN_INTERVAL_FRAMES
        )

        # Remember the previous spawn position so objects
        # do not repeatedly appear in the same spot.
        self.last_spawn_x = None

        self.score = 0
        self.misses = 0
        self.game_over = False

    def _spawn_object(self):
        # Keep the entire falling object inside the playable width.
        min_x = 20
        max_x = WIDTH - 20

        # Try several times to find a position that is
        # sufficiently different from the previous spawn.
        x = random.randint(min_x, max_x)

        if self.last_spawn_x is not None:
            for _ in range(10):
                candidate_x = random.randint(min_x, max_x)

                if abs(candidate_x - self.last_spawn_x) >= MIN_SPAWN_X_DISTANCE:
                    x = candidate_x
                    break

        self.last_spawn_x = x

        self.objects.append(
            FallingObject(
                x=x,
                y=-14,
                speed=3
            )
        )

    def handle_input(self, keys_pressed):
        if self.game_over:
            return

        if keys_pressed[pygame.K_LEFT]:
            self.basket.x -= self.basket.speed

        if keys_pressed[pygame.K_RIGHT]:
            self.basket.x += self.basket.speed

        # Keep the entire basket inside the screen.
        half_width = self.basket.width / 2
        self.basket.x = max(
            half_width,
            min(WIDTH - half_width, self.basket.x)
        )

    def handle_keydown(self, key):
        if self.game_over and key == pygame.K_r:
            self.__init__()

    def update(self):
        if self.game_over:
            return

        # Task 3: count down to the next spawn.
        self.frames_until_spawn -= 1

        # Only spawn if there is room on the screen.
        if (
            self.frames_until_spawn <= 0
            and len(self.objects) < MAX_OBJECTS_ON_SCREEN
        ):
            self._spawn_object()

            # Choose a new random interval for the next object.
            self.frames_until_spawn = random.randint(
                MIN_SPAWN_INTERVAL_FRAMES,
                MAX_SPAWN_INTERVAL_FRAMES
            )

        for obj in self.objects:
            obj.update()

        basket_rect = self.basket.get_rect()

        # Task 1: collect caught objects first instead of
        # removing them while iterating through the list.
        caught_objects = []

        for obj in self.objects:
            if is_caught(basket_rect, obj):
                caught_objects.append(obj)

        # Update score for all caught objects.
        self.score += len(caught_objects)

        # Remove caught objects after the loop is finished.
        for obj in caught_objects:
            self.objects.remove(obj)

        missed = [
            o for o in self.objects
            if o.is_past_bottom(HEIGHT)
        ]

        if missed:
            self.objects = [
                o for o in self.objects
                if not o.is_past_bottom(HEIGHT)
            ]

            self.misses += len(missed)

            if self.misses >= MAX_MISSES:
                self.game_over = True

    def draw(self, surface, font):
        from game import renderer

        renderer.draw_scene(
            surface,
            self.basket,
            self.objects
        )

        renderer.draw_text(
            surface,
            font,
            f"Score: {self.score}",
            (10, 10)
        )

        renderer.draw_text(
            surface,
            font,
            f"Misses: {self.misses}/{MAX_MISSES}",
            (10, 36)
        )

        if self.game_over:
            renderer.draw_banner(
                surface,
                font,
                f"Game Over! Final score: {self.score}. Press R to restart."
            )
