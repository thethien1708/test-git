import pygame
import math

# --- Hằng số ---
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# --- Lớp Ball ---
class Ball:
    def __init__(self, x, y, radius, color, vx=0, vy=0):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = vx
        self.vy = vy

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def apply_gravity(self, gravity, dt):
        self.vy += gravity * dt

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# --- Lớp Hexagon ---
class Hexagon:
    def __init__(self, center_x, center_y, side_length, color, rotation_speed=0):
        self.center_x = center_x
        self.center_y = center_y
        self.side_length = side_length
        self.color = color
        self.rotation_angle = 0  # radians
        self.rotation_speed = rotation_speed # radians per second

    def get_vertices(self):
        vertices = []
        for i in range(6):
            angle_deg = 60 * i + self.rotation_angle * 180 / math.pi
            angle_rad = math.radians(angle_deg)
            x = self.center_x + self.side_length * math.cos(angle_rad)
            y = self.center_y + self.side_length * math.sin(angle_rad)
            vertices.append((x, y))
        return vertices

    def get_edges(self):
        vertices = self.get_vertices()
        edges = []
        for i in range(6):
            edges.append((vertices[i], vertices[(i + 1) % 6]))
        return edges

    def update(self, dt):
        self.rotation_angle += self.rotation_speed * dt
        self.rotation_angle %= (2 * math.pi) # Keep angle within 0 to 2*pi

    def draw(self, surface):
        vertices = self.get_vertices()
        pygame.draw.polygon(surface, self.color, vertices, 2) # Draw outline

# --- Lớp PhysicsEngine ---
class PhysicsEngine:
    def __init__(self, gravity=9.81):
        self.gravity = gravity

    def update(self, ball, hexagon, dt):
        ball.apply_gravity(self.gravity, dt)
        ball.update(dt)
        hexagon.update(dt)
        self._check_and_handle_collisions(ball, hexagon)

    def _check_and_handle_collisions(self, ball, hexagon):
        ball_pos = pygame.math.Vector2(ball.x, ball.y)
        
        for edge_start, edge_end in hexagon.get_edges():
            p1 = pygame.math.Vector2(edge_start)
            p2 = pygame.math.Vector2(edge_end)

            # Vector của cạnh
            edge_vec = p2 - p1
            
            # Vector từ điểm bắt đầu cạnh đến tâm bóng
            ball_to_p1 = ball_pos - p1

            # Chiếu vector ball_to_p1 lên edge_vec để tìm điểm gần nhất trên đường thẳng
            # t là tham số trên đường thẳng (0 <= t <= 1 nếu điểm nằm trên đoạn thẳng)
            if edge_vec.length_squared() == 0: # Tránh chia cho 0 nếu cạnh có độ dài 0
                continue
            t = ball_to_p1.dot(edge_vec) / edge_vec.length_squared()
            
            # Giới hạn t trong khoảng [0, 1] để tìm điểm gần nhất trên đoạn thẳng
            t = max(0, min(1, t))
            
            # Điểm gần nhất trên cạnh
            closest_point = p1 + t * edge_vec
            
            # Vector từ tâm bóng đến điểm gần nhất
            normal_vec = ball_pos - closest_point
            
            distance = normal_vec.length()

            if distance < ball.radius:
                # Va chạm xảy ra
                # Đẩy bóng ra khỏi cạnh để tránh bị kẹt
                overlap = ball.radius - distance
                if distance != 0: # Tránh chia cho 0
                    ball_pos += normal_vec.normalize() * overlap
                    ball.x, ball.y = ball_pos.x, ball_pos.y

                # Tính toán phản xạ
                if normal_vec.length() == 0: # Nếu tâm bóng trùng với điểm gần nhất (trường hợp hiếm)
                    normal_vec = pygame.math.Vector2(0, 1) # Chọn một vector pháp tuyến mặc định
                else:
                    normal_vec = normal_vec.normalize()

                # Vận tốc tương đối của bóng so với cạnh (nếu cạnh đứng yên)
                # Ở đây cạnh lục giác xoay, nhưng để đơn giản, ta coi cạnh là đứng yên tại thời điểm va chạm
                # Để xử lý va chạm với cạnh xoay phức tạp hơn, cần tính vận tốc điểm va chạm trên cạnh
                
                ball_vel = pygame.math.Vector2(ball.vx, ball.vy)
                
                # Thành phần vận tốc vuông góc với cạnh
                dot_product = ball_vel.dot(normal_vec)
                
                # Vận tốc sau va chạm (phản xạ đàn hồi)
                reflected_vel = ball_vel - 2 * dot_product * normal_vec
                
                ball.vx = reflected_vel.x
                ball.vy = reflected_vel.y

# --- Lớp Game ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Mô phỏng quả bóng trong lục giác")
        self.clock = pygame.time.Clock()
        self.running = True

        # Khởi tạo các đối tượng game
        self.ball = Ball(WIDTH // 2, HEIGHT // 4, 15, RED, vx=50, vy=0)
        self.hexagon = Hexagon(WIDTH // 2, HEIGHT // 2, 150, BLUE, rotation_speed=0.5) # 0.5 rad/s
        self.physics_engine = PhysicsEngine(gravity=500) # Tăng trọng lực để thấy rõ hiệu ứng

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, dt):
        self.physics_engine.update(self.ball, self.hexagon, dt)

    def render(self):
        self.screen.fill(BLACK)
        self.hexagon.draw(self.screen)
        self.ball.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Thời gian trôi qua giữa các khung hình (giây)
            self.handle_events()
            self.update(dt)
            self.render()

        pygame.quit()

def do_nothing():
    print("do nothing")
    
if __name__ == "__main__":
    game = Game()
    game.run()