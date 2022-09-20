import pygame, sys
from pygame.locals import QUIT

pygame.init()

size = width, height = 960, 672  #window size
screen = pygame.Surface((320, 224))
display = pygame.display.set_mode(size)
pygame.display.set_caption("Dodgem")  #window title

clock = pygame.time.Clock()
"""
TODO:
    *BUG: distortion in distance
    *optimise to reduce lag
    *background
    *curves
    *hills
    *points
    *enemy cars
    *game over on collision with cars or road
    *random track
"""


class Player:
    #set up player variables
    X = 0
    speed = 0
    maxSpeed = 5
    accel = maxSpeed / 3
    brakingDecel = -maxSpeed
    decel = -maxSpeed / 3
    offRoadDecel = -maxSpeed / 2
    offRoadLimit = maxSpeed / 4
    accelerating = False
    braking = False
    drivingLeft = False
    drivingRight = False
    images = [
        pygame.image.load("Assets/player_straight.png").convert_alpha(),
        pygame.image.load("Assets/player_left.png").convert_alpha(),
        pygame.image.load("Assets/player_right.png").convert_alpha()
    ]
    image = images[0]

    def update():
        dx = Game.dt * (Player.speed / Player.maxSpeed)

        if Player.drivingLeft:
            Player.X = Player.X - dx
        elif Player.drivingRight:
            Player.X = Player.X + dx

        if Player.accelerating:
            Player.speed = Player.speed + (Player.accel * Game.dt)
        elif Player.braking:
            Player.speed = Player.speed + (Player.brakingDecel * Game.dt)
        else:
            Player.speed = Player.speed + (Player.decel * Game.dt)

        if (Player.X < -1
                or Player.X > 1) and Player.speed > Player.offRoadLimit:
            Player.speed = Player.speed + (Player.offRoadDecel * Game.dt
                                           )  #slower when offroad
        Player.X = -1.5 if Player.X < -1.5 else 1.5 if Player.X > 1.5 else Player.X  #player can't go too far offroad
        Player.speed = 0 if Player.speed < 0 else Player.maxSpeed if Player.speed > Player.maxSpeed else Player.speed  #speed limited to maxSpeed

        if Player.drivingLeft == True:
            Player.image = Player.images[1]
        elif Player.drivingRight == True:
            Player.image = Player.images[2]
        else:
            Player.image = Player.images[0]

        Player.image = pygame.transform.scale2x(Player.image)
        rect = Player.image.get_rect()
        screen.blit(Player.image,
                    (width / 2 - rect.width / 2, height - 20 - rect.height))


class Background:

    def update():
        pass


class Camera:

    Z = 0
    height = 400

    def update():
        Camera.Z = Camera.Z + Game.dt * Player.speed  #move camera forwards
        #if Camera.Z >= Road.trackLength:
        #Camera.Z -= Road.trackLength  #loop track when finished


class Road:

    width = width * 1.6
    groundColors = [(23, 138, 0), (31, 176, 2)]
    roadColors = [(140, 140, 140), (120, 120, 120)]
    curbColors = [(255, 255, 255), (224, 16, 16)]
    laneColor = (255, 255, 255)
    zMap = []
    lanes = 4
    laneMarkerWidth = 10
    curbWidth = 50
    textureOffset = 0

    def update():
        Road.textureOffset += Game.dt * Player.speed
        if Road.textureOffset > 2:
            Road.textureOffset -= 2
        Road.Zmap = []
        for i in range(int(height / 2)):
            Z = (-1 * Camera.height) / (i - (height / 2))
            scale = (1 / Z)
            w = Road.width * scale
            colorIndex = 0
            if (Z + Road.textureOffset) % 2 > 1:
                colorIndex += 1
            Road.Zmap.append({
                "Z": Z,
                "scale": scale,
                "w": w,
                "colorIndex": colorIndex,
                "screen_y": height - i
            })

        for l in Road.Zmap:
            Xoffset = -1 * (Player.X * l["w"]) / 2
            cw = Road.curbWidth * l["scale"]
            middle = width / 2 + Xoffset
            halfRoadW = l["w"] / 2
            pygame.draw.line(screen, Road.groundColors[l["colorIndex"]],
                             (0, l["screen_y"]),
                             (width, l["screen_y"]))  #grass
            pygame.draw.line(screen, Road.roadColors[l["colorIndex"]],
                             (middle - halfRoadW, l["screen_y"]),
                             (middle + halfRoadW, l["screen_y"]))  #road
            pygame.draw.line(screen, Road.curbColors[l["colorIndex"]],
                             (middle - halfRoadW - cw, l["screen_y"]),
                             (middle - halfRoadW, l["screen_y"]))  #curbR
            pygame.draw.line(screen, Road.curbColors[l["colorIndex"]],
                             (middle + halfRoadW, l["screen_y"]),
                             (middle + halfRoadW + cw, l["screen_y"]))  #curbL

            if l["colorIndex"] == 1:
                for i in range(Road.lanes - 1):
                    x = (l["w"] / Road.lanes * (i + 1))
                    w = Road.laneMarkerWidth * l["scale"]
                    pygame.draw.line(
                        screen, Road.laneColor,
                        (middle - halfRoadW + x - w / 2, l["screen_y"]),
                        (middle - halfRoadW + x + w / 2, l["screen_y"]))


class Game:

    fps = 30
    dt = int(1 / fps * 1000)  #change in time between frames

    def handleInput():  #map keys to controls
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    Player.drivingLeft = True
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    Player.drivingRight = True
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    Player.accelerating = True
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    Player.braking = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    Player.drivingLeft = False
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    Player.drivingRight = False
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    Player.accelerating = False
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    Player.braking = False

    def updateFrame():
        global screen
        screen.fill((0, 0, 0))
        Game.dt = clock.get_time() / 1000  #change in time between frames
        Background.update()
        Camera.update()
        Road.update()
        Player.update()
        #print(Player.speed,Player.X,Camera.Z)
        screen = pygame.transform.scale(screen, (960, 672))
        display.blit(screen, (0, 0))
        pygame.display.flip()  #draw to display


while True:
    clock.tick(Game.fps)  #run game loop at max fps
    Game.handleInput()
    Game.updateFrame()
