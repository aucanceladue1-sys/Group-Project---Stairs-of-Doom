import pygame
import random
import sys

pygame.init()

WIDTH = 480
HEIGHT = 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Montclair Stairs of Doom")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (50, 150, 255)
BUTTON_HOVER = (80, 180, 255)

try:
    background_img = pygame.image.load("stairsbg.png").convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except:
    background_img = None

PLAYER_W = 80
PLAYER_H = 100

OBSTACLE_W = 35
OBSTACLE_H = 35
obstacles = []
platforms_since_obstacle = 5

try:
    student_img_orig = pygame.image.load("student.png").convert_alpha()
    student_img = pygame.transform.scale(student_img_orig, (PLAYER_W, PLAYER_H))
except:
    print("Could not find student image file. Using red square.")
    student_img = None

player_rect = pygame.Rect(200, 550, PLAYER_W, PLAYER_H)
player_y_speed = 0
gravity = 0.5
jump_power = -16
facing_right = True
last_safe_platform = None
score = 0
lives = 3
game_over = False
game_started = False


def make_platform(x, y, w=200, h=30, falling_type=False, moving=False):
    move_speed = random.choice([-2, 2]) if moving else 0
    return [x, y, w, h, falling_type, False, 25, False, moving, move_speed]


def make_obstacle(x, y):
    return pygame.Rect(x, y, OBSTACLE_W, OBSTACLE_H)


def difficulty_level():
    return min(int(score / 700), 6)


def obstacle_x_on_platform(platform_x, platform_width):
    side = random.choice(["left", "right"])

    if side == "left":
        return platform_x
    else:
        return platform_x + platform_width - OBSTACLE_W


def should_spawn_obstacle(level):
    global platforms_since_obstacle

    if score < 1500:
        return False

    if platforms_since_obstacle < 5:
        return False

    if random.random() < min(0.08 + level * 0.06, 0.35):
        platforms_since_obstacle = 0
        return True

    return False


def draw_sky_background():
    screen.fill((135, 206, 235))

    pygame.draw.circle(screen, (255, 245, 120), (390, 90), 45)

    cloud_color = (255, 255, 255)

    pygame.draw.circle(screen, cloud_color, (90, 120), 25)
    pygame.draw.circle(screen, cloud_color, (120, 105), 35)
    pygame.draw.circle(screen, cloud_color, (155, 120), 25)
    pygame.draw.rect(screen, cloud_color, (85, 120, 75, 25))

    pygame.draw.circle(screen, cloud_color, (310, 220), 22)
    pygame.draw.circle(screen, cloud_color, (340, 205), 32)
    pygame.draw.circle(screen, cloud_color, (375, 220), 22)
    pygame.draw.rect(screen, cloud_color, (305, 220, 75, 22))

    pygame.draw.circle(screen, cloud_color, (130, 360), 18)
    pygame.draw.circle(screen, cloud_color, (155, 345), 28)
    pygame.draw.circle(screen, cloud_color, (185, 360), 18)
    pygame.draw.rect(screen, cloud_color, (125, 360, 65, 18))


def make_platforms():
    global platforms_since_obstacle

    platforms = []
    start_platform = make_platform(140, 650, 200, 15, False)
    platforms.append(start_platform)

    last_y = 650

    for i in range(1, 8):
        level = difficulty_level()
        new_y = last_y - random.randint(110, 150)
        new_x = random.randint(20, WIDTH - 130)
        platform_width = 110

        platforms.append(make_platform(new_x, new_y, platform_width, 15, False))

        platforms_since_obstacle += 1

        if should_spawn_obstacle(level):
            obs_x = obstacle_x_on_platform(new_x, platform_width)
            obs_y = new_y - OBSTACLE_H
            obstacles.append(make_obstacle(obs_x, obs_y))

        last_y = new_y

    return platforms


def draw_button(text, x, y, w, h, inactive_color, active_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, w, h), border_radius=10)
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, w, h), border_radius=10)

    font = pygame.font.SysFont(None, 40)
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=(x + w / 2, y + h / 2))
    screen.blit(text_surf, text_rect)

    return False


def draw_title():
    title_font = pygame.font.SysFont(None, 80)
    lines = ["STAIRS", "OF", "DOOM"]

    start_y = 145
    spacing = 85

    for i, line in enumerate(lines):
        y = start_y + i * spacing

        shadow = title_font.render(line, True, (50, 50, 50))
        screen.blit(shadow, (WIDTH // 2 - shadow.get_width() // 2 + 4, y + 4))

        for dx in [-2, 2]:
            for dy in [-2, 2]:
                outline = title_font.render(line, True, BLACK)
                screen.blit(outline, (WIDTH // 2 - outline.get_width() // 2 + dx, y + dy))

        main = title_font.render(line, True, WHITE)
        screen.blit(main, (WIDTH // 2 - main.get_width() // 2, y))


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

        if player_rect.right < 0:
            player_rect.left = WIDTH

        if player_rect.left > WIDTH:
            player_rect.right = 0

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
                        last_safe_platform = p

                        if p[4]:
                            p[5] = True

                        break

            for o in obstacles:
                if player_rect.colliderect(o):
                    if old_y + PLAYER_H <= o.top:
                        lives -= 1
                        player_rect.x, player_rect.y = 200, 550
                        player_y_speed = jump_power

                        if lives <= 0:
                            game_over = True

                        break

        for p in platforms:
            if p[4] and p[5]:
                p[6] -= 1
                if p[6] <= 0:
                    p[7] = True

            if p[7]:
                old_platform_y = p[1]
                fall_amount = 6 + level
                p[1] += fall_amount

                for o in obstacles:
                    if (
                        o.bottom == old_platform_y
                        and o.left >= p[0] - 5
                        and o.right <= p[0] + p[2] + 5
                    ):
                        o.y += fall_amount

        for p in platforms:
            if p[8]:
                old_platform_x = p[0]
                p[0] += p[9]

                if p[0] <= 0 or p[0] + p[2] >= WIDTH:
                    p[9] *= -1

                if player_rect.bottom == p[1] and player_rect.right > p[0] and player_rect.left < p[0] + p[2]:
                    player_rect.x += p[0] - old_platform_x

        if player_rect.y < 300 and player_y_speed < 0:
            scroll = abs(int(player_y_speed))
            player_rect.y += scroll
            score += scroll

            for p in platforms:
                p[1] += scroll

            for o in obstacles:
                o.y += scroll

        platforms = [p for p in platforms if p[1] < HEIGHT]
        obstacles = [o for o in obstacles if o.y < HEIGHT]

        while len(platforms) < 8:
            level = difficulty_level()
            top_p = min(platforms, key=lambda p: p[1])
            new_y = top_p[1] - random.randint(100, 130)
            platform_width = max(70, 110 - level * 5)
            new_x = random.randint(40, WIDTH - platform_width - 40)

            falling = random.random() < (
                0 if score < 1500 else min(0.08 + level * 0.07, 0.55)
            )

            moving = random.random() < 0.25 if score >= 500 else False

            platforms.append(make_platform(new_x, new_y, platform_width, 15, falling, moving))

            platforms_since_obstacle += 1

            if should_spawn_obstacle(level):
                obs_x = obstacle_x_on_platform(new_x, platform_width)
                obs_y = new_y - OBSTACLE_H
                obstacles.append(make_obstacle(obs_x, obs_y))

        if player_rect.top > HEIGHT:
            lives -= 1

            if last_safe_platform is not None:
                last_safe_platform[7] = False
                last_safe_platform[5] = False
                last_safe_platform[6] = 25
                last_safe_platform[1] = 600

                if last_safe_platform not in platforms:
                    platforms.append(last_safe_platform)

                player_rect.x = last_safe_platform[0] + last_safe_platform[2] // 2 - PLAYER_W // 2
                player_rect.bottom = last_safe_platform[1]
            else:
                player_rect.x, player_rect.y = 200, 550

            player_y_speed = jump_power

            if lives <= 0:
                game_over = True

    if not game_started:
        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill((230, 245, 255))

        draw_title()

        if draw_button("START", WIDTH // 2 - 75, 430, 150, 60, BUTTON_COLOR, BUTTON_HOVER):
            game_started = True

    else:
        draw_sky_background()

        for p in platforms:
            pr = pygame.Rect(p[0], p[1], p[2], p[3])

            if p[8]:
                color = (80, 160, 255)
            elif p[4]:
                color = (230, 170, 70)
            else:
                color = (90, 210, 120)
                
            pygame.draw.rect(screen, color, pr)
            pygame.draw.rect(screen, BLACK, pr, 2)

        for o in obstacles:
            scale = 0.7

            half_width = int(o.width * scale / 2)
            height = int(o.height * scale)

            points = [
                (o.centerx, o.bottom - height),
                (o.centerx - half_width, o.bottom),
                (o.centerx + half_width, o.bottom)
            ]

            pygame.draw.polygon(screen, (200, 40, 40), points)
            pygame.draw.polygon(screen, BLACK, points, 2)

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
                obstacles = []
                platforms_since_obstacle = 5
                platforms = make_platforms()

    pygame.display.flip()
