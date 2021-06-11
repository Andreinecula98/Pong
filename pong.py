import sys
import pygame


class Ball:
    def __init__(self, screen, color, posX, posY, radius):
        self.screen = screen
        self.color = color
        self.posX = posX
        self.posY = posY
        self.radius = radius
        self.dx = 0
        self.dy = 0
        self.show()

    def show(self):
        pygame.draw.circle(self.screen, self.color, (self.posX, self.posY), self.radius)

    def start_moving(self):
        self.dx = 10
        self.dy = 5

    def move_player1(self):
        self.posX += self.dx
        self.posY += self.dy

    def move_player2(self):
        self.posX -= self.dx
        self.posY -= self.dy

    def paddle_collision(self):
        self.dx = -self.dx

    def wall_collision(self):
        self.dy = -self.dy

    def restart_pos(self):
        self.posX = WIDTH // 2
        self.posY = HEIGHT // 2
        self.dx = 0
        self.dy = 0
        self.show()


class Paddle:
    def __init__(self, screen, color, posX, posY, width, height):
        self.screen = screen
        self.color = color
        self.posX = posX
        self.posY = posY
        self.width = width
        self.height = height
        self.state = 'stopped'
        self.show()

    def show(self):
        pygame.draw.rect(self.screen, self.color, (self.posX, self.posY, self.width, self.height))

    def move(self):
        if self.state == 'up':
            self.posY -= 10
        elif self.state == 'down':
            self.posY += 10

    def clamp(self):
        if self.posY <= 0:
            self.posY = 0
        if self.posY >= HEIGHT - self.height:
            self.posY = HEIGHT - self.height

    def restart_pos(self):
        self.posY = HEIGHT // 2 - self.height // 2
        self.state = 'stopped'
        self.show()


class CollisionManager:
    def between_ball_and_paddle1(self, ball, paddle1):
        if ball.posY + ball.radius > paddle1.posY and ball.posY - ball.radius < paddle1.posY + paddle1.height:
            if ball.posX - ball.radius <= paddle1.posX + paddle1.width:
                return True
        return False

    def between_ball_and_paddle2(self, ball, paddle2):
        if ball.posY + ball.radius > paddle2.posY and ball.posY - ball.radius < paddle2.posY + paddle2.height:
            if ball.posX + ball.radius >= paddle2.posX:
                return True
        return False

    def between_ball_and_walls(self, ball):
        if ball.posY - ball.radius <= 0:
            return True

        if ball.posY + ball.radius >= HEIGHT:
            return True

    def check_goal_player1(self, ball):
        if ball.posX - ball.radius >= WIDTH:
            return True

    def check_goal_player2(self, ball):
        if ball.posX + ball.radius <= 0:
            return True


class Score:
    def __init__(self, screen, points, posX, posY):
        self.screen = screen
        self.points = points
        self.posX = posX
        self.posY = posY
        self.font = pygame.font.SysFont("monospace", 80, bold=True)
        self.label = self.font.render(self.points, False, WHITE)
        self.show()

    def show(self):
        self.screen.blit(self.label, (self.posX - self.label.get_rect().width // 2, self.posY))

    def increase(self):
        points = int(self.points) + 1
        self.points = str(points)
        self.label = self.font.render(self.points, False, WHITE)

    def restart(self):
        self.points = '0'
        self.label = self.font.render(self.points, False, WHITE)


pygame.init()
pygame.joystick.init()
joysticks = []
motion = [0, 0]
WIDTH = 1400
HEIGHT = 850
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
clock = pygame.time.Clock()
fps = 30
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('PONG')


def paint_black():
    screen.fill(BLACK)
    pygame.draw.line(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 5)


def restart():
    paint_black()
    score1.restart()
    score2.restart()
    ball.restart_pos()
    paddle1.restart_pos()
    paddle2.restart_pos()


paint_black()

# OBJECTS
ball = Ball(screen, WHITE, WIDTH // 2, HEIGHT // 2, 15)
paddle1 = Paddle(screen, WHITE, 15, HEIGHT // 2 - 60, 20, 120)
paddle2 = Paddle(screen, WHITE, WIDTH - 20 - 15, HEIGHT // 2 - 60, 20, 120)
collision = CollisionManager()
score1 = Score(screen, '0', WIDTH // 4, 15)
score2 = Score(screen, '0', WIDTH - WIDTH // 4, 15)

playing = False
for i in range(pygame.joystick.get_count()):
    joysticks.append((pygame.joystick.Joystick(i)))
    joysticks[-1].init()
if abs(motion[1]) < 0.1:
    motion[1] = 0
# mainloop
while True:
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:
                sys.exit()
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 10:
                ball.start_moving()
                playing = True
            if event.button == 9:
                restart()
        if event.type == pygame.JOYAXISMOTION:
            if event.value < 0:
                paddle1.state = 'up'
            if event.value > 0.5:
                paddle1.state = 'down'
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 6:
                paddle2.state = 'up'
            if event.button == 5:
                paddle2.state = 'down'
        if event.type == pygame.JOYBUTTONUP:
            paddle1.state = 'stopped'
            paddle2.state = 'stopped'

    if playing:
        paint_black()
        if int(score1.points) < int(score2.points):
            ball.move_player1()
        else:
            ball.move_player2()
        ball.show()

        paddle1.move()
        paddle1.clamp()
        paddle1.show()

        paddle2.move()
        paddle2.clamp()
        paddle2.show()

        # check for collisions
        if collision.between_ball_and_paddle1(ball, paddle1):
            ball.paddle_collision()

        if collision.between_ball_and_paddle2(ball, paddle2):
            ball.paddle_collision()

        if collision.between_ball_and_walls(ball):
            ball.wall_collision()
        if collision.check_goal_player1(ball):
            paint_black()
            score1.increase()
            ball.restart_pos()
            paddle1.restart_pos()
            paddle2.restart_pos()
        if collision.check_goal_player2(ball):
            paint_black()
            score2.increase()
            ball.restart_pos()
            paddle1.restart_pos()
            paddle2.restart_pos()
    score1.show()
    score2.show()

    pygame.display.update()
