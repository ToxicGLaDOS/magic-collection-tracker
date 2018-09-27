import pygame



class PreciseRect(pygame.rect.Rect):
    def __init__(self, x, y, width, height):
        pygame.rect.Rect.__init__(self, x, y, width, height)
        self.precise_x = x
        self.precise_y = y
        self.precise_width = width
        self.precise_height = height

        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)

    def set_x(self, x):
        self.precise_x = x
        self.x = int(x)
    
    def set_y(self, y):
        self.precise_y = y
        self.y = int(y)
    
    def set_width(self, width):
        self.precise_width = width
        self.width = int(width)
    
    def set_height(self, height):
        self.precise_height = height
        self.height = int(height)
    