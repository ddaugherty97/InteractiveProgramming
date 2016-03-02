"""
The  Interactive Vertical-Scrolling Shooting Game of Chickens, made with pygame

Kevin Zhang and Daniel Daugherty
Software Design Spring 2016
"""


import pygame, sys
from pygame.locals import *
import random


class Cloud(object):

	def __init__(self, window, xpos, ypos):
		self.cloudObj = pygame.image.load('cloud.jpg')
		self.cloudObj.set_colorkey((255,255,255))
		self.cloudObj = pygame.transform.scale(self.cloudObj, (100,100))

		
		self.window = window
		self.xpos = xpos
		self.ypos = ypos
		self.yvel = 15
		self.window.blit(self.cloudObj, (self.xpos, self.ypos))


	def is_in_range(self):
		
		return self.ypos > -100	

	def update(self):
		self.window.fill(pygame.Color(135, 206, 250), pygame.Rect(self.xpos, self.ypos, 100,100))
		

		self.ypos -= self.yvel
		self.window.blit(self.cloudObj, (self.xpos, self.ypos))

		pygame.display.update()	


class Chicken(object):

	def __init__ (self, window):
		self.chickenObj = pygame.image.load('chicken.jpg')
		#self.chickenObj.set_colorkey((255,255,255))
		self.chickenObj = pygame.transform.scale(self.chickenObj, (100, 100))
		self.window = window
		self.xpos = 350
		self.ypos = 10
		self.xvel = 10
		self.yvel = 10
		self.window.blit(self.chickenObj, (self.xpos, self.ypos))




	def update(self):
		#self.window.fill(pygame.Color(135,206,250))
		self.window.fill(pygame.Color(135, 206, 250), pygame.Rect(self.xpos, self.ypos, 100,100))
		pressed = pygame.key.get_pressed()
		if pressed[pygame.K_DOWN]:
			self.ypos += self.yvel
		elif pressed[pygame.K_UP]:
			self.ypos -= self.yvel	
		elif pressed[pygame.K_RIGHT]:
			self.xpos += self.xvel
		elif pressed[pygame.K_LEFT]:
			self.xpos -= self.xvel	
		elif pressed[pygame.K_ESCAPE]:
			pygame.quit()
			sys.exit()	

		self.window.blit(self.chickenObj, (self.xpos, self.ypos))

		pygame.display.update()
		

if __name__ == '__main__':

	pygame.init()
	fpsClock = pygame.time.Clock()
	window = pygame.display.set_mode((800,600))
	pygame.display.set_caption('Testing 123')
	window.fill(pygame.Color(135,206,250))

	chicken1 = Chicken(window)
	cloud_list = []
	for i in range(10):
		cloud_list.append(Cloud(window, random.randint(0,800), random.randint(0,600)))

	while True:
		



		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			

		chicken1.update()	
		for i in range(len(cloud_list)):
			if not cloud_list[i].is_in_range():
				cloud_list[i] = Cloud(window, random.randint(0,800), 600)

			cloud_list[i].update()
		fpsClock.tick(30)			
