import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎣 Fish Catcher")

WHITE = (255, 255, 255)
BLUE = (100, 180, 255)
BROWN = (139, 69, 19)
DARKBLUE = (0, 100, 200)
RED = (255, 80, 80)
GREEN = (100, 255, 100)
GOLD = (255, 215, 0)
BLACK = (30, 30, 30)
HOOK_COLOR = BLACK

font = pygame.font.SysFont("arial", 22)
big_font = pygame.font.SysFont("arial", 36, bold=True)

clock = pygame.time.Clock()
hook_speed = 5
fish_speed = 2
TIME_LIMIT = 60
GOAL_SCORE = 50

class Hook:
    def __init__(self):
        self.angle = 0
        self.swing_speed = 0.02
        self.length = 80
        self.active = False
        self.origin_x = WIDTH // 2
        self.origin_y = 140
        self.end_x = self.origin_x
        self.end_y = self.origin_y + self.length

    def cast(self):
        if not self.active:
            self.active = True
            self.end_y = self.origin_y + self.length

    def update(self):
        if not self.active:
            self.angle += self.swing_speed
            if self.angle > math.pi / 4 or self.angle < -math.pi / 4:
                self.swing_speed *= -1
            self.end_x = self.origin_x + int(self.length * math.sin(self.angle))
            self.end_y = self.origin_y + int(self.length * math.cos(self.angle))
        else:
            self.end_y += hook_speed
            if self.end_y > HEIGHT:
                self.active = False
                self.angle = 0

    def draw(self):
        pygame.draw.line(screen, HOOK_COLOR, (self.origin_x, self.origin_y), (self.end_x, self.end_y), 3)
        pygame.draw.circle(screen, HOOK_COLOR, (self.end_x, self.end_y), 7)

class Fish:
    def __init__(self):
        self.dir = random.choice([-1, 1])
        self.type = random.choices(["small", "medium", "large", "bomb"], weights=[4, 3, 2, 2])[0]

        if self.type == "small":
            self.color = RED
            self.width, self.height = 40, 20
            self.score = 3
        elif self.type == "medium":
            self.color = GREEN
            self.width, self.height = 50, 30
            self.score = 5
        elif self.type == "large":
            self.color = GOLD
            self.width, self.height = 60, 40
            self.score = 8
        else:
            self.color = BLACK
            self.width, self.height = 80, 60
            self.score = -5

        self.x = random.randint(50, WIDTH - self.width - 50)
        self.y = random.randint(300, HEIGHT - 40)
        if random.random() < 0.5:
            self.dir *= -1

    def update(self):
        self.x += self.dir * fish_speed
        if self.x < 20 or self.x > WIDTH - self.width:
            self.dir *= -1

    def draw(self):
        if self.type == "bomb":
            pygame.draw.circle(screen, self.color, (self.x + self.width // 2, self.y + self.height // 2), 12)
        else:
            pygame.draw.ellipse(screen, self.color, (self.x, self.y, self.width, self.height))

    def caught_by(self, hook):
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2
        return hook.active and abs(hook.end_x - cx) < self.width // 2 and abs(hook.end_y - cy) < self.height // 2

def reset_game():
    global hook, fishes, score, start_ticks, game_state
    hook = Hook()
    fishes = [Fish() for _ in range(5)]
    bomb = Fish()
    bomb.type = "bomb"
    bomb.color = BLACK
    bomb.width, bomb.height = 80, 60
    bomb.score = -5
    bomb.x = random.randint(50, WIDTH - bomb.width - 50)
    bomb.y = random.randint(300, HEIGHT - 40)
    fishes.append(bomb)
    score = 0
    start_ticks = pygame.time.get_ticks()
    game_state = "playing"

reset_game()

exit_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 50, 120, 40)
play_button = pygame.Rect(WIDTH//2 + 30, HEIGHT//2 + 50, 140, 40)

running = True
while running:
    screen.fill(BLUE)
    pygame.draw.rect(screen, DARKBLUE, (0, 200, WIDTH, HEIGHT - 200))
    pygame.draw.rect(screen, BROWN, (0, 0, WIDTH, 140))

    seconds = (pygame.time.get_ticks() - start_ticks) // 1000
    time_left = max(0, TIME_LIMIT - seconds)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game_state == "playing" and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            hook.cast()
        elif game_state in ["win", "lose", "timeout"]:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if exit_button.collidepoint(mx, my):
                    running = False
                elif play_button.collidepoint(mx, my):
                    reset_game()

    if time_left == 0 and game_state == "playing":
        if score >= GOAL_SCORE:
            game_state = "win"
        else:
            game_state = "timeout"

    if score < 0 and game_state == "playing":
        game_state = "lose"

    hook.update()
    hook.draw()

    if game_state == "playing":
        for fish in fishes:
            fish.update()
            fish.draw()
            if fish.caught_by(hook):
                score += fish.score
                if score >= GOAL_SCORE and game_state == "playing":
                    game_state = "win"
                fishes.remove(fish)
                fishes.append(Fish())
                hook.active = False

    for fish in fishes:
        if game_state == "playing":
            fish.draw()

    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render("Press SPACE to cast hook", True, WHITE), (10, 40))
    screen.blit(font.render("Red Fish: +3", True, RED), (10, 70))
    screen.blit(font.render("Green Fish: +5", True, GREEN), (180, 70))
    screen.blit(font.render("Golden Fish: +8", True, GOLD), (10, 100))
    screen.blit(font.render("Black bomb: -5", True, BLACK), (180, 100))
    screen.blit(font.render(f"{time_left}s", True, WHITE), (WIDTH - 100, 10))

    if game_state in ["win", "lose", "timeout"]:
        if game_state == "win":
            msg = big_font.render("Challenge Success! Congratulations!!!", True, GOLD)
        elif game_state == "lose":
            msg = big_font.render("Score < 0! Challenge Failed", True, RED)
        else:
            msg = big_font.render("Time's OUT! Not enough score.", True, RED)
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 40))

        pygame.draw.rect(screen, BLACK, exit_button)
        pygame.draw.rect(screen, BLACK, play_button)
        screen.blit(font.render("Exit", True, WHITE), (exit_button.x + 40, exit_button.y + 8))
        screen.blit(font.render("Play Again", True, WHITE), (play_button.x + 15, play_button.y + 8))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
