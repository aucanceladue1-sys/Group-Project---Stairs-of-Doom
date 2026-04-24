import pygame
import random
import sys

pygame.init()

WIDTH = 480
HEIGHT = 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Montclair Stairs of Doom")
clock = pygame.time.Clock()

#COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (50, 150, 255)
BUTTON_HOVER = (80, 180, 255)

#Background
try:
    background_img = pygame.image.load("stairsbg.png").convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except:
    background_img = None

#PLAYER DIMENSIONS
PLAYER_W = 80  # Was 40
PLAYER_H = 100  # Was 50

#Student Image
try:
    student_img_orig = pygame.image.load("student.png").convert_alpha()
    student_img = pygame.transform.scale(student_img_orig, (PLAYER_W, PLAYER_H))
except:
    print("Could not find student image file. Using red square.")
    student_img = None

player_rect = pygame.Rect(200, 550, PLAYER_W, PLAYER_H)
player_y_speed = 0
gravity = 0.5
jump_power = -15
facing_right = True

score = 0
lives = 3
game_over = False
game_started = False


def make_platform(x, y, w=200, h=30, falling_type=False):
    return [x, y, w, h, falling_type, False, 25, False]


def difficulty_level():
    return min(int(score / 700), 6)


def make_platforms():
    platforms = []
    start_platform = make_platform(140, 650, 200, 15, False)
    platforms.append(start_platform)
    last_y = 650
    for i in range(1, 8):
        level = difficulty_level()
        # Increased gap slightly to account for the much taller player
        new_y = last_y - random.randint(140 + level * 5, 180 + level * 8)
        new_x = random.randint(20, WIDTH - 130)
        platforms.append(make_platform(new_x, new_y, 110, 15, False))
        last_y = new_y
    return platforms


def draw_button(text, x, y, w, h, inactive_color, active_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, w, h), border_radius=10)
        if click[0] == 1: return True
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, w, h), border_radius=10)

    font = pygame.font.SysFont(None, 40)
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=(x + w / 2, y + h / 2))
    screen.blit(text_surf, text_rect)
    return False


platforms = make_platforms()

while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if game_started and not game_over:
        keys = pygame.key.get_pressed()
        level = difficulty_level()
        move_speed = 8 + level * 0.4
        current_gravity = gravity + level * 0.03

        if keys[pygame.K_LEFT]:
            player_rect.x -= int(move_speed)
            facing_right = False
        if keys[pygame.K_RIGHT]:
            player_rect.x += int(move_speed)
            facing_right = True

        if player_rect.right < 0: player_rect.left = WIDTH
        if player_rect.left > WIDTH: player_rect.right = 0

        old_y = player_rect.y
        player_y_speed += current_gravity
        player_rect.y += int(player_y_speed)

        if player_y_speed > 0:
            for p in platforms:
                plat_rect = pygame.Rect(p[0], p[1], p[2], p[3])
                if player_rect.colliderect(plat_rect):
                    if old_y + PLAYER_H <= plat_rect.top:
                        player_rect.bottom = plat_rect.top
                        player_y_speed = jump_power
                        if p[4]: p[5] = True
                        break

        for p in platforms:
            if p[4] and p[5]:
                p[6] -= 1
                if p[6] <= 0: p[7] = True
            if p[7]: p[1] += 6 + level

        if player_rect.y < 300 and player_y_speed < 0:
            scroll = abs(int(player_y_speed))
            player_rect.y += scroll
            score += scroll
            for p in platforms: p[1] += scroll

        platforms = [p for p in platforms if p[1] < HEIGHT]

        while len(platforms) < 8:
            level = difficulty_level()
            top_p = min(platforms, key=lambda p: p[1])
            new_y = top_p[1] - random.randint(140 + level * 5, 180 + level * 8)
            platform_width = max(70, 110 - level * 5)
            new_x = random.randint(20, WIDTH - platform_width - 20)
            falling = random.random() < (0 if score < 1500 else min(0.08 + level * 0.07, 0.55))
            platforms.append(make_platform(new_x, new_y, platform_width, 15, falling))

        if player_rect.top > HEIGHT:
            lives -= 1
            player_rect.x, player_rect.y = 200, 550
            player_y_speed = 0
            if lives <= 0: game_over = True


    if background_img:
        screen.blit(background_img, (0, 0))
    else:
        screen.fill((230, 245, 255))

    if not game_started:
        title_font = pygame.font.SysFont(None, 60)
        title_surf = title_font.render("STAIRS OF DOOM", True, BLACK)
        screen.blit(title_surf, (WIDTH // 2 - 180, 200))
        if draw_button("START", WIDTH // 2 - 75, 350, 150, 60, BUTTON_COLOR, BUTTON_HOVER):
            game_started = True
    else:
        for p in platforms:
            pr = pygame.Rect(p[0], p[1], p[2], p[3])
            color = (230, 170, 70) if p[4] else (90, 210, 120)
            pygame.draw.rect(screen, color, pr)
            pygame.draw.rect(screen, BLACK, pr, 2)

        #Player Image
        if student_img:
            if not facing_right:
                flipped_img = pygame.transform.flip(student_img, True, False)
                screen.blit(flipped_img, player_rect)
            else:
                screen.blit(student_img, player_rect)
        else:
            pygame.draw.rect(screen, (255, 100, 100), player_rect)

        font = pygame.font.SysFont(None, 30)
        screen.blit(font.render(f"Score: {int(score / 10)}", True, BLACK), (10, 10))
        screen.blit(font.render(f"Lives: {lives}", True, BLACK), (10, 40))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 150))
            screen.blit(overlay, (0, 0))
            big_f = pygame.font.SysFont(None, 50)
            screen.blit(big_f.render("GAME OVER", True, BLACK), (140, 300))
            if draw_button("RETRY", WIDTH // 2 - 75, 380, 150, 50, BUTTON_COLOR, BUTTON_HOVER):
                player_rect.x, player_rect.y = 200, 550
                player_y_speed = 0
                score = 0
                lives = 3
                game_over = False
                platforms = make_platforms()

    pygame.display.flip()