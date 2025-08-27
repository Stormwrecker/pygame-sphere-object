"""
The follow program creates a sphere-looking object using Pygame-CE. How it really works is that it takes an image,
slices it into 1 x 'your-height' and places them onto a circular track. Each segment then is sorted according to z depth for blitting.
Manipulating `Sphere.master_angle` will move the slices up and down the track and give the illusion of a 3D spherical object.

I've added a stretch effect just to add a more natural feel to the object's movement. To create an image for the
`Sphere`, simply figure out your height (say 16px), multiply that by π (say ~51px), and that will be sufficient for
'wrapping' around the whole object.

When blitting an object, make sure that you blit to `display` and NOT screen. The `display` is the actual canvas that
everything gets drawn on. Then the display is scaled to fit the window, perfect for pixel artists.

Using Pygame (not -CE) will result in your sphere object having a red background as I set color-key to red for the image.

Have fun experimenting with this technique, but please give credit if used!

Simply use this line in your docs: `Sphere code by Stormwrecker`
"""

# necessary modules
import pygame
import math

# extra modules
import random

# initialize pygame
pygame.init()

# window dimensions
screen_width = 800
screen_height = 480
# canvas dimensions (the bigger the size, the smaller your objects will appear)
display_width = 400
display_height = 240
# helpful measurements
half_display_x = display_width // 2
half_display_y = display_height // 2

# create the window and a canvas
screen = pygame.display.set_mode((screen_width, screen_height))
display = pygame.Surface((display_width, display_height))

# clock setup
clock = pygame.time.Clock()
FPS = 60


# sphere object
class Sphere(pygame.sprite.Sprite):
    def __init__(self, x, y, scale=3):
        # initialize sprite
        pygame.sprite.Sprite.__init__(self)
        # the bigger the scale, the more smooth the appearance will be
        # but the program might slow down some. Combine bigger scale
        # with larger canvas for maximum effect!
        self.master_scale = scale
        # get original image
        self.original_image = pygame.image.load("face.png").convert_alpha()
        self.original_image = pygame.transform.flip(self.original_image, True, False)
        # this color can be used for the drawing process
        self.color = self.original_image.get_at((0, 0))
        # various image setup
        self.width = self.original_image.get_width()
        self.height = self.original_image.get_height()
        self.original_image = pygame.transform.scale(self.original_image, (self.width * self.master_scale, self.height * self.master_scale))
        self.width = self.original_image.get_width()
        self.height = self.original_image.get_height()
        # actual image setup
        self.image = pygame.Surface((self.height + 2, self.height + 2)).convert_alpha()
        self.image.fill((255, 0, 0))
        self.image.set_colorkey((255, 0, 0))
        # rectangle
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.centerx = self.image.get_width() // 2
        self.centery = self.image.get_height() // 2

        # master image is the final output
        self.master_image = self.image

        # set up surface segments
        self.segments = [None for i in range(self.original_image.get_width())]
        self.num_items = len(self.segments)
        self.angle_increment = 360 / self.num_items if self.num_items > 0 else 0

        # positioning segments
        for i in range(self.original_image.get_width()):
            # actual image segment
            seg_img = self.original_image.subsurface((i, 0, 1, self.height)).convert_alpha()
            # increment segment position
            seg_angle = math.radians(self.angle_increment * i + 90)
            x = int(math.cos(seg_angle) * (4 * self.master_scale)) + self.centerx
            y = int(math.sin(seg_angle) * (4 * self.master_scale)) + self.image.get_height()
            # create segment rectangle
            seg_rect = seg_img.get_rect()
            seg_rect.topleft = (x, y)
            # segment z depth
            seg_depth = 0
            # each item in segments has this format: [image, rect, angle, z depth]
            self.segments[i] = [seg_img, seg_rect, seg_angle, seg_depth]

        # master angle for sphere heading
        self.master_angle = 90

        # rotation speed
        self.speed = 2

        # thickness of image outline
        self.thickness = 2

        # extra animation/physics variables (not required for sphere setup)
        self.max_stretch = 10
        self.grow_x = random.randint(0, self.max_stretch)
        self.grow_y = 0
        self.direction = 1
        self.dx = 0
        self.dy = 0
        self.vel_y = 0
        self.on_ground = False

    def update(self):
        # this is the only code you really need in here
        self.rotate()

        """All of the code below is NOT required for the sphere setup"""

        # reset variables
        self.dy = 0
        self.dx = 0
        self.on_ground = False

        # gravity
        self.vel_y += 1
        if self.vel_y >= 8:
            self.vel_y = 8
        self.dy += self.vel_y

        # keep object onscreen
        if self.rect.bottom + self.dy >= display_height:
            self.vel_y = 0
            self.dy = display_height - self.rect.bottom
            self.on_ground = True

        # move rectangle
        self.rect.x += self.dx
        self.rect.y += self.dy

        """End of extra code"""

    def rotate(self):
        # make the sphere look back and forth
        if self.master_angle >= 270:
            self.speed = -2
        if self.master_angle <= 90:
            self.speed = 2
        self.master_angle += self.speed

        # Keep master_angle normalized
        self.master_angle %= 360

        # update segments
        for seg in self.segments:
            # get current heading (in radians)
            current_angle = seg[2] + math.radians(self.master_angle)

            # position each segment based on heading (the 8 should NOT be changed, but you can mess with the 2)
            seg[1].midbottom = (round(math.cos(current_angle) * (8 * self.master_scale)) + self.centerx,
                                round(math.sin(current_angle) * (2 * self.master_scale)) + self.image.get_height())

            # calculate 'z depth'
            seg[3] = math.sin(current_angle) + 2

    def draw(self, display):
        # keep image from smearing
        self.image.fill((255, 0, 0))

        # This section here is what keeps the sphere from looking like a cylinder
        pygame.draw.circle(self.image, (25, 25, 25), (self.centerx, self.image.get_height() // 2), 8 * self.master_scale)
        new_mask = pygame.mask.from_surface(self.image)
        new_mask.invert()
        new_image = new_mask.to_surface(setcolor=(255, 0, 0)).convert_alpha()
        new_image.set_colorkey((0, 0, 0))

        # fill remaining image
        self.image.fill(self.color)

        # sort image segments based on z depth
        sorted_segs = sorted(self.segments, key=lambda x: x[3])

        # only the 'visible' segments get draw to the image
        for seg in [s for s in sorted_segs if s[3] >= 2.0]:
            self.image.blit(seg[0], seg[1])

        # draw the circular mask
        self.image.blit(new_image, (0, 0))

        """All of the code below is NOT required for the sphere setup"""

        # stretch back and forth
        if self.grow_x > self.max_stretch:
            self.direction = -2
            if self.on_ground:
                self.vel_y = random.randint(-10, -8)
        if self.grow_x < .5:
            self.direction = 1

        self.grow_x += .5 * self.direction
        self.grow_y = abs(self.max_stretch - self.grow_x)

        # scale original image
        orig_x, orig_y = (18, 18)
        size_x = orig_x + round(self.grow_x)
        size_y = orig_y + round(self.grow_y)
        self.master_image = pygame.transform.scale(self.image, (size_x * self.master_scale, size_y * self.master_scale))
        self.rect = self.master_image.get_rect(center=self.rect.center)

        """End of extra code"""

        # draw a nice black outline for effect
        mask_img = pygame.mask.from_surface(self.master_image).to_surface(setcolor=(1, 1, 1)).convert()
        mask_img.set_colorkey((0, 0, 0))
        for i in [(-self.thickness, -self.thickness), (0, -self.thickness), (self.thickness, -self.thickness), (-self.thickness, 0), (0, 0), (self.thickness, 0), (-self.thickness, self.thickness), (0, self.thickness), (self.thickness, self.thickness)]:
          display.blit(mask_img, (self.rect.x + i[0], self.rect.y + i[1]))

        # draw final image
        display.blit(self.master_image, self.rect)


# this list contains ALL the sphere objects you want to draw/update
sphere_objects = []

# create sphere object
sphere_obj = Sphere(half_display_x + random.randint(-100, 100), half_display_y + random.randint(-100, 100))
sphere_objects.append(sphere_obj)

# main loop
run = True
while run:
    # fill screen and display
    screen.fill((0, 0, 0))
    display.fill((50, 50, 50))

    # draw all sphere objects
    for obj in sphere_objects:
        obj.update()
        obj.draw(display)

    # draw and scale the display to fit the window
    screen.blit(pygame.transform.scale(display, screen.get_size()), (0, 0))
    pygame.display.flip()

    # main event loop
    all_events = pygame.event.get()
    for event in all_events:
        # quit
        if event.type == pygame.QUIT:
            run = False
        # reset sphere object
        if event.type == pygame.KEYDOWN:
            sphere_objects = []
            sphere_obj = Sphere(half_display_x + random.randint(-100, 100), half_display_y + random.randint(-100, 100))
            sphere_objects.append(sphere_obj)

    # tick clock
    clock.tick(FPS)

# quit
pygame.quit()
