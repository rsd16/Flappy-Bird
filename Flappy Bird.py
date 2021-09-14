from itertools import cycle
import random
import sys
import pygame
from pygame.locals import *


FPS = 30
SCREEN_WIDTH  = 288
SCREEN_HEIGHT = 512
PIPE_GAP_SIZE = 100
BASE_Y = SCREEN_HEIGHT * 0.79
IMAGES = {}
SOUNDS = {}
HIT_BOX = {}
BACKGROUNDS_LIST = ('assets/sprites/background-day.png', 'assets/sprites/background-night.png')
PIPES_LIST = ('assets/sprites/pipe-green.png', 'assets/sprites/pipe-red.png')
PLAYERS_LIST = (('assets/sprites/redbird-upflap.png', 'assets/sprites/redbird-midflap.png', 'assets/sprites/redbird-downflap.png',),
                ('assets/sprites/bluebird-upflap.png','assets/sprites/bluebird-midflap.png','assets/sprites/bluebird-downflap.png',),
                ('assets/sprites/yellowbird-upflap.png','assets/sprites/yellowbird-midflap.png','assets/sprites/yellowbird-downflap.png',))

def intro_screen():
    player_index = 0
    player_index_gen = cycle([0, 1, 2, 1])
    loop_iter = 0

    player_x = int(SCREEN_WIDTH * 0.2)
    player_y = int((SCREEN_HEIGHT - IMAGES['player'][0].get_height()) / 2)

    message_x = int((SCREEN_WIDTH - IMAGES['message'].get_width()) / 2)
    message_y = int(SCREEN_HEIGHT * 0.12)

    base_x = 0
    base_shift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    player_shm_values = {'val': 0, 'dir': 1}

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()

            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                SOUNDS['wing'].play()
                return {'player_y': player_y + player_shm_values['val'], 'base_x': base_x, 'player_index_gen': player_index_gen}

        if (loop_iter + 1) % 5 == 0:
            player_index = next(player_index_gen)

        loop_iter = (loop_iter + 1) % 30
        base_x = -((-base_x + 4) % base_shift)
        player_shm(player_shm_values)

        SCREEN.blit(IMAGES['background'], (0,0))
        SCREEN.blit(IMAGES['player'][player_index], (player_x, player_y + player_shm_values['val']))
        SCREEN.blit(IMAGES['message'], (message_x, message_y))
        SCREEN.blit(IMAGES['base'], (base_x, BASE_Y))

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def main_game(movement_info):
    score = 0
    player_index = 0
    loop_iter = 0
    player_index_gen = movement_info['player_index_gen']
    player_x = int(SCREEN_WIDTH * 0.2)
    player_y = movement_info['player_y']

    base_x = movement_info['base_x']
    base_shift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    new_pipe1 = get_random_pipe()
    new_pipe2 = get_random_pipe()

    upper_pipes = [{'x': SCREEN_WIDTH + 200, 'y': new_pipe1[0]['y']}, {'x': SCREEN_WIDTH + 200 + (SCREEN_WIDTH / 2), 'y': new_pipe2[0]['y']}]
    lower_pipes = [{'x': SCREEN_WIDTH + 200, 'y': new_pipe1[1]['y']}, {'x': SCREEN_WIDTH + 200 + (SCREEN_WIDTH / 2), 'y': new_pipe2[1]['y']}]

    dt = FPSCLOCK.tick(FPS) / 1000
    pipe_velocity_x = -128 * dt

    player_velocity_y = -9
    player_max_velocity_y = 10
    player_min_velocity_y = -8
    player_acceleration_y = 1
    player_rotation = 45
    player_velocity_rotation = 3
    player_rotation_threshold = 20
    player_flap_acceleration = -9
    player_flapped = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()

            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if player_y > -2 * IMAGES['player'][0].get_height():
                    player_velocity_y = player_flap_acceleration
                    player_flapped = True
                    SOUNDS['wing'].play()

        crash_test = check_collision({'x': player_x, 'y': player_y, 'index': player_index}, upper_pipes, lower_pipes)

        if crash_test[0]:
            return {'y': player_y, 'groundCrash': crash_test[1], 'base_x': base_x, 'upper_pipes': upper_pipes,
                    'lower_pipes': lower_pipes, 'score': score, 'player_velocity_y': player_velocity_y, 'player_rotation': player_rotation}

        player_mid_position = player_x + IMAGES['player'][0].get_width() / 2
        for pipe in upper_pipes:
            pipe_mid_position = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipe_mid_position <= player_mid_position < pipe_mid_position + 4:
                score += 1
                SOUNDS['point'].play()

        if (loop_iter + 1) % 3 == 0:
            player_index = next(player_index_gen)

        loop_iter = (loop_iter + 1) % 30
        base_x = -((-base_x + 100) % base_shift)

        if player_rotation > -90:
            player_rotation -= player_velocity_rotation

        if player_velocity_y < player_max_velocity_y and not player_flapped:
            player_velocity_y += player_acceleration_y

        if player_flapped:
            player_flapped = False

            player_rotation = 45

        player_height = IMAGES['player'][player_index].get_height()
        player_y += min(player_velocity_y, BASE_Y - player_y - player_height)

        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            upper_pipe['x'] += pipe_velocity_x
            lower_pipe['x'] += pipe_velocity_x

        if 3 > len(upper_pipes) > 0 and 0 < upper_pipes[0]['x'] < 5:
            new_pipe = get_random_pipe()
            upper_pipes.append(new_pipe[0])
            lower_pipes.append(new_pipe[1])

        if len(upper_pipes) > 0 and upper_pipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upper_pipes.pop(0)
            lower_pipes.pop(0)

        SCREEN.blit(IMAGES['background'], (0,0))

        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            SCREEN.blit(IMAGES['pipe'][0], (upper_pipe['x'], upper_pipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lower_pipe['x'], lower_pipe['y']))

        SCREEN.blit(IMAGES['base'], (base_x, BASE_Y))

        show_score(score)

        visible_rotation = player_rotation_threshold
        if player_rotation <= player_rotation_threshold:
            visible_rotation = player_rotation

        player_surface = pygame.transform.rotate(IMAGES['player'][player_index], visible_rotation)
        SCREEN.blit(player_surface, (player_x, player_y))

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def game_over(crash_info):
    score = crash_info['score']
    player_x = SCREEN_WIDTH * 0.2
    player_y = crash_info['y']
    player_height = IMAGES['player'][0].get_height()
    player_velocity_y = crash_info['player_velocity_y']
    player_acceleration_y = 2
    player_rotation = crash_info['player_rotation']
    player_velocity_rotation = 7

    base_x = crash_info['base_x']

    upper_pipes = crash_info['upper_pipes'],
    lower_pipes = crash_info['lower_pipes']

    SOUNDS['hit'].play()
    if not crash_info['groundCrash']:
        SOUNDS['die'].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if player_y + player_height >= BASE_Y - 1:
                    return

        if player_y + player_height < BASE_Y - 1:
            player_y += min(player_velocity_y, BASE_Y - player_y - player_height)

        if player_velocity_y < 15:
            player_velocity_y += player_acceleration_y

        if not crash_info['groundCrash']:
            if player_rotation > -90:
                player_rotation -= player_velocity_rotation

        SCREEN.blit(IMAGES['background'], (0,0))

        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            SCREEN.blit(IMAGES['pipe'][0], (upper_pipe['x'], upper_pipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lower_pipe['x'], lower_pipe['y']))

        SCREEN.blit(IMAGES['base'], (base_x, BASE_Y))
        show_score(score)

        player_surface = pygame.transform.rotate(IMAGES['player'][1], player_rotation)
        SCREEN.blit(player_surface, (player_x,player_y))
        SCREEN.blit(IMAGES['gameover'], (50, 180))

        FPSCLOCK.tick(FPS)
        pygame.display.update()

def player_shm(player_shm):
    if abs(player_shm['val']) == 8:
        player_shm['dir'] *= -1

    if player_shm['dir'] == 1:
         player_shm['val'] += 1
    else:
        player_shm['val'] -= 1

def get_random_pipe():
    gap_Y = random.randrange(0, int(BASE_Y * 0.6 - PIPE_GAP_SIZE))
    gap_Y += int(BASE_Y * 0.2)
    pipe_height = IMAGES['pipe'][0].get_height()
    pipe_X = SCREEN_WIDTH + 10
    return [{'x': pipe_X, 'y': gap_Y - pipe_height}, {'x': pipe_X, 'y': gap_Y + PIPE_GAP_SIZE}]

def show_score(score):
    score_digits = [int(x) for x in list(str(score))]
    total_width = 0

    for digit in score_digits:
        total_width += IMAGES['numbers'][digit].get_width()

    x_offset = (SCREEN_WIDTH - total_width) / 2

    for digit in score_digits:
        SCREEN.blit(IMAGES['numbers'][digit], (x_offset, SCREEN_HEIGHT * 0.1))
        x_offset += IMAGES['numbers'][digit].get_width()

def check_collision(player, upper_pipes, lower_pipes):
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    if player['y'] + player['h'] >= BASE_Y - 1:
        return [True, True]
    else:
        player_rect = pygame.Rect(player['x'], player['y'], player['w'], player['h'])
        pipe_width = IMAGES['pipe'][0].get_width()
        pipe_height = IMAGES['pipe'][0].get_height()

        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            upper_pipe_rect = pygame.Rect(upper_pipe['x'], upper_pipe['y'], pipe_width, pipe_height)
            lower_pipe_rect = pygame.Rect(lower_pipe['x'], lower_pipe['y'], pipe_width, pipe_height)

            player_hit_box = HIT_BOX['player'][pi]
            upper_pipe_hit_box = HIT_BOX['pipe'][0]
            lower_pipe_hit_box = HIT_BOX['pipe'][1]

            upper_pipe_collide = pixel_collision(player_rect, upper_pipe_rect, player_hit_box, upper_pipe_hit_box)
            lower_pipe_collide = pixel_collision(player_rect, lower_pipe_rect, player_hit_box, lower_pipe_hit_box)

            if upper_pipe_collide or lower_pipe_collide:
                return [True, False]

    return [False, False]

def pixel_collision(rect1, rect2, hit_box1, hit_box2):
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1 = rect.x - rect1.x
    y1 = rect.y - rect1.y
    x2 = rect.x - rect2.x
    y2 = rect.y - rect2.y

    for x in range(rect.width):
        for y in range(rect.height):
            if hit_box1[x1 + x][y1 + y] and hit_box2[x2 + x][y2 + y]:
                return True

    return False

def get_hit_box(image):
    box = []
    for x in range(image.get_width()):
        box.append([])
        for y in range(image.get_height()):
            box[x].append(bool(image.get_at((x, y))[3]))

    return box

def main():
    global SCREEN
    global FPSCLOCK

    pygame.init()

    FPSCLOCK = pygame.time.Clock()

    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Flappy Bird')

    IMAGES['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
    IMAGES['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
    IMAGES['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()
    IMAGES['numbers'] = (pygame.image.load('assets/sprites/0.png').convert_alpha(),
                         pygame.image.load('assets/sprites/1.png').convert_alpha(),
                         pygame.image.load('assets/sprites/2.png').convert_alpha(),
                         pygame.image.load('assets/sprites/3.png').convert_alpha(),
                         pygame.image.load('assets/sprites/4.png').convert_alpha(),
                         pygame.image.load('assets/sprites/5.png').convert_alpha(),
                         pygame.image.load('assets/sprites/6.png').convert_alpha(),
                         pygame.image.load('assets/sprites/7.png').convert_alpha(),
                         pygame.image.load('assets/sprites/8.png').convert_alpha(),
                         pygame.image.load('assets/sprites/9.png').convert_alpha())

    if 'win' in sys.platform:
        sound_extension = '.wav'
    else:
        sound_extension = '.ogg'

    SOUNDS['die'] = pygame.mixer.Sound('assets/audio/die' + sound_extension)
    SOUNDS['hit'] = pygame.mixer.Sound('assets/audio/hit' + sound_extension)
    SOUNDS['point'] = pygame.mixer.Sound('assets/audio/point' + sound_extension)
    SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + sound_extension)
    SOUNDS['wing'] = pygame.mixer.Sound('assets/audio/wing' + sound_extension)

    while True:
        background = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[background]).convert()

        player = random.randint(0, len(PLAYERS_LIST) - 1)
        IMAGES['player'] = (pygame.image.load(PLAYERS_LIST[player][0]).convert_alpha(),
                            pygame.image.load(PLAYERS_LIST[player][1]).convert_alpha(),
                            pygame.image.load(PLAYERS_LIST[player][2]).convert_alpha())

        pipe = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES['pipe'] = (pygame.transform.flip(pygame.image.load(PIPES_LIST[pipe]).convert_alpha(), False, True),
                          pygame.image.load(PIPES_LIST[pipe]).convert_alpha())

        HIT_BOX['pipe'] = (get_hit_box(IMAGES['pipe'][0]), get_hit_box(IMAGES['pipe'][1]))

        HIT_BOX['player'] = (get_hit_box(IMAGES['player'][0]), get_hit_box(IMAGES['player'][1]), get_hit_box(IMAGES['player'][2]))

        movement_info = intro_screen()
        crash_info = main_game(movement_info)
        game_over(crash_info)

if __name__ == '__main__':
    main()
