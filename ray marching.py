import pygame
from pygame.locals import *
from pygame.math import *

import math, time

RESOLUTION = (960,720)
MAX_STEPS = 100
MAX_DIST = 100
SURF_DIST = 0.01


class Sphere(Vector3):

    def __init__(self, position, radius, color):

        Vector3.__init__(self, position)
        self.w = radius
        self.color = color

    def dist_from_point(self, p):

        return Vector3(p-self).length()-self.w


class HorizontalPlane:

    def __init__(self, y, color):

        self.y = y
        self.color = color

    def dist_from_point(self, p):

        return p.y - self.y


def GetDist(p, scene):

    scene_distances = [item.dist_from_point(p) for item in scene]
    return min(scene_distances)

def GetNearestObject(p, scene):

    nearest_object = scene[0]
    closest = scene[0].dist_from_point(p)
    for item in scene:
        dist = item.dist_from_point(p)
        if dist < closest:
            closest = dist
            nearest_object = item
    return nearest_object
        

def RayMarch(origin, direction, scene):

    dO = 0
    for n in range(MAX_STEPS):
        p = origin + direction * dO
        dS = GetDist(p, scene)
        dO += dS
        if (dO > MAX_DIST or dS < SURF_DIST):
            break

    return dO

def GetNormal(p, scene):
    d = GetDist(p, scene)
    e = Vector2(0.01,0)

    n = Vector3(d) - Vector3(
        GetDist(p-e.xyy, scene),
        GetDist(p-e.yxy, scene),
        GetDist(p-e.yyx, scene))
    return n.normalize()

def GetLight(p, scene):
    
    lightPos = (2, 4, 2)
    l = Vector3(lightPos - p).normalize()
    n = GetNormal(p, scene)

    # clamp between 0 and 1
    dif = max(0, min(l.dot(n), 1))
    d = RayMarch(p+n*SURF_DIST*2, l, scene)
    if d < Vector3(lightPos-p).length():
        dif *= 0.1
    return dif

def GetColor(p, scene):

    nearest = GetNearestObject(p, scene)
    return nearest.color

def main():

    pygame.init()

    sky = pygame.Color(0, 0, 0)
    scene = [Sphere((-1, 1, 4), 1, pygame.Color(255,0,0)),
             Sphere((2, 1, 5), 1, pygame.Color(0, 127, 127)),
             HorizontalPlane(0, pygame.Color(0, 127, 0))]
    
    resolution = Vector2(RESOLUTION)
    display = pygame.display.set_mode(RESOLUTION)
    clock = pygame.time.Clock()

    a = time.time()
    
    # begin ray marching
    for y in range(int(resolution.y)):
        for x in range(int(resolution.x)):
            uv = Vector2(x-0.5*resolution.x, 0.5*resolution.y-y)/resolution.y

            ray_origin = Vector3(0, 1, 0)
            ray_direction = Vector3(uv.x, uv.y, 1).normalize()

            # d is distance to scene
            d = RayMarch(ray_origin, ray_direction, scene)
            p = ray_origin + ray_direction * d

            dif = int((1-GetLight(p, scene))*255) if d < MAX_DIST else 0
            col = GetColor(p, scene) - pygame.Color(dif,dif,dif) if d < MAX_DIST else sky
            display.set_at((x, y), col)
        print("Rendering... {}% complete".format(y*100/resolution.y))
            
    print("Render time: {}s".format(int(time.time()-a)))
    
    game_exit = False
    while not game_exit:
        for event in pygame.event.get():
            if event.type == QUIT:
                game_exit = True        

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == '__main__':
    main()
