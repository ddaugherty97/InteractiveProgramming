"""
The  Interactive Vertical-Scrolling Shooting Game of Chickens, made with pygame

Kevin Zhang and Daniel Daugherty
Software Design Spring 2016
"""


import pygame, sys, os
from pygame.locals import *
import random, math

FRAMERATE = 60

# Colors
BLACK    = (  0,   0,   0)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
SCREEN_W = 1600
SCREEN_H = 900







class Cloud(object):

	def __init__(self, window, xpos, ypos):
		self.cloudObj = pygame.image.load('cloud.png')
		#self.cloudObj.set_colorkey((255,255,255))
		self.cloudObj = pygame.transform.scale(self.cloudObj, (100,100))
		self.cloudObj.convert()

		
		self.window = window
		self.xpos = xpos
		self.ypos = ypos
		self.yvel = 20
		self.window.blit(self.cloudObj, (self.xpos, self.ypos))


	def is_in_range(self):
		
		return self.ypos > -100	

	def update(self):
		#self.window.fill(pygame.Color(135, 206, 250), pygame.Rect(self.xpos, self.ypos, 100,100))
		

		self.ypos -= self.yvel
		self.window.blit(self.cloudObj, (self.xpos, self.ypos))



class Chicken(object):

	def __init__ (self, window):
		self.chickenObj = pygame.image.load('chicken.png')
		self.chickenObj.set_colorkey((255,255,255))
		self.chickenObj = pygame.transform.scale(self.chickenObj, (100, 100))
		self.chickenObj.convert()
		self.chickenFlip = pygame.transform.flip(self.chickenObj, True, False)
		self.chicken = self.chickenObj
		self.window = window
		self.xpos = SCREEN_W/2 -50
		self.ypos = 10
		self.xvel = 10
		self.yvel = 10
		self.window.blit(self.chicken, (self.xpos, self.ypos))




	def update(self):

		#self.window.fill(pygame.Color(135, 206, 250), pygame.Rect(self.xpos, self.ypos, 100,100))
		pressed = pygame.key.get_pressed()
		if pressed[pygame.K_DOWN] and self.ypos <= SCREEN_H - 100:
			self.ypos += self.yvel
		if pressed[pygame.K_UP] and self.ypos >= 0:
			self.ypos -= self.yvel	
		if pressed[pygame.K_RIGHT] and self.xpos <= SCREEN_W - 100:
			self.chicken = self.chickenFlip
			self.xpos += self.xvel
		if pressed[pygame.K_LEFT] and self.xpos >= 0:
			self.chicken = self.chickenObj
			self.xpos -= self.xvel	
		if pressed[pygame.K_ESCAPE]:
			pygame.quit()
			sys.exit()	

		self.window.blit(self.chicken, (self.xpos, self.ypos))



class Hawk(object):

	def __init__(self, window, pos, xvel, top_hawk):
		self.hawk = pygame.image.load('hawk.png')
		self.hawk.set_colorkey((255,255,255))
		self.hawk = pygame.transform.scale(self.hawk, (150,150))
		self.hawk.convert()
		self.window = window
		if top_hawk:
			self.ypos = pos
			if pos == -150 or pos == SCREEN_H:
				self.xpos = random.randint(-150, SCREEN_W)
			else:
				self.xpos = random.choice([-150, SCREEN_W])	
		else:		
			self.xpos = pos
			if pos == -150 or pos == SCREEN_W:
				self.ypos = random.randint(-150,SCREEN_H)
			else:
				self.ypos = random.choice([-150,SCREEN_H])


		if  self.xpos > SCREEN_W/2:
			self.xvel = -1 * xvel
		else:
			self.hawk = pygame.transform.flip(self.hawk, True, False)
			self.xvel = xvel	

		if self.ypos > SCREEN_H/2:	
			self.yvel = -1 * 2
		else:
			self.yvel = 2

		self.window.blit(self.hawk, (self.xpos, self.ypos))

	def is_in_range(self):
		return self.xpos <= SCREEN_W +150 and self.xpos >= -150 and self.ypos <= SCREEN_H+150 and self.ypos >= -150	

	def update(self, chicken):
		x_diff = chicken.xpos - self.xpos
		y_diff = chicken.ypos - self.ypos
		vector_mag = math.sqrt(x_diff**2 + y_diff **2)
		self.xvel = self.xvel + x_diff/vector_mag
		self.yvel = self.yvel + y_diff/vector_mag

		self.xpos += self.xvel
		self.ypos += self.yvel
		self.window.blit(self.hawk, (self.xpos, self.ypos))


		
class ChickenModel(object):
	pass


class ChickenView(object):
	pass


class ChickenController(object):
	pass

class ChickenMain(object):

	 def __init__(self, width = SCREEN_W, height = SCREEN_H):
	 	self.width = width
	 	self.height = height
		self.clock = pygame.time.Clock()
		self.window = pygame.display.set_mode((self.width,self.height))
		pygame.display.set_caption('Testing 123')
		self.window.fill(pygame.Color(135,206,250))


	 def MainLoop(self):
	 	pygame.init()
		chicken1 = Chicken(self.window)
		hawkfleet = []
		for i in range(1):
			hawkfleet.append(Hawk(self.window, random.randint(-150,SCREEN_H), random.randint(1, 7), True))
			hawkfleet.append(Hawk(self.window, random.randint(-150,SCREEN_W), random.randint(1, 7), False))

		cloud_list = []
		for i in range(10):
			cloud_list.append(Cloud(self.window, random.randint(0,SCREEN_H), random.randint(0,SCREEN_W)))

		lastGetTicks = pygame.time.get_ticks()

		done = False
	

		while not done:

			self.window.fill(pygame.Color(135,206,250))


			t = pygame.time.get_ticks()
			dt = (t - lastGetTicks) / 1000.0
			lastGetTicks = t


			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()

			
			for i in range(len(cloud_list)):
				if not cloud_list[i].is_in_range():
					cloud_list[i] = Cloud(self.window, random.randint(0,SCREEN_W), SCREEN_H)

				cloud_list[i].update()

			for i in range(len(hawkfleet)):
				if not hawkfleet[i].is_in_range():
					 if random.choice([True, False]):
					 	hawkfleet[i] = Hawk(self.window, random.randint(-150,SCREEN_W), random.randint(1,2), True)
					 else:
					 	hawkfleet[i] = Hawk(self.window, random.randint(-150,SCREEN_H), random.randint(1,2), False)

				hawkfleet[i].update(chicken1)	
				
		

			
		
			chicken1.update()	

			pygame.display.update()


			self.clock.tick(FRAMERATE)		

if __name__ == '__main__':
	MainWindow = ChickenMain()
	MainWindow.MainLoop()


			
