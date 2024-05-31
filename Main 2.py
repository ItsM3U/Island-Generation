import sys
import pygame
import noise
import random
import math

WIDTH = 800
HEIGHT = 600
RESOLUTION = (WIDTH, HEIGHT)
TITLE = "Insula"
FPS = 60

WORLD_SIZE = 128
NOISE_SCALE = 100
MIN_CELLS = 1000
CELL_SIZE = 10

FILL = (0, 0, 0)
SEA = (60, 160, 235)
SAND = (250, 200, 100)
GRASS = (60, 150, 40)
STONE = (85, 85, 85)

def GenerateSeed():
    return random.randint(0, 1000)

class Game:
    def __init__(self):
        self.Screen = pygame.display.set_mode(RESOLUTION)
        pygame.display.set_caption(TITLE)
        self.Clock = pygame.time.Clock()
        self.Running = True
        self.Keys = pygame.key.get_pressed()
        self.Seed = GenerateSeed()
        self.World = self.GenerateWorld()
        self.CameraX = 0.0
        self.CameraY = 0.0
        self.ZoomLevel = 0.625
        self.MaxCameraX = (WORLD_SIZE * CELL_SIZE * self.ZoomLevel - WIDTH) / (2 * CELL_SIZE * self.ZoomLevel)
        self.MaxCameraY = (WORLD_SIZE * CELL_SIZE * self.ZoomLevel - HEIGHT) / (2 * CELL_SIZE * self.ZoomLevel)
        self.MinCameraX = -self.MaxCameraX
        self.MinCameraY = -self.MaxCameraY
        self.IsDragging = False
        self.DragStart = (0, 0)

    def GenerateWorld(self):
        World = []

        for y in range(WORLD_SIZE):
            Row = []
            for x in range(WORLD_SIZE):
                DistanceToCenter = math.sqrt((x - 64) ** 2 + (y - 64) ** 2)
                ScaledDistance = DistanceToCenter / (WORLD_SIZE / math.sqrt(2))
                Value = noise.snoise2(x / NOISE_SCALE, y / NOISE_SCALE, octaves=8, persistence=0.6, lacunarity=2.0, repeatx=1024, repeaty=1024, base=self.Seed)
                if Value > ScaledDistance:
                    if 0 < Value < 0.225:
                        Row.append(1)
                    elif 0.225 < Value < 0.315:
                        Row.append(2)
                    elif 0.315 < Value < 0.5:
                        Row.append(3)
                    else:
                        Row.append(0)
                else:
                    Row.append(0)
            World.append(Row)

        if sum(sum(Row) for Row in World) < MIN_CELLS:
            self.Seed += 1
            return self.GenerateWorld()

        return World

    def HandleEvents(self):
        for Event in pygame.event.get():
            if Event.type == pygame.QUIT:
                self.Running = False
            elif Event.type == pygame.MOUSEBUTTONDOWN:
                if Event.button == 1:
                    self.IsDragging = True
                    self.DragStart = pygame.mouse.get_pos()
            elif Event.type == pygame.MOUSEBUTTONUP:
                if Event.button == 1:
                    self.IsDragging = False
            elif Event.type == pygame.MOUSEMOTION and self.IsDragging:
                CurrentPosition = pygame.mouse.get_pos()
                DiffX = (CurrentPosition[0] - self.DragStart[0])
                DiffY = (CurrentPosition[1] - self.DragStart[1])
                self.CameraX += DiffX / (CELL_SIZE * self.ZoomLevel)
                self.CameraY += DiffY / (CELL_SIZE * self.ZoomLevel)
                self.DragStart = CurrentPosition
            elif Event.type == pygame.MOUSEWHEEL:
                if Event.y > 0:
                    self.ZoomLevel *= 1.1
                elif Event.y < 0:
                    self.ZoomLevel /= 1.1

    def Update(self):
        self.Clock.tick(FPS)

        self.Keys = pygame.key.get_pressed()
        if self.Keys[pygame.K_ESCAPE]:
            self.Running = False

        self.ZoomLevel = max(0.625, min(self.ZoomLevel, 2.0))

        pygame.display.set_caption(f"{TITLE} - Camera ({int(self.CameraX)}, {int(self.CameraY)}) - Zoom ({self.ZoomLevel:.3f}) - Seed ({self.Seed}) - FPS ({int(self.Clock.get_fps())})")

        self.MaxCameraX = (WORLD_SIZE * CELL_SIZE * self.ZoomLevel - WIDTH) / (2 * CELL_SIZE * self.ZoomLevel)
        self.MaxCameraY = (WORLD_SIZE * CELL_SIZE * self.ZoomLevel - HEIGHT) / (2 * CELL_SIZE * self.ZoomLevel)
        self.MinCameraX = -self.MaxCameraX
        self.MinCameraY = -self.MaxCameraY

        self.CameraX = max(self.MinCameraX, min(self.CameraX, self.MaxCameraX))
        self.CameraY = max(self.MinCameraY, min(self.CameraY, self.MaxCameraY))

    def Render(self):
        self.Screen.fill(FILL)

        GridX = (WIDTH - WORLD_SIZE * CELL_SIZE * self.ZoomLevel) // 2 + int(self.CameraX * CELL_SIZE * self.ZoomLevel)
        GridY = (HEIGHT - WORLD_SIZE * CELL_SIZE * self.ZoomLevel) // 2 + int(self.CameraY * CELL_SIZE * self.ZoomLevel)

        Surface = pygame.Surface((WORLD_SIZE * CELL_SIZE, WORLD_SIZE * CELL_SIZE))

        for y, Row in enumerate(self.World):
            for x, Value in enumerate(Row):
                CellX = (x * CELL_SIZE)
                CellY = (y * CELL_SIZE)
                CellRect = pygame.Rect(CellX, CellY, CELL_SIZE, CELL_SIZE)

                if Value == 0:
                    pygame.draw.rect(Surface, SEA, CellRect)
                elif Value == 1:
                    pygame.draw.rect(Surface, SAND, CellRect)
                elif Value == 2:
                    pygame.draw.rect(Surface, GRASS, CellRect)
                elif Value == 3:
                    pygame.draw.rect(Surface, STONE, CellRect)

        scaled_surface = pygame.transform.scale(Surface, (int(WORLD_SIZE * CELL_SIZE * self.ZoomLevel), int(WORLD_SIZE * CELL_SIZE * self.ZoomLevel)))
        self.Screen.blit(scaled_surface, (GridX, GridY))

        pygame.display.flip()

def Main() -> None:
    pygame.init()

    m_Game = Game()

    while m_Game.Running:
        m_Game.HandleEvents()
        m_Game.Update()
        m_Game.Render()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    Main()
