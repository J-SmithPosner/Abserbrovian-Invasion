import pygame, sys
import random
import math
from time import time
from pygame import mixer

width, height =550, 550
pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.set_num_channels(64)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('The game thingy')

GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 122.5, 0)
BLACKISH = (0, 5, 20)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)



fps = 60
health = 5
score = 0
high_score = 0
cannons = []
spaceHold = False
bullets = []
asteroids = []
bulletSpeed = 3
threshold = 500


class Circle():
  
  def __init__(self, color, x, y, r, w):
      self.x = x
      self.y = y
      self.r = r
      self.w = w
      self.color = color

  def draw(self):
    pygame.draw.circle(screen, (self.color), [self.x, self.y], self.r,
                         self.w)

class Button():
    def __init__(self, text, width, height, pos):
        self.pressed = False

        self.Rect = pygame.Rect(pos, (width,height))

        self.text = text
        self.text_rect = self.text.get_rect(center = self.Rect.center)
    
    def draw(self):
        pygame.draw.rect(screen, WHITE, self.Rect, border_radius= 12)
        screen.blit(self.text, self.text_rect)

    def checkClick(self):
        mouse_pos = pygame.mouse.get_pos()
        if(self.Rect.collidepoint(mouse_pos)):
            if pygame.mouse.get_pressed()[0]: #returns tuple of (left, midle, right) but midle doesn't exist on this computer
                self.pressed = True
            else:
                self.pressed = False
        else:
          self.pressed = False
        return self.pressed
            


playTxt = pygame.font.SysFont('roboto', 50).render('Play', 1, BLACKISH)
howToTxt = pygame.font.SysFont('roboto', 50).render('How To Play', 1, BLACKISH)
menuTxt = pygame.font.SysFont('roboto', 25).render('Menu', 1, BLACKISH)

play = Button(playTxt, width/4, height/10, (width/2 - width/8, height/2-height/20))
howTo = Button(howToTxt, width/3+20, height/9,  (width/2 - (width/3+20)/2, height/2-height/18+height/10+10))
Menu = Button(menuTxt, width/10, height/20, (width-width/8, height/30))


              
mouseX, mouseY = pygame.mouse.get_pos()
planet = Circle((RED), width / 2, height / 2, width / 8, 0)
ufo = Circle((GREEN), mouseX, mouseY, width/35, 0)

def blitRotate(surf, image, pos, originPos, angle):

    # offset from pivot to center
    image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    
    # roatated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # roatetd image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

    # rotate and blit the image
    surf.blit(rotated_image, rotated_image_rect)


def collideCircles(circle1, circle2):
  if math.sqrt((circle1.x - circle2.x)**2 +
                 (circle1.y - circle2.y)**2) < circle1.r + circle2.r:
    return True
  else:
    return False

def manage_cannons(cannons, bullets, asteroids):
  global health
  global score
  if len(cannons) < 2.5 + (time()-start)/45:
    theta = random.randint(0,359)
    y = math.sin(theta) * planet.r + planet.y 
    x = math.cos(theta) * planet.r + planet.x
    noNear = True
    for cannon in cannons:
      if abs(cannon[0].x - x) < cannon[0].r*2 and abs(cannon[0].y - y) < cannon[0].r*2:
        noNear = False
    if noNear:
      cannons.append([Circle(YELLOW, x, y, width/40, 6), Circle(ORANGE, x, y, width/100, 0), bulletSpeed + random.randint(0,4)/2 + (time()-start)/60])
  
  for cannon in cannons:
    dilationFactor = (cannon[2]/2) / math.sqrt((cannon[1].x - planet.x)**2 + (cannon[1].y - planet.y)**2)
    
    cannon[1].x -= dilationFactor * (planet.x - cannon[1].x)
    cannon[1].y -= dilationFactor * (planet.y - cannon[1].y)

    bulletDelay = 20
    if (0-bulletDelay > cannon[1].x or cannon[1].x > width+bulletDelay) or (0-bulletDelay> cannon[1].y  or cannon[1].y > height+bulletDelay):
      cannon[1].x = cannon[0].x
      cannon[1].y = cannon[0].y

    cannon[0].draw()
    dx = planet.x - cannon[0].x
    dy = planet.y - cannon[0].y
    rads = math.atan2(-dy,dx)
    rads %= 2*math.pi
    degs = math.degrees(rads) 

    imgW, imgH = cannonImg.get_size()

    blitRotate(screen, cannonImg, (cannon[0].x, cannon[0].y), (imgW/2, imgH/2),degs)

    cannon[1].draw()

    if collideCircles(cannon[1], ufo):
      cannon[1].x, cannon[1].y = (cannon[0].x, cannon[0].y)
      cannon[2] = cannon[2]*3/4
      health -=1
    if collideCircles(cannon[0], ufo):
      cannons.remove(cannon)
      health-=1
      score += 20
    for bullet in bullets:
      if collideCircles(cannon[1], bullet):
        cannon[1].x = cannon[0].x
        cannon[1].y = cannon[0].y

        bullets.remove(bullet)
        cannon[2] = max(cannon[2]*5/6, bulletSpeed/3*2)
      if collideCircles(cannon[0], bullet):
        cannons.remove(cannon)
        score += 20

def manage_bullets(bullets):
  global spaceHold
  global score
  if keys_pressed[pygame.K_SPACE] and len(bullets) <= 0+(score/750) and not spaceHold:
    bullets.append(Circle(ORANGE, ufo.x, ufo.y, 5, 0))

  if spaceHold and not keys_pressed[pygame.K_SPACE]:
    spaceHold = False
  elif not spaceHold and keys_pressed[pygame.K_SPACE]:
    spaceHold = True
  
  for bullet in bullets:
    dilationFactor = bulletSpeed / math.sqrt((bullet.x - planet.x)**2 + (bullet.y - planet.y)**2)

    bullet.x += dilationFactor * (planet.x - bullet.x)
    bullet.y += dilationFactor * (planet.y - bullet.y)

    if collideCircles(bullet, planet):
      bullets.remove(bullet)
      score += 1

    bullet.draw()

def manage_asteroids(asteroids, bullets):
  global health
  global score
  asteroidSpeed = min(2 +(time()-start)/60,4.5)/1.2
  if len(asteroids) < min(6 + (time()-start)/45, 9):
    xy = random.randint(0, 1)
    if xy == 1:
      x = random.randint(0, width)
      y = random.randint(0,1)*height
    elif xy == 0:
      y = random.randint(0, height)
      x = random.randint(0,1)*width
          
    if score >= 500:
      if random.randint(0,100)  < (score-500)/18:
        if random.randint(0,1) == 1:
          follow = True
        else:
          follow = False
      else:
        follow = False
    else:
      follow = False

    asteroids.append([Circle(WHITE, x, y, width/40, 0), follow])
  for asteroid in asteroids:
    if asteroid[1]:
      dilationFactor = (asteroidSpeed-1) / math.sqrt((asteroid[0].x - ufo.x)**2 + (asteroid[0].y - ufo.y)**2)

      asteroid[0].x += dilationFactor * (ufo.x - asteroid[0].x)
      asteroid[0].y += dilationFactor * (ufo.y - asteroid[0].y)

    else:
      dilationFactor = asteroidSpeed / math.sqrt((asteroid[0].x - planet.x)**2 + (asteroid[0].y - planet.y)**2)

      asteroid[0].x += dilationFactor * (planet.x - asteroid[0].x)
      asteroid[0].y += dilationFactor * (planet.y - asteroid[0].y)

    if collideCircles(asteroid[0], planet):
      asteroids.remove(asteroid)
      score += 4
    if collideCircles(asteroid[0], ufo):
      asteroids.remove(asteroid)
      health -= 1
    
    for bullet in bullets:
      if collideCircles(bullet, asteroid[0]):
        bullets.remove(bullet)


    screen.blit(asteroidImg, (asteroid[0].x-asteroid[0].r, asteroid[0].y-asteroid[0].r))


background = pygame.image.load('Assets/Stary_Space.jpg')
background = pygame.transform.scale(background, (width, height))
ufoImg = pygame.image.load('Assets/UFO.png')
ufoImg = pygame.transform.scale(ufoImg, (ufo.r*2, ufo.r*2))
cannonImg = pygame.image.load('Assets/Cannon.png')
cannonImg = pygame.transform.scale(cannonImg, (width/40*5, width/20))
asteroidImg = pygame.image.load('Assets/Asteroid.png')
asteroidImg = pygame.transform.scale(asteroidImg, (width/20, width/20))
marsImg = pygame.image.load('Assets/Mars.png')
marsImg = pygame.transform.scale(marsImg, (planet.r*2+1, planet.r*2+10))
earthImg = pygame.image.load('Assets/Earth.png')
earthImg = pygame.transform.scale(earthImg, (planet.r*2, planet.r*2))
plunisImg = pygame.image.load('Assets/Plunis.png')
plunisImg = pygame.transform.scale(plunisImg, (planet.r*2, planet.r*2))

planetImg = random.choice([marsImg, plunisImg, earthImg])

clock = pygame.time.Clock()
start = time()
mode = 'menu'
while True:
  clock.tick(fps)
  screen.blit(background, (0,0))

  for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()


  if mode == 'play':

    mouseX, mouseY = pygame.mouse.get_pos()

    while not collideCircles(Circle(GREEN, mouseX, mouseY, 1, 0), ufo):
      screen.blit(background, (0,0))
      ufo.x = width/2
      ufo.y = height/4
      screen.blit(planetImg, (planet.x-planetImg.get_width()/2, planet.y-planetImg.get_height()/2))
      screen.blit(ufoImg, (ufo.x-ufoImg.get_width()/2, ufo.y-ufoImg.get_height()/2))
      health = 5
      txt0 = pygame.font.SysFont('roboto',30).render('Please hover your', 1, WHITE)
      txt1 = pygame.font.SysFont('roboto', 30).render('mouse over the ufo', 1, WHITE) 
      txt2 = pygame.font.SysFont('roboto', 30).render('to start', 1, WHITE)
      screen.blit(txt0, (width*3/5, height/4))
      screen.blit(txt1, (width*3/5, height/4+15))
      screen.blit(txt2, (width*3/5, height/4+30))
      mouseX, mouseY = pygame.mouse.get_pos()
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()
      pygame.display.update()
    start = time()
    mode = 'start'

  if mode == 'start':

    keys_pressed = pygame.key.get_pressed()


    ufo.x, ufo.y = pygame.mouse.get_pos()
    screen.blit(planetImg, (planet.x-planetImg.get_width()/2, planet.y-planetImg.get_height()/2))
    screen.blit(ufoImg, (ufo.x-ufoImg.get_width()/2, ufo.y-ufoImg.get_height()/2))

    manage_bullets(bullets)
    manage_asteroids(asteroids, bullets)
    manage_cannons(cannons, bullets, asteroids)
    

    
    font_txt = pygame.font.SysFont('roboto', 90).render(str(score), 1, WHITE)
    text_width, text_height = pygame.font.SysFont('roboto', 90).size(str(score))
    screen.blit(font_txt, (width/2-text_width/2, height/2-text_height/2))
    
    Menu.draw()
    if Menu.checkClick():
      mode = 'menu'

    for i in range(5):
      pygame.draw.rect(screen, (63.75*i,255-63.75*i, 0), pygame.Rect(5, height/2-30 + 12*i, 15, 12)) 
    pygame.draw.rect(screen, (WHITE), pygame.Rect(3, height/2-30 + 12*(5-(health))+2, 19, 8))

    if collideCircles(planet, ufo):
      health = 0
    if health == 0:
      if score > high_score:
        high_score = score
      health = 5
      score = 0
      threshold = 500
      asteroids = []
      bullets = []
      cannons = []
      ufo.x = width/2
      ufo.y = height/4
      planetImg = random.choice([marsImg, plunisImg, earthImg])

      
      mode = 'menu'

    if score > threshold:
      mode = 'travel'

    Menu.draw()
  if mode == 'menu':
    howTo.draw()
    play.draw()
    txt = pygame.font.SysFont('robot', 60).render(f"High Score = {high_score}",1,WHITE)
    screen.blit(txt, (width/2-txt.get_width()/2,height/2 - play.Rect.height -10))
    
    if play.checkClick():
      mode = 'play'
      score = 0
    if howTo.checkClick():
      mode = 'howto'
    
  
  elif mode == 'howto':
    if Menu.checkClick():
        mode = 'menu'
    txt = pygame.font.SysFont('robot', 60).render("Instructions", 1, WHITE)
    screen.blit(txt, (width/2-txt.get_width()/2, 30))

    Instructions = """The goal of this game is to 
destroy planets. Meteors will 
fall from the sky damaging the planet. 
Avoid the meteors to stay alive. 
Aliens will be defending the planet. 
Avoid the aliens bullets and shoot
the aliens to score more points. 

Use the mouse to move. 
Press the space bar to shoot. """
    Instructions = Instructions.split('\n')
    for i, line in enumerate(Instructions):
        txt = pygame.font.SysFont('robot', 40).render(line, 1, WHITE)
        screen.blit(txt, (15, (100 + 25 * i)))
      
    txt = pygame.font.SysFont('robot', 25).render("Meteor", 1, WHITE)
    screen.blit(txt, (width / 4 * 0 + 15, (height / 4 * 3)))
    screen.blit(pygame.transform.scale(asteroidImg, (60,60)), (width / 4 * 0 + 15, (height / 4 * 3 + 30)))

    txt = pygame.font.SysFont('robot', 25).render("Planet Defender", 1,WHITE)
    screen.blit(txt, (width / 4 * 1, (height / 4 * 3)))
    screen.blit(pygame.transform.scale(cannonImg, (100,40)), (width / 4 * 1 + 15, (height / 4 * 3 + 30)))


    txt = pygame.font.SysFont('robot', 25).render("You/UFO", 1, WHITE)
    screen.blit(txt, (width / 4 * 2 + 15, (height / 4 * 3)))
    screen.blit(pygame.transform.scale(ufoImg, (60,60)), (width / 4 * 2 + 15, (height / 4 * 3 + 30)))


    txt = pygame.font.SysFont('robot', 25).render("Planets", 1, WHITE)
    screen.blit(txt, (width / 4 * 3 + 15, (height / 4 * 3)))
    screen.blit(pygame.transform.scale(marsImg, (50,50)), (width / 4 * 3-5, (height / 4 * 3 + 30)))
    screen.blit(pygame.transform.scale(earthImg, (50,50)), (width / 4 * 3 + 55, (height / 4 * 3 + 30)))
    screen.blit(pygame.transform.scale(plunisImg, (50,50)), (width / 4 * 3 + 25, (height / 4 * 3 + 80)))



    Menu.draw()

  
  elif mode == 'travel':
    num = 0
    oldImg = planetImg
    planetImg = random.choice([marsImg, plunisImg, earthImg])
    while num < width:
      clock.tick(fps)
      screen.blit(background, (0-num, 0))
      screen.blit(background, (width-num, 0))
      screen.blit(planetImg, (planet.x-planetImg.get_width()/2 + width-num, planet.y-planetImg.get_height()/2))
      screen.blit(oldImg, (planet.x-oldImg.get_width()/2 -num, planet.y-oldImg.get_height()/2))
      screen.blit(ufoImg, (ufo.x-ufoImg.get_width()/2, ufo.y-ufoImg.get_height()/2))
      
      num += 3

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()


      pygame.display.update()
    threshold += 500
    mode = 'start'
       
  pygame.display.update()
