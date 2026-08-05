import random
import pygame
from dungeon_gen import generate_dungeon
from constant import *

def draw(screen, font, grid, rooms, seed, status):
    screen.fill(COLOR_BG)
    if status["status"] != 0:
        label = font.render(f"Error: {status['message']}", True, (255, 0, 0))
        screen.blit(label, (MARGIN, MARGIN + GRID_H * CELL_SIZE + 12))
        return
    
    room_by_coord = {room.coord: room for room in rooms}
    
    for x, y in grid:
        rect = pygame.Rect(MARGIN + x * CELL_SIZE, MARGIN + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if (x, y) in room_by_coord:
            room = room_by_coord[(x, y)]
            color = COLOR_SPAWN if room.room_type == "spawn" else COLOR_BOSS if room.room_type == "boss" else COLOR_ROOM
        else:
            color = COLOR_EMPTY
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, COLOR_GRID_LINE, rect, 1)
    
    label = font.render(f"seed={seed}  rooms={len(rooms)}",True,COLOR_TEXT)

    screen.blit(label, (MARGIN, MARGIN + GRID_H * CELL_SIZE + 12))
    label = font.render("(R: random seed, ESPACE: seed+1, ECHAP: quitter)",True,COLOR_TEXT)
    screen.blit(label, (MARGIN, MARGIN + GRID_H * CELL_SIZE + 36))
 
def main():
    pygame.init()
    screen = pygame.display.set_mode((MARGIN * 2 + GRID_W * CELL_SIZE, MARGIN * 3 + GRID_H * CELL_SIZE + 20))
    pygame.display.set_caption("Dungeon Generator")
    font = pygame.font.SysFont(None, 24)

    seed = random.randint(0, 2**32 - 1)
    grid, rooms, status = generate_dungeon(seed, continuity_bias=CONTINUITY_BIAS, w=GRID_W, h=GRID_H, max_rooms=MAX_ROOMS)
  

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    seed = random.randint(0, 2**32 - 1)
                    grid, rooms, status = generate_dungeon(seed, continuity_bias=CONTINUITY_BIAS, w=GRID_W, h=GRID_H, max_rooms=MAX_ROOMS)
                elif event.key == pygame.K_SPACE:
                    seed += 1
                    grid, rooms, status = generate_dungeon(seed, continuity_bias=CONTINUITY_BIAS, w=GRID_W, h=GRID_H, max_rooms=MAX_ROOMS)
      
        draw(screen, font, grid, rooms, seed, status)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()