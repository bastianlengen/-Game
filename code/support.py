import pygame

from settings import *
from os.path import join
from os import walk


def import_image(*path, alpha=True, format='png'):
    full_path = join(*path) + f'.{format}'
    surf = pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()
    return surf


def import_folder(*path):
    frames = []
    for folder_path, sub_folders, image_names in walk(join(*path)):
        for image_name in sorted(image_names, key=lambda name: int(name.split('.')[0])):
            full_path = join(folder_path, image_name)
            surf = pygame.image.load(full_path).convert_alpha()
            frames.append(surf)
    return frames


def import_folder_dict(*path):
	frame_dict = {}
	for folder_path, _, image_names in walk(join(*path)):
		for image_name in image_names:
			full_path = join(folder_path, image_name)
			surface = pygame.image.load(full_path).convert_alpha()
			frame_dict[image_name.split('.')[0]] = surface
	return frame_dict


def import_sub_folders(*path):
    frames = {}
    for _, sub_folders, _ in walk(join(*path)):
        if sub_folders:
            for sub_folder in sub_folders:
                frames[sub_folder] = import_folder(*path, sub_folder)
    return frames


def import_tilemap(cols, rows, *path):
    frames = {}
    surf = import_image(*path)
    cell_width, cell_height = surf.get_width() / cols, surf.get_height() / rows
    for col in range(cols):
        for row in range(rows):
            cutout_rect = pygame.Rect(col * cell_width, row * cell_height, cell_width, cell_height)  # l,t,w,h
            cutout_surf = pygame.Surface((cell_width, cell_height))
            cutout_surf.fill('green')  # Fill the background
            cutout_surf.set_colorkey('green')  # Ignore all grind pixels
            cutout_surf.blit(surf, (0, 0), cutout_rect)
            frames[(col, row)] = cutout_surf
    return frames

