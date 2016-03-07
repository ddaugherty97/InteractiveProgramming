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


CURR_DIR = os.path.dirname(os.path.realpath(__file__))





class Cloud(pygame.sprite.Sprite):

	def __init__(self, xpos, ypos):
		pygame.sprite.Sprite.__init__(self)

		self.image = pygame.image.load('cloud2.png')   #loading cloud picture
		scale = random.random() + 1
		self.image = pygame.transform.scale(self.image, (int(scale*200),int(scale*100)))   #scales the clouds to a randomly set size
		self.image.fill((255, 255, 255, 200), None, pygame.BLEND_RGBA_MULT)
		if random.choice([True, False]):
			self.image = pygame.transform.flip(self.image, True, False)   #randomly flips the clouds for variety

		
		
		self.xpos = xpos
		self.ypos = ypos
		self.rect = pygame.Rect(self.xpos, self.ypos, self.image.get_width(), self.image.get_height())
		self.yvel = scale*15  #sets the speed of the cloud based on its size


	def is_in_range(self):
		"""
		checks if the cloud hit the top
		"""
		
		return self.rect.bottom > 0

	def update(self):
		"""
		Moves the rectangle based on x-vel and y-vel
		"""
		

		#self.ypos -= self.yvel
		self.rect = self.rect.move(0, -self.yvel)



class Sky():
	"""
	Represents all the clouds in the game
	"""

	def __init__(self, model):
		self.model = model
		self.clouds = pygame.sprite.Group()

		self.num_clouds = 0

		for i in range(10):
			self.clouds.add(Cloud(random.randint(0,SCREEN_W), random.randint(0,SCREEN_H)))  #creates a group of clouds in a Group
			self.num_clouds += 1

	def update(self):	
		"""
		makes the clouds scroll up
		"""
		for cloud in self.clouds:
			if not cloud.is_in_range():   #if the cloud is out of range, kill it and replace it with new a one
				cloud.kill()
				Cloud(random.randint(0,SCREEN_W), SCREEN_H).add(self.clouds)

		for cloud in self.clouds:  #update all clouds to move up
			cloud.update()





class Chicken(pygame.sprite.Sprite):
	"""
	The main character, the Chicken class
	"""

	def __init__ (self):
		pygame.sprite.Sprite.__init__(self)



		self.alive = True # the chicken's life

		self.sheet = pygame.image.load('chickenspritesheet.png')
		self.sprite_num = 3   #row of the chicken's subimage
		self.dt_image = 0.0   #the time for changing the picture of the image
		self.index = 0   #column of the chicken's subimage
		self.animation_speed = 0.10  #speed of the chicken's animation sequence

		self.width = 88  #width of the subimage
		self.height = 54  #height of the subimage

		self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num * self.height, self.width, self.height+23))
		self.image = self.sheet.subsurface(self.sheet.get_clip())      #setting and getting the subimage
		self.image = pygame.transform.scale(self.image, (125,100))
		self.index += 1

		
		self.xpos = SCREEN_W/2 -50
		self.ypos = 10
		self.xvel = 0
		self.yvel = 0
		self.rect = pygame.Rect(self.xpos, self.ypos, 100, 100)
		self.hitbox = pygame.Rect(self.xpos + 12.5, self.ypos + 12.5, 75, 75)  #hitbox of the chicken, defined as 3/4 of its size
	


	def move(self, xvel, yvel):
		"""
		Moves the chicken around based on its rectangle
		"""
		if self.alive:
			if not self.rect.right <= SCREEN_W:    #checks boundaries
				self.rect.right = SCREEN_W -1
			if not self.rect.left >= 0:
				self.rect.left = 1	
			if not self.rect.top >= 0:
				self.rect.top = 1
			if not self.rect.bottom <= SCREEN_H:	
				self.rect.bottom = SCREEN_H -1

		self.rect = self.rect.move(xvel, yvel)
		self.hitbox = self.hitbox.move(xvel, yvel)


	def update(self, hawks, dt):
		"""
		Moves the chicken
		"""


		self.correct_boxes()  #makes sure that the hitbox stays within the chicken's model


		self.move(self.xvel, self.yvel)  #moves and checks for collision before making image
		self.collide(hawks)

		self.dt_image += dt
		if self.dt_image > self.animation_speed:   #incrementally changes the subimage to make animation
			self.index += 1
			if self.index >= 3:
				self.index = 0
			self.dt_image = 0

			if self.xvel > 0:
				self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num * self.height, self.width, self.height+23))
				self.image = self.sheet.subsurface(self.sheet.get_clip())
			else:
				self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num * self.height, self.width, self.height+23))
				self.image = self.sheet.subsurface(self.sheet.get_clip())
				self.image = pygame.transform.flip(self.image, True, False)
		self.image = pygame.transform.scale(self.image, (125,100))


	def collide(self, hawks):
		"""
		Checks for collisions with hawks and chickens
		"""

		for hawk in hawks:
			if self.hitbox.colliderect(hawk.hitbox):  #checks for collision between hitboxes
				self.alive = False
				self.yvel = 5
				self.xvel = 0

	def correct_boxes(self):
		"""
		Corrects the hitboxes in case of mishaps
		"""
		self.hitbox.top = self.rect.top + 12.5   #makes sure the top of the hitbox is aligned properly
		self.hitbox.right = self.rect.right -12.5 #makes sure the right of the hitbox is aligned properly




class Hawk(pygame.sprite.Sprite):
	"""
	The Hawk Class, the predators
	"""

	def __init__(self, pos, xvel, top_hawk):
		pygame.sprite.Sprite.__init__(self)


		self.sheet = pygame.image.load('hawkspritesheet.png')
		self.sprite_num = 2  #row of the subimage
		self.dt_image = 0.0
		self.counter = 0.0  #counter for delay of start
		self.index = 0  #column of the subimage
		self.animation_speed = 0.10  #animation speed of the hawk

		self.width = 85  #width ofthe subimage
		self.height = 69.95   #height of the subimage

		self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num * self.height, self.width, self.height))
		self.image = self.sheet.subsurface(self.sheet.get_clip())  #set and get subimage

		self.image = pygame.transform.scale(self.image, (150,150))
		self.index += 1
		

		if top_hawk:   #if top hawk, then determines where the hawk will appear from
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
			# self.image = pygame.transform.flip(self.image, True, False)
			self.sprite_num = 1
			self.xvel = xvel	

		if self.ypos > SCREEN_H/2:	
			self.yvel = -1 * 7
		else:
			self.yvel = 7

		self.rect = pygame.Rect(self.xpos, self.ypos, 150, 150)	
		self.hitbox = pygame.Rect(self.xpos + 18.75, self.ypos + 18.75, 112.5, 112.5)

	def is_in_range(self):
		"""
		Checks if still within screen boundaries
		"""

		return self.rect.right <= SCREEN_W +150 and self.rect.left >= -150 and self.rect.bottom <= SCREEN_H+150 and self.rect.top >= -150	

	def update(self, chicken, dt):
		"""
		Updates hawks to chase the chicken
		"""

		self.dt_image += dt

		self.counter += dt
		if self.counter > 2:
			x_diff = chicken.rect.right - self.rect.right
			y_diff = chicken.rect.top - self.rect.top
			vector_mag = math.sqrt(x_diff**2 + y_diff**2) * 5
			self.xvel = self.xvel + x_diff / vector_mag 
			if self.xvel < 0:
				self.sprite_num = 2
			else:
				self.sprite_num = 1 
			self.yvel = self.yvel + y_diff / vector_mag

			self.rect = self.rect.move(self.xvel, self.yvel)
			self.hitbox = self.hitbox.move(self.xvel, self.yvel)


			if self.dt_image > self.animation_speed:
				self.index += 1
				if self.index >= 4:
					self.index = 0
				self.dt_image = 0
				self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num * self.height, self.width, self.height))
				self.image = self.sheet.subsurface(self.sheet.get_clip())
			self.image = pygame.transform.scale(self.image, (150,150))

		




class Flock():
	"""
	Represents all the Hawks in the game
	"""

	def __init__(self, model):

		self.model = model

		self.hawkfleet = pygame.sprite.Group()

		self.num_hawks = 0

		for i in range(1):
			Hawk(random.randint(-150,SCREEN_H), random.randint(1, 7), True).add(self.hawkfleet)
			Hawk(random.randint(-150,SCREEN_W), random.randint(1, 7), False).add(self.hawkfleet)
			self.num_hawks += 2

		

	def update(self, chicken, dt):		
		"""
		Updates hawks in the flock, checks if they're still in range
		"""


		for hawk in self.hawkfleet:
			if not hawk.is_in_range():
				hawk.kill()
				self.num_hawks -= 1

				if random.choice([True, False]):
					Hawk(random.randint(-150,SCREEN_W), random.randint(1,7), True).add(self.hawkfleet)
					self.num_hawks += 1
				else:
					Hawk(random.randint(-150,SCREEN_H), random.randint(1,7), False).add(self.hawkfleet)
					self.num_hawks += 1

		for hawk in self.hawkfleet:
			hawk.update(chicken, dt)	




		
class ChickenModel:
	"""
	Model for the game
	"""
	
	def __init__(self):
		self.width = SCREEN_W
		self.height = SCREEN_H

		self.chicken = Chicken()
		self.alive = self.chicken.alive
		self.chicken_sprite = pygame.sprite.Group(self.chicken)


		self.hawks = Flock(self)

		self.sky = Sky(self)

	def update(self, dt):
		"""
		Updates all the stuff
		"""

		self.sky.update()
		self.hawks.update(self.chicken, dt)
		self.chicken_sprite.update(self.hawks.hawkfleet, dt)


		self.alive = self.chicken.alive

	

	def get_drawables(self):
		"""
		Gives a list of things to draw in view
		"""
		return [self.sky.clouds, self.hawks.hawkfleet, self.chicken_sprite]





class ChickenView:
	"""
	View for Game
	"""
	def __init__(self, model):
		pygame.init()
		self.width = SCREEN_W
		self.height = SCREEN_H
		self.model = model
		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption('CHICKENS CHICKENS CHICKENS')


		pygame.font.init()
		self.font = pygame.font.Font(CURR_DIR + '/Chicken.ttf', 80)

		self.game_over = self.font.render('GAME OVER', False, RED)

	def draw(self, alive):
		"""
		Redraws game windows, fetching drawables from model
		"""
		self.screen.fill(pygame.Color(135,206,250))

		drawables = self.model.get_drawables()

		for g in drawables:
			g.draw(self.screen)	



		if not alive:
			self.screen.blit(self.game_over, (SCREEN_W/2 - 150,SCREEN_H/2 - 80))	


		pygame.display.flip()	





class ChickenController:
	"""
	Controller for Player
	"""

	def __init__(self, model):
		self.model = model
		self.done = False

	def process_events(self, alive):		
		"""
		Manages keypresses
		"""
		pygame.event.pump

		if alive:

			for event in pygame.event.get():
				if event.type == QUIT:
					self.done = True
				
				elif event.type == pygame.KEYDOWN:	
					k = event.key

					if k == pygame.K_DOWN and self.model.chicken.rect.bottom <= SCREEN_H:
						self.model.chicken.yvel = 10

					if k == pygame.K_UP and self.model.chicken.rect.top >= 0:
						self.model.chicken.yvel = -10

					if k == pygame.K_RIGHT and self.model.chicken.rect.right <= SCREEN_W:
						self.model.chicken.xvel = 10

					if k == pygame.K_LEFT and self.model.chicken.rect.left >= 0:
						self.model.chicken.xvel = -10

					if k == pygame.K_ESCAPE:
						self.done = True

				elif event.type == pygame.KEYUP:
					k = event.key

					if k == pygame.K_DOWN:
						self.model.chicken.yvel = -5		
					if k == pygame.K_UP:
						self.model.chicken.yvel = -5	
					if k == pygame.K_LEFT:
						self.model.chicken.xvel = -.01		
					if k == pygame.K_RIGHT:
						self.model.chicken.xvel = .01			

		return self.done								


	

class ChickenMain(object):
	"""
	Main Class
	"""


	def __init__(self, width = SCREEN_W, height = SCREEN_H):
		self.width = width
		self.height = height
		self.clock = pygame.time.Clock()
		self.model = ChickenModel()
		self.view = ChickenView(self.model)
		self.controller = ChickenController(self.model)

		
		
	def MainLoop(self):
		"""
		Game Loop
		"""

		lastGetTicks = pygame.time.get_ticks()


		done = False


		while not done:
			if self.model.alive:


				t = pygame.time.get_ticks()
				dt = (t - lastGetTicks) / 1000.0
				lastGetTicks = t

				done = self.controller.process_events(self.model.alive)
				self.model.update(dt)
				self.view.draw(self.model.alive)

				self.clock.tick(FRAMERATE)		

			else:
				while self.model.chicken.rect.top < SCREEN_H:
					t = pygame.time.get_ticks()
					dt = (t - lastGetTicks) / 1000.0
					lastGetTicks = t

					done = self.controller.process_events(self.model.alive)
					self.model.update(dt)
					self.view.draw(self.model.alive)

					self.clock.tick(FRAMERATE)
				done = True		


		pygame.quit()
		sys.exit()	

if __name__ == '__main__':
	MainWindow = ChickenMain()
	MainWindow.MainLoop()