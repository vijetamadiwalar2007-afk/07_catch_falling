"""
GameEngine: owns the basket and all falling objects.

Task 1: fixed collision detection and safe object removal.
Task 2: improved basket boundaries.
Task 3: controlled object spawning.
Task 4: temporary basket speed boost.
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

# Task 4 speed boost settings
BOOST_MULTIPLIER = 2
BOOST_DURATION_FRAMES = 180

MAX_MISSES = 5


class GameEngine:
    def __init__(self):
        self.basket = Basket(x=WIDTH / 2, y=HEIGHT - 30)
        self.objects = []

        # Task 3: varied spawn interval.
        self.frames_until_spawn = random.randint(
            MIN_SPAWN_INTERVAL_FRAMES,
            MAX_SPAWN_INTERVAL_FRAMES
        )

        # Task 3: remember previous spawn position.
        self.last_spawn_x = None

        self.score = 0
        self.misses = 0
        self.game_over = False

        # Task 4: boost timer.
        self.boost_frames_remaining = 0

    def _spawn_object(self):
        # Keep objects inside the playable width.
        min_x = 20
        max_x = WIDTH - 20

        x = random.randint(min_x, max_x)

        # Avoid repeatedly spawning in the same horizontal position.
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

        # Task 4: use increased speed while boost is active.
        if self.boost_frames_remaining > 0:
            self.basket.speed = (
                self.basket.normal_speed * BOOST_MULTIPLIER
            )
        else:
            self.basket.speed = self.basket.normal_speed

        if keys_pressed[pygame.K_LEFT]:
            self.basket.x -= self.basket.speed

        if keys_pressed[pygame.K_RIGHT]:
            self.basket.x += self.basket.speed

        # Task 2: keep the entire basket inside the screen.
        half_width = self.basket.width / 2
        self.basket.x = max(
            half_width,
            min(WIDTH - half_width, self.basket.x)
        )

    def handle_keydown(self, key):
        if self.game_over and key == pygame.K_r:
            self.__init__()
            return

        # Task 4: activate speed boost with Spacebar.
        if key == pygame.K_SPACE and self.boost_frames_remaining <= 0:
            self.boost_frames_remaining = BOOST_DURATION_FRAMES

    def update(self):
        if self.game_over:
            return

        # Task 4: count down the boost timer.
        if self.boost_frames_remaining > 0:
            self.boost_frames_remaining -= 1

            if self.boost_frames_remaining == 0:
                self.basket.speed = self.basket.normal_speed

        # Task 3: count down to the next spawn.
        self.frames_until_spawn -= 1

        # Only spawn when there is room on the screen.
        if (
            self.frames_until_spawn <= 0
            and len(self.objects) < MAX_OBJECTS_ON_SCREEN
        ):
            self._spawn_object()

            # Choose a new random interval.
            self.frames_until_spawn = random.randint(
                MIN_SPAWN_INTERVAL_FRAMES,
                MAX_SPAWN_INTERVAL_FRAMES
            )

        for obj in self.objects:
            obj.update()

        basket_rect = self.basket.get_rect()

        # Task 1: collect caught objects before removing them.
        caught_objects = []

        for obj in self.objects:
            if is_caught(basket_rect, obj):
                caught_objects.append(obj)

        self.score += len(caught_objects)

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

        # Task 4: clearly show the boost while active.
        if self.boost_frames_remaining > 0:
            renderer.draw_text(
                surface,
                font,
                "SPEED BOOST!",
                (10, 62)
            )

        if self.game_over:
            renderer.draw_banner(
                surface,
                font,
                f"Game Over! Final score: {self.score}. Press R to restart."
            )
