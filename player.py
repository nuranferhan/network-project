from roles import load_character_frames
from gameconfig import *

class Player:
    # Tüm karakterler için animasyon framelerini sınıf değişkeni olarak yükle
    ANIMATIONS = None

    def __init__(self, x, y, color, role=None):
        self.x = x - CHARACTER_WIDTH / 2
        self.y = y - CHARACTER_HEIGHT / 2
        self.color = color

        # Color'a göre role belirleme
        if role is None:
            if self.color == (255, 255, 0):  # Yellow
                self.role = 'cop'
            elif self.color == (255, 0, 0):  # Red
                self.role = 'thief'
            else:
                self.role = 'cop'  # Varsayılan
        else:
            self.role = role

        self.width = CHARACTER_WIDTH
        self.height = CHARACTER_HEIGHT
        self.vel = PLAYER_VELOCITY
        self.default_vel = self.vel  # Boost sonrası geri dönebilmek için
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Animasyon için ek değişkenler
        self.direction = 'right'  # Varsayılan yön
        self.moving = False
        self.current_frame = 0
        self.animation_speed = 0.2  # Her frame için geçecek saniye
        self.last_update = 0
        self.caught = False  # Yakalanma durumu

        # İlk kez bir Player instance'ı oluşturulduğunda animasyonları yükle
        if Player.ANIMATIONS is None:
            Player.ANIMATIONS = load_character_frames()

        # Frame'ler için gerekli boyutları ayarla
        self.resize_frames()

    def resize_frames(self):
        """Tüm frame'leri oyuncu boyutuna göre ölçeklendirir."""
        for direction in Player.ANIMATIONS[self.role]:
            for i, frame in enumerate(Player.ANIMATIONS[self.role][direction]):
                # Frame'leri daha büyük boyutlarda ölçeklendir
                Player.ANIMATIONS[self.role][direction][i] = pygame.transform.scale(
                    frame, (self.width, self.height)
                )

    @classmethod
    def from_absolute_pos(cls, x, y, color, role=None, caught=False, direction='right', moving=False):
        player = cls.__new__(cls)
        player.x = x
        player.y = y
        player.color = color

        # Color'a göre role belirleme
        if role is None:
            if player.color == (255, 255, 0):  # Yellow
                player.role = 'cop'
            elif player.color == (255, 0, 0):  # Red
                player.role = 'thief'
            else:
                player.role = 'cop'
        else:
            player.role = role

        player.width = CHARACTER_WIDTH
        player.height = CHARACTER_HEIGHT
        player.vel = PLAYER_VELOCITY
        player.default_vel = PLAYER_VELOCITY
        player.rect = pygame.Rect(x, y, player.width, player.height)

        # Animasyon için ek değişkenler
        player.direction = direction  # Dışarıdan alınan yön
        player.moving = moving  # Dışarıdan alınan hareket durumu
        player.current_frame = 0
        player.animation_speed = ANIMATION_SPEED  # Her frame için geçecek saniye
        player.last_update = pygame.time.get_ticks()
        player.caught = caught  # Yakalanma durumu

        # İlk kez bir Player instance'ı oluşturulduğunda animasyonları yükle
        if Player.ANIMATIONS is None:
            Player.ANIMATIONS = load_character_frames()

        # Frame'ler için gerekli boyutları ayarla
        player.resize_frames()

        return player

    def update_rect(self):
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        # Karakterin rolünü kontrol et ve uygun animasyonu göster
        if self.role not in Player.ANIMATIONS:
            # Rol için animasyon yoksa sadece renkli dikdörtgen çiz
            pygame.draw.rect(surface, self.color, self.rect)
            return

        # Normal hareket animasyonları
        if self.moving:
            # Doğru frame'i seç ve çiz
            current_animation = Player.ANIMATIONS[self.role][self.direction]
            if self.current_frame >= len(current_animation):
                self.current_frame = 0

            current_image = current_animation[int(self.current_frame)]
            surface.blit(current_image, (self.x, self.y))

            # Frame'i güncelle
            now = pygame.time.get_ticks()
            if now - self.last_update > self.animation_speed * 1000:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(current_animation)
        else:
            # Hareket etmiyorsa ilk frame'i göster
            if self.direction in Player.ANIMATIONS[self.role] and len(Player.ANIMATIONS[self.role][self.direction]) > 0:
                surface.blit(Player.ANIMATIONS[self.role][self.direction][0], (self.x, self.y))
            else:
                # Fallback: Eğer animasyon yoksa orijinal dikdörtgeni çiz
                pygame.draw.rect(surface, self.color, self.rect)

    def move(self, walls):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        self.moving = False  # Hareket durumunu sıfırla

        if keys[pygame.K_LEFT]:
            dx = -self.vel
            self.direction = 'left'
            self.moving = True
        elif keys[pygame.K_RIGHT]:
            dx = self.vel
            self.direction = 'right'
            self.moving = True
        if keys[pygame.K_UP]:
            dy = -self.vel
            self.moving = True
        elif keys[pygame.K_DOWN]:
            dy = self.vel
            # Aşağı animasyon yoksa son kullanılan yön animasyonunu kullan
            self.moving = True

        if dx != 0:
            self.x += dx
            self.update_rect()
            for wall in walls:
                if self.rect.colliderect(wall):
                    if dx > 0:
                        self.rect.right = wall.left
                    elif dx < 0:
                        self.rect.left = wall.right
                    self.x = self.rect.x
                    continue

        if dy != 0:
            self.y += dy
            self.update_rect()
            for wall in walls:
                if self.rect.colliderect(wall):
                    if dy > 0:
                        self.rect.bottom = wall.top
                    elif dy < 0:
                        self.rect.top = wall.bottom
                    self.y = self.rect.y
                    continue

        self.update_rect()

    # === BOOST EKLENTİLERİ ===
    def speed_boost(self, multiplier, duration):
        self.vel *= multiplier
        self.boost_end_time = pygame.time.get_ticks() + duration * 1000

    def update(self):
        if hasattr(self, "boost_end_time") and pygame.time.get_ticks() > self.boost_end_time:
            self.vel = self.default_vel
            del self.boost_end_time