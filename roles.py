import random
import os
import pygame

DEFAULT_ROLES = ['cop', 'cop', 'thief']


def shuffle_roles(roles=None):
    """Returns a shuffled copy of the given roles list."""
    if roles is None:
        roles = DEFAULT_ROLES.copy()
    else:
        roles = roles.copy()
    random.shuffle(roles)
    return roles


def role_to_color(role):
    """Returns the RGB color associated with a role."""
    if role == 'cop':
        return 255, 255, 0  # Yellow
    elif role == 'thief':
        return 255, 0, 0  # Red
    else:
        return 0, 255, 0  # Green (default)


def load_character_frames():
    """Tüm karakter framelerini yükler ve döndürür."""
    animations = {
        'cop': {
            'left': [],
            'right': [],
            'up': []
        },
        'thief': {
            'left': [],
            'right': [],
            'up': []
        }
    }

    base_path = "charactersgif"

    # Cop karakter animasyonlarını yükle
    for i in range(35):
        frame_number = str(i).zfill(2)
        left_frame = pygame.image.load(os.path.join(base_path, "cop left", f"frame_{frame_number}_delay-0.1s.gif"))
        right_frame = pygame.image.load(os.path.join(base_path, "cop right", f"frame_{frame_number}_delay-0.1s.gif"))
        animations['cop']['left'].append(left_frame)
        animations['cop']['right'].append(right_frame)

    for i in range(20):
        frame_number = str(i).zfill(2)
        up_frame = pygame.image.load(os.path.join(base_path, "cop top sub", f"frame_{frame_number}_delay-0.1s.gif"))
        animations['cop']['up'].append(up_frame)

    # Thief karakter animasyonlarını yükle
    for i in range(26):
        frame_number = str(i).zfill(2)
        left_frame = pygame.image.load(os.path.join(base_path, "thief left", f"frame_{frame_number}_delay-0.1s.gif"))
        right_frame = pygame.image.load(os.path.join(base_path, "thief right", f"frame_{frame_number}_delay-0.1s.gif"))
        animations['thief']['left'].append(left_frame)
        animations['thief']['right'].append(right_frame)

    for i in range(22):
        frame_number = str(i).zfill(2)
        up_frame = pygame.image.load(os.path.join(base_path, "thief top sub", f"frame_{frame_number}_delay-0.1s.gif"))
        animations['thief']['up'].append(up_frame)

    return animations