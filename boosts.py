import os
from gameconfig import *

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Animasyon bilgileri
BOOST_TYPES = {
    "diamond": {
        "folder": "assets/diamond",
        "frame_count": 10,  # 10 frame var
        "delay": 0.07,  # Frame başına gecikme süresi
        "count": 5,  # Oyunda kaç tane olacak
        "score": 10
    },
    "money": {
        "folder": "assets/money",
        "frame_count": 40,  # 40 frame var
        "delay": 0.05,  # Frame başına gecikme süresi
        "count": 3,  # Oyunda kaç tane olacak
        "score": 5
    },
    "energy": {
        "folder": "assets/energy",
        "frame_count": 14,  # 14 frame var
        "delay": 0.08,  # Frame başına gecikme süresi
        "count": 2,  # Oyunda kaç tane olacak
        "speed_boost": 1.5,
        "duration": 5
    },
    "portal1": {
        "folder": "assets/portal1",
        "frame_count": 6,
        "delay": 0.05,  # Frame başına gecikme süresi
        "count": 1,  # Oyunda 1 tane olacak
        "teleport_to": "portal2"  # Bu portalın ışınlayacağı diğer portal
    },
    "portal2": {
        "folder": "assets/portal2",
        "frame_count": 6,
        "delay": 0.05,  # Frame başına gecikme süresi
        "count": 1,  # Oyunda 1 tane olacak
        "teleport_to": "portal1"  # Bu portalın ışınlayacağı diğer portal
    },
}



class Boost:
    def __init__(self, boost_id, boost_type, x, y):
        self.id = boost_id
        self.type = boost_type
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, BOOST_EDGE, BOOST_EDGE)

        # Animasyon değişkenleri
        self.frames = []
        self.current_frame = 0
        self.frame_delay = int(BOOST_TYPES[boost_type]["delay"] * 1000)  # Milisaniyeye çevir
        self.last_update = 0  # İlk frame'i göstermek için başlangıçta 0

        # Frame'leri yükle
        self.load_frames(boost_type)

        self.active = True
        self.start_time = None  # For energy

    def load_frames(self, boost_type):
        folder = BOOST_TYPES[boost_type]["folder"]
        frame_count = BOOST_TYPES[boost_type]["frame_count"]

        for i in range(frame_count):
            # Frame adını oluştur (frame_00_delay-0.07s.gif gibi)
            frame_name = f"frame_{i:02d}_delay-{BOOST_TYPES[boost_type]['delay']}s.gif"
            frame_path = os.path.join(folder, frame_name)

            # Resmi yükle ve ölçeklendir
            try:
                image = pygame.image.load(frame_path)
                image = pygame.transform.scale(image, (BOOST_EDGE, BOOST_EDGE))
                self.frames.append(image)
            except pygame.error as e:
                print(f"Resim yüklenirken hata: {e} - {frame_path}")

        # En az bir kare olduğundan emin ol
        if not self.frames:
            # Yedek olarak boş bir yüzey oluştur
            empty_surface = pygame.Surface((BOOST_EDGE, BOOST_EDGE), pygame.SRCALPHA)
            empty_surface.fill((255, 0, 255, 128))  # Mor yarı saydam (hata gösterimi)
            self.frames.append(empty_surface)

    def update_animation(self):
        # Animasyonu güncelle
        now = pygame.time.get_ticks()
        elapsed = now - self.last_update

        if elapsed > self.frame_delay:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    @property
    def image(self):
        # Güncel frame'i döndür
        if not self.frames:
            # Herhangi bir frame yoksa boş bir yüzey döndür
            empty_surface = pygame.Surface((BOOST_EDGE, BOOST_EDGE), pygame.SRCALPHA)
            empty_surface.fill((255, 0, 255, 128))  # Mor yarı saydam (hata gösterimi)
            return empty_surface
        return self.frames[self.current_frame]


class BoostManager:
    def __init__(self, walls, width, height, server_boosts=None):
        # Portallerin birbirlerine referans edebilmesi için (önce oluştur)
        self.portal_pairs = {}
        # Teleport için cooldown takibi
        self.last_teleport_time = 0
        # Animasyon zamanlaması için son güncelleme zamanı
        self.last_animation_update = pygame.time.get_ticks()
        # Boost listesi
        self.boosts = []

        # Server'dan boost verileri geldi mi?
        if server_boosts:
            self.create_boosts_from_server(server_boosts)

        # Portalları birbiriyle eşleştir
        self._link_portals()

    def create_boosts_from_server(self, server_boosts):
        """Server'dan gelen boost verilerini kullanarak boostları oluştur"""
        for boost_data in server_boosts:
            boost_id = boost_data["id"]
            boost_type = boost_data["type"]
            x = boost_data["x"]
            y = boost_data["y"]

            self.boosts.append(Boost(boost_id, boost_type, x, y))

        print(f"Created {len(self.boosts)} boosts from server data")



    def _link_portals(self):
        """Portal1 ve portal2 arasında bağlantı kur"""
        portal1 = None
        portal2 = None

        # Portalları bul
        for boost in self.boosts:
            if boost.type == "portal1" and boost.active:
                portal1 = boost
            elif boost.type == "portal2" and boost.active:
                portal2 = boost

        # Eğer her iki portal da bulunduysa eşleştir
        if portal1 and portal2:
            self.portal_pairs["portal1"] = portal2
            self.portal_pairs["portal2"] = portal1

    def update(self):
        # Her framede tüm boost animasyonlarını güncelle
        now = pygame.time.get_ticks()
        for boost in self.boosts:
            if boost.active:
                boost.update_animation()

    def draw(self, surface):
        # Çizim yapmadan önce tüm animasyonları güncelle - önemli!
        self.update()

        # Boostları çiz
        for boost in self.boosts:
            if boost.active:
                surface.blit(boost.image, (boost.x, boost.y))

    def check_collision(self, player, scoreboard):
        """Çarpışmaları kontrol et ve çarpışma varsa güçlendirici ID'sini döndür"""
        for boost in self.boosts:
            if boost.active and boost.rect.colliderect(player.rect):
                # Deactivate locally until server confirms
                boost.active = False
                return boost.id
        return None

    def update_active_boosts(self, active_boosts_dict):
        """Güçlendiricileri, sunucu tarafındaki aktif durumlarına göre güncelle"""
        for boost in self.boosts:
            if boost.id in active_boosts_dict:
                # Update the boost active status
                boost.active = active_boosts_dict[boost.id]

                # CRITICAL FIX: For portals, always keep them active
                if boost.type in ["portal1", "portal2"]:
                    boost.active = True

    def apply_boost_effect(self, player, boost_type, scoreboard):
        """Toplanan güçlendiricinin etkisini uygula"""
        now = pygame.time.get_ticks()

        if boost_type == "diamond":
            scoreboard.update_score(scoreboard.score + BOOST_TYPES["diamond"]["score"])
        elif boost_type == "money":
            scoreboard.update_score(scoreboard.score + BOOST_TYPES["money"]["score"])
        elif boost_type == "energy":
            player.speed_boost(BOOST_TYPES["energy"]["speed_boost"], BOOST_TYPES["energy"]["duration"])
        elif (boost_type == "portal1" or boost_type == "portal2") and now - self.last_teleport_time > TELEPORT_COOLDOWN:
            # Teleport işlemini yap
            self._link_portals()  # Bağlantıyı güncelle

            # Hedef portalı bul
            target_type = BOOST_TYPES[boost_type]["teleport_to"]

            # Hedef portalı bul
            target_portal = None
            for boost in self.boosts:
                if boost.type == target_type and boost.active:
                    target_portal = boost
                    break

            if target_portal:
                # Oyuncunun konumunu hedef portalın konumuna ayarla
                if 660<target_portal.rect.centerx<720:
                    player.x = target_portal.rect.centerx - (CELL_SIZE + CHARACTER_WIDTH/2)
                    player.y = target_portal.rect.centery - CHARACTER_HEIGHT/2
                    player.update_rect()
                else:
                    player.x = target_portal.rect.centerx + (CELL_SIZE - CHARACTER_WIDTH/2)
                    player.y = target_portal.rect.centery - CHARACTER_HEIGHT/2
                    player.update_rect()

                # Teleport cooldown'u başlat
                self.last_teleport_time = now

                # Teleport efekti veya ses eklenebilir
                print(f"Işınlandı: {boost_type} -> {target_type}")

