import pygame
import random
import sys
import math
import array

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 90
BALL_SIZE = 15
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

class PongGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=1)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("PONG - Player vs AI")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 32)
        self.large_font = pygame.font.SysFont("Arial", 64)
        
        # Sound effects generation
        self.sounds = self._generate_sounds()
        
        self.reset_game()
        self.running = True
        self.paused = True
        self.game_started = False
        self.last_message = ""
        self.message_timer = 0
        
        # AI Properties
        self.ai_difficulty = 1
        self.ai_reaction_counter = 0
        self.ai_target_y = HEIGHT // 2

    def _generate_sounds(self):
        sounds = {}
        sample_rate = 44100
        duration = 0.1
        n_samples = int(sample_rate * duration)

        def create_beep(freq):
            buf = array.array('h', [0] * n_samples)
            for i in range(n_samples):
                t = i / sample_rate
                buf[i] = int(32767 * math.sin(2 * math.pi * freq * t))
            sound = pygame.mixer.Sound(buffer=buf)
            return sound

        sounds['hit'] = create_beep(440)
        sounds['bounce'] = create_beep(330)
        sounds['score'] = create_beep(880)
        return sounds

    def reset_game(self):
        self.player_paddle = pygame.Rect(30, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.ai_paddle = pygame.Rect(WIDTH - 30 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)
        self.ball_dx = random.choice([-5, 5])
        self.ball_dy = random.uniform(-4, 4)
        self.player_score = 0
        self.ai_score = 0
        self.base_speed = 5
        self.current_ball_speed = self.base_speed

    def reset_ball(self):
        self.ball.center = (WIDTH//2, HEIGHT//2)
        self.ball_dx = random.choice([-1, 1]) * self.current_ball_speed
        self.ball_dy = random.uniform(-3, 3)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_started:
                        self.game_started = True
                    self.paused = not self.paused

        if not self.paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.player_paddle.y -= 7
            if keys[pygame.K_DOWN]:
                self.player_paddle.y += 7
            
            # Clamp player paddle
            self.player_paddle.top = max(0, self.player_paddle.top)
            self.player_paddle.bottom = min(HEIGHT, self.player_paddle.bottom)

    def update(self):
        if self.paused or not self.game_started:
            return

        # Ball movement
        self.ball.x += self.ball_dx
        self.ball.y += self.ball_dy

        # Wall collisions (top/bottom)
        if self.ball.top <= 0 or self.ball.bottom >= HEIGHT:
            self.ball_dy *= -1
            self.sounds['bounce'].play()

        # Paddle collisions
        for paddle in [self.player_paddle, self.ai_paddle]:
            if self.ball.colliderect(paddle):
                # 1. Ball tunneling prevention (clamping)
                if paddle == self.player_paddle:
                    self.ball.left = paddle.right
                else:
                    self.ball.right = paddle.left

                # 3. Paddle collision angle (change based on impact point)
                relative_intersect = (paddle.centery - self.ball.centery)
                normalized_intersect = relative_intersect / (PADDLE_HEIGHT / 2)
                bounce_angle = normalized_intersect * (3.14159 / 4) # Max 45 degrees
                self.ball_dx *= -1.05
                self.ball_dy = -bounce_angle * self.current_ball_speed
                
                # Clamp speed
                max_speed = 15
                if abs(self.ball_dx) > max_speed:
                    self.ball_dx = (max_speed if self.ball_dx > 0 else -max_speed)
                
                self.sounds['hit'].play()

        # 2. Better AI randomness/logic
        self.ai_reaction_counter += 1
        reaction_delay = max(1, 10 - (self.ai_difficulty // 2)) # Harder = less delay
        
        if self.ai_reaction_counter >= reaction_delay:
            self.ai_reaction_counter = 0
            # AI predicts trajectory if ball moving toward it
            if self.ball_dx < 0:
                # Moving towards player, drift to center
                target_y = HEIGHT // 2
            else:
                # Moving towards AI, try to predict
                # Simple prediction: where will ball be at paddle X?
                time_to_reach = (self.ai_paddle.left - self.ball.centerx) / self.ball_dx
                predicted_y = self.ball.centery + (self.ball_dy * time_to_reach)
                target_y = predicted_y

            # Add positional error that decreases with difficulty
            error = max(0, 50 - (self.ai_difficulty * 5))
            self.ai_target_y = target_y + random.uniform(-error, error)

        # AI movement speed cap and clamping
        ai_speed = 4 + (self.ai_difficulty * 0.8)
        if self.ai_paddle.centery < self.ai_target_y:
            self.ai_paddle.y += ai_speed
        elif self.ai_paddle.centery > self.ai_target_y:
            self.ai_paddle.y -= ai_speed
        
        # 7. Prevent paddle from going off screen
        self.ai_paddle.top = max(0, self.ai_paddle.top)
        self.ai_paddle.bottom = min(HEIGHT, self.ai_paddle.bottom)

        # Scoring
        if self.ball.left <= 0:
            self.ai_score += 1
            self._handle_score("AI SCORED!")
            self.update_difficulty()
            self.reset_ball()
        elif self.ball.right >= WIDTH:
            self.player_score += 1
            self._handle_score("PLAYER SCORED!")
            self.update_difficulty()
            self.reset_ball()

        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1

    def _handle_score(self, msg):
        self.last_message = msg
        self.message_timer = 90 # ~1.5 seconds at 60FPS
        self.sounds['score'].play()

    def update_difficulty(self):
        self.ai_difficulty = 1 + (self.player_score // 2)
        self.current_ball_speed = self.base_speed + (self.player_score * 0.5)

    def draw(self):
        self.screen.fill(BLACK)

        # Draw dashed center line
        dash_len = 20
        for y in range(0, HEIGHT, dash_len * 2):
            pygame.draw.line(self.screen, GRAY, (WIDTH//2, y), (WIDTH//2, y + dash_len), 2)

        # Draw Paddles and Ball
        pygame.draw.rect(self.screen, WHITE, self.player_paddle)
        pygame.draw.rect(self.screen, WHITE, self.ai_paddle)
        # 5. Draw ball as circle
        pygame.draw.circle(self.screen, WHITE, self.ball.center, BALL_SIZE // 2)

        # Draw Scores (5. Rounded positioning)
        score_text = self.font.render(f"{self.player_score}   {self.ai_score}", True, WHITE)
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 40))

        # Draw AI Difficulty
        diff_text = self.font.render(f"AI Level: {self.ai_difficulty}", True, GRAY)
        self.screen.blit(diff_text, (20, 20))

        # Draw messages after score
        if self.message_timer > 0:
            msg_overlay = self.font.render(self.last_message, True, WHITE)
            self.screen.blit(msg_overlay, (WIDTH // 2 - msg_overlay.get_width() // 2, HEIGHT // 2 + 50))

        # Draw Start/Pause Overlay
        if not self.game_started:
            overlay = self.large_font.render("Press SPACE to start", True, WHITE)
            self.screen.blit(overlay, (WIDTH // 2 - overlay.get_width() // 2, HEIGHT // 2 - 50))
        elif self.paused:
            overlay = self.large_font.render("PAUSED", True, GRAY)
            self.screen.blit(overlay, (WIDTH // 2 - overlay.get_width() // 2, HEIGHT // 2 - 50))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = PongGame()
    game.run()
