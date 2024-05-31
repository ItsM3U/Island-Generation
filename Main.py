import sys
import pygame
import noise
import random
import math

WIDTH, HEIGHT = 640, 640
TITLE = "Insula"
FPS = 60

NOISE_SCALE = 100.0
ENVIRONMENT_SIZE = 128

FILL = (0, 0, 0)
BLACK = (15, 15, 15)
GRAY = (45, 45, 45)
WHITE = (240, 240, 240)

class Game:
    def __init__(self):
        pygame.init()
        self.Screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.Clock = pygame.time.Clock()
        self.Keys = pygame.key.get_pressed()
        pygame.display.set_caption(TITLE)
        self.Running = True
        self.Seed = self.GenerateSeed()
        self.IslandMap = self.GenerateIsland()

    def GenerateSeed(self):
        return random.randint(0, 1000)

    def GenerateIsland(self):
        IslandMap = []

        for y in range(ENVIRONMENT_SIZE):
            Row = []
            for x in range(ENVIRONMENT_SIZE):
                DistanceToCenter = math.sqrt((x - 64) ** 2 + (y - 64) ** 2)
                ScaledDistance = DistanceToCenter / (ENVIRONMENT_SIZE / math.sqrt(2))
                Value = noise.snoise2(x / NOISE_SCALE, y / NOISE_SCALE, octaves=8, persistence=0.6, lacunarity=2.0, repeatx=1024, repeaty=1024, base=self.Seed)
                Row.append(Value > ScaledDistance)
            IslandMap.append(Row)

        if sum(sum(Row) for Row in IslandMap) < 1000:
            self.Seed += 1
            return self.GenerateIsland()

        return IslandMap

    def HandleInput(self):
        self.Keys = pygame.key.get_pressed()

        if self.Keys[pygame.K_ESCAPE]:
            self.Running = False

    def HandleEvents(self):
        for Event in pygame.event.get():
            if Event.type == pygame.QUIT:
                self.Running = False

    def Update(self):
        self.HandleInput()
        pygame.display.flip()
        self.Clock.tick(FPS)
        pygame.display.set_caption(f"{TITLE} - FPS: {int(self.Clock.get_fps())} - Seed: {self.Seed}")

    def Render(self):
        self.Screen.fill(FILL)

        BlockSize = 5
        OffsetX = (WIDTH - ENVIRONMENT_SIZE * BlockSize) // 2
        OffsetY = (HEIGHT - ENVIRONMENT_SIZE * BlockSize) // 2

        for y in range(ENVIRONMENT_SIZE):
            for x in range(ENVIRONMENT_SIZE):
                Color = WHITE if self.IslandMap[y][x] else BLACK
                pygame.draw.rect(self.Screen, Color,
                                 (OffsetX + x * BlockSize, OffsetY + y * BlockSize, BlockSize, BlockSize), 0)
                pygame.draw.rect(self.Screen, GRAY,
                                 (OffsetX + x * BlockSize, OffsetY + y * BlockSize, BlockSize, BlockSize), 1)

        pygame.display.flip()


def Main() -> None:
    m_Game = Game()

    while m_Game.Running:
        m_Game.HandleEvents()
        m_Game.Update()
        m_Game.Render()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    Main()
