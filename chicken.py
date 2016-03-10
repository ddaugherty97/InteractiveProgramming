"""
The  Interactive Vertical-Scrolling Shooting Game of Chickens, made with pygame

Kevin Zhang and Daniel Daugherty
Software Design Spring 2016
"""


import pygame, sys, os
from pygame.locals import *
import random, math
import pickle

FRAMERATE = 60

# Colors
BLACK    = (  0,   0,   0)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
SCREEN_W = 1600
SCREEN_H = 900


CURR_DIR = os.path.dirname(os.path.realpath(__file__))


class Cloud(pygame.sprite.Sprite):

	def __init__(self, xpos, ypos, xvel, yvel):
		pygame.sprite.Sprite.__init__(self)

		self.image = pygame.image.load('cloud2.png')   #loading cloud picture
		self.scale = random.random() + 1
		self.image = pygame.transform.scale(self.image, (int(self.scale*200),int(self.scale*100)))   #scales the clouds to a randomly set size
		self.image.fill((255, 255, 255, 200), None, pygame.BLEND_RGBA_MULT)
		if random.choice([True, False]):
			self.image = pygame.transform.flip(self.image, True, False)   #randomly flips the clouds for variety

		
		
		self.xpos = xpos
		self.ypos = ypos
		self.rect = pygame.Rect(self.xpos, self.ypos, self.image.get_width(), self.image.get_height())
		self.yvel = yvel
		self.xvel = xvel


	def is_in_range(self):
		"""
		checks if the cloud hit the top
		"""

		return self.rect.bottom > 0 and self.rect.right > 0


	def update(self):
		"""
		Moves the rectangle based on x-vel and y-vel
		"""

		self.rect = self.rect.move(self.scale * self.xvel, self.scale * self.yvel)


class Sky():
	"""
	Represents all the clouds in the game
	"""

	def __init__(self, model, left, xvel, yvel):
		self.model = model
		self.clouds = pygame.sprite.Group()
		self.left = left
		self.xvel = xvel
		self.yvel = yvel

		self.num_clouds = 0

		for i in range(10):
			self.clouds.add(Cloud(random.randint(0,SCREEN_W), random.randint(0,SCREEN_H), xvel, yvel))  #creates a group of clouds in a Group
			self.num_clouds += 1
	

	def update(self):	
		"""
		makes the clouds scroll up
		"""

		if not self.left:
			for cloud in self.clouds:
				if not cloud.is_in_range():   #if the cloud is out of range, kill it and replace it with new a one
					cloud.kill()
					Cloud(random.randint(0,SCREEN_W), SCREEN_H, self.xvel, self.yvel).add(self.clouds)
		else:
			for cloud in self.clouds:
				if not cloud.is_in_range():   #if the cloud is out of range, kill it and replace it with new a one
					cloud.kill()
					Cloud(SCREEN_W, random.randint(0, SCREEN_H), self.xvel, self.yvel).add(self.clouds)

		for cloud in self.clouds: 
		# update all clouds to move up
			cloud.xvel = self.xvel
			cloud.yvel = self.yvel
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
		self.accelerate = False

		self.width = 88  #width of the subimage
		self.height = 54  #height of the subimage

		self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num * self.height, self.width, self.height+23))
		self.image = self.sheet.subsurface(self.sheet.get_clip())      #setting and getting the subimage
		self.image = pygame.transform.scale(self.image, (125,100))
		self.index += 1

		
		self.xpos = SCREEN_W/2 -50
		self.ypos = 100
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


	def update(self, hawks, dt, alive):
		"""
		Moves the chicken
		"""


		self.correct_boxes()  #makes sure that the hitbox stays within the chicken's model
		self.move(self.xvel, self.yvel)  #moves and checks for collision before making image
		self.collide(hawks)


		if alive:

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
		else:
			self.sheet.set_clip(pygame.Rect(2 * self.width+3, 3 * self.height+82, self.width, self.height+23))
			self.image = self.sheet.subsurface(self.sheet.get_clip())

		self.image = pygame.transform.scale(self.image, (125,100))


	def collide(self, hawks):
		"""
		Checks for collisions with hawks and chickens
		"""

		for hawk in hawks:
			if self.hitbox.colliderect(hawk.hitbox):  #checks for collision between hitboxes
				self.alive = False
				self.yvel = 10   
				self.xvel = 0

	def correct_boxes(self):
		"""
		Corrects the hitboxes in case of mishaps
		"""
		self.hitbox.top = self.rect.top + 12.5   #makes sure the top of the hitbox is aligned properly
		self.hitbox.right = self.rect.right -12.5 #makes sure the right of the hitbox is aligned properly


class EggShot(pygame.sprite.Sprite):
	"""
	The projectile Egg that the Chicken can shoot
	"""

	def __init__(self, side, top, xvel, model):
		pygame.sprite.Sprite.__init__(self)


		#making the image and animation
		self.model = model

		self.sheet = pygame.image.load('rolling_eggs.png')
		self.sprite_num = 0  #row of the subimage
		self.dt_image = 0.0
		self.index = 0   #column of the subimage
		self.animation_speed = .10  #animation speed of the egg rolling

		self.width = 20  #width of the subimage
		self.height = 20  #height of the subimage

		self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num * self.height, self.width, self.height))
		self.image = self.sheet.subsurface(self.sheet.get_clip())

		self.image = pygame.transform.scale(self.image, (50, 50))
		self.index += 1

		#determining where the image is in the screen

		self.yvel = 20
		self.xvel = xvel  #x velocity is the same as the chicken's upon proc

		self.rect = pygame.Rect(side , top, 50, 50)

		if self.xvel > 0:
			self.hitbox = pygame.Rect(side + 5, top + 5, 40, 40)
		else:
			self.hitbox = pygame.Rect(side - 5, top + 5, 40, 40)	

	def is_in_range(self):
		"""
		Checks if egg is still in the screen, assuming that it never hit a hawk
		"""

		return self.rect.top <= SCREEN_H


	def move(self, xvel, yvel):
		"""
		Moves the egg, making it drop
		"""

		self.rect = self.rect.move(xvel, yvel)
		self.hitbox = self.hitbox.move(xvel, yvel)	

	def update(self, hawks, dt):
	
		"""
		Updates the egg, making it fall, checking for range and collisions.
		"""
		self.dt_image +=dt

		self.move(self.xvel, self.yvel)
		self.collide(hawks)

		if self.dt_image > self.animation_speed:   #animation to make the egg roll while dropping
			self.index += 1
			if self.index >= 8:
				self.index = 0
			self.dt_image = 0
			
			self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num * self.height, self.width, self.height))
			self.image = self.sheet.subsurface(self.sheet.get_clip())

		self.image = pygame.transform.scale(self.image, (50,50))	


	def collide(self, hawks):
		"""
		Checks for collisions with hawks
		"""

		for hawk in hawks:
			if self.hitbox.colliderect(hawk.hitbox):
				if isinstance(hawk, Boss_Hawk):
					self.model.score += 5000
				else:
					self.model.score += 1000
				self.kill()
				hawk.alive = False
				hawk.yvel = 15
				hawk.xvel = 0


class Eggs():
	"""
	The group that represents the current collection of eggs that are procced
	"""

	def __init__(self, model):

		self.model = model
		self.egggroup = pygame.sprite.Group()

		self.num_eggs = 0

	def drop_eggs(self, side, top, xvel):
		"""
		Creates a new egg shot given a key press on space, adds it to the group
		"""
		temp = EggShot(side, top, xvel, self.model)

		temp.add(self.egggroup)

	def update(self, hawks, dt):
		"""
		updates the eggs, checking for out of range and moving them
		"""

		for egg in self.egggroup:
			if not egg.is_in_range():
				egg.kill()
				self.num_eggs -= 1

		for egg in self.egggroup:
			egg.update(hawks, dt)		
				

class Hawk(pygame.sprite.Sprite):
	"""
	The Hawk Class, the predators
	"""

	def __init__(self, pos, xvel, top_hawk):
		pygame.sprite.Sprite.__init__(self)


		self.alive = True # The hawk's life, in reference to eggs

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
		

		if top_hawk:   #if top hawk, then determines where the hawk will appear from on the top and bottom
			self.ypos = pos
			if pos == -150 or pos == SCREEN_H:
				self.xpos = random.randint(-150, SCREEN_W)
			else:
				self.xpos = random.choice([-150, SCREEN_W])	
		else:		                        #if not, then determines where the hawk will appear from the sides
			self.xpos = pos
			if pos == -150 or pos == SCREEN_W:
				self.ypos = random.randint(-150,SCREEN_H)
			else:
				self.ypos = random.choice([-150,SCREEN_H])


		if  self.xpos > SCREEN_W/2:  #orients the hawk properly based on where it came from
			self.xvel = -1 * xvel
		else:
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

	def update(self, chicken, dt, start):
		"""
		Updates hawks to chase the chicken
		"""

		self.dt_image += dt

		if self.alive:
			self.counter += dt  
			if not start:
				if self.counter > 2:  #wait 2 seconds before letting hawks fly in
					x_diff = chicken.rect.right - self.rect.right   
					y_diff = chicken.rect.top - self.rect.top
					vector_mag = math.sqrt(x_diff**2 + y_diff**2) * 5   #calculates how to chase the chicken
					self.xvel = self.xvel + x_diff / vector_mag 
					if self.xvel < 0:
						self.sprite_num = 2  #changes orientation of hawk based on which direction it's flying
					else:
						self.sprite_num = 1   #changes orientation based on direction of flight
					self.yvel = self.yvel + y_diff / vector_mag

					self.rect = self.rect.move(self.xvel, self.yvel)
					self.hitbox = self.hitbox.move(self.xvel, self.yvel)

				if self.dt_image > self.animation_speed:    #changes the image incrementally based on time for animation
					self.index += 1
					if self.index >= 4:
						self.index = 0
					self.dt_image = 0
					self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num * self.height, self.width, self.height))
					self.image = self.sheet.subsurface(self.sheet.get_clip())  
				
		else:

			self.sheet.set_clip(pygame.Rect(0 * self.width, 5 * self.height, self.width -17, self.height)) #subimage for dead hawk
			self.image = self.sheet.subsurface(self.sheet.get_clip())

			if self.sprite_num == 2 :   #if the hawk was facing the other direction when dying, it will flip the death image
				self.image = pygame.transform.flip(self.image, True, False)
			self.xvel = 0
			self.yvel = 10

			self.rect = self.rect.move(self.xvel, self.yvel)
			self.hitbox = self.hitbox.move(5000, 5000)

	
		self.image = pygame.transform.scale(self.image, (150,150))


class Boss_Hawk(pygame.sprite.Sprite):
	"""
	The Hawk Class, the predators
	"""

	def __init__(self, pos, xvel, top_hawk):
		pygame.sprite.Sprite.__init__(self)


		self.alive = True # The hawk's life, in reference to eggs

		self.sheet = pygame.image.load('bosshawkspritesheet.png')
		self.sprite_num = 2  #row of the subimage
		self.dt_image = 0.0
		self.counter = 0.0  #counter for delay of start
		self.index = 0  #column of the subimage
		self.animation_speed = 0.10  #animation speed of the hawk

		self.width = 85  #width ofthe subimage
		self.height = 69.95   #height of the subimage

		self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num * self.height, self.width, self.height))
		self.image = self.sheet.subsurface(self.sheet.get_clip())  #set and get subimage

		self.image = pygame.transform.scale(self.image, (300,300))
		self.index += 1
		

		if top_hawk:   #if top hawk, then determines where the hawk will appear from on the top and bottom
			self.ypos = pos
			if pos == -300 or pos == SCREEN_H:
				self.xpos = random.randint(-300, SCREEN_W)
			else:
				self.xpos = random.choice([-300, SCREEN_W])	
		else:		                        #if not, then determines where the hawk will appear from the sides
			self.xpos = pos
			if pos == -300 or pos == SCREEN_W:
				self.ypos = random.randint(-300,SCREEN_H)
			else:
				self.ypos = random.choice([-300,SCREEN_H])


		if  self.xpos > SCREEN_W/2:  #orients the hawk properly based on where it came from
			self.xvel = -1 * xvel
		else:
			self.sprite_num = 1
			self.xvel = xvel	

		if self.ypos > SCREEN_H/2:	
			self.yvel = -1 * 4
		else:
			self.yvel = 4

		self.rect = pygame.Rect(self.xpos, self.ypos, 300, 300)	
		self.hitbox = pygame.Rect(self.xpos + 37.5, self.ypos + 37.5, 225, 225)

	def is_in_range(self):
		"""
		Checks if still within screen boundaries
		"""

		return self.rect.right <= SCREEN_W +300 and self.rect.left >= -300 and self.rect.bottom <= SCREEN_H+300 and self.rect.top >= -300	

	def update(self, chicken, dt, start):
		"""
		Updates hawks to chase the chicken
		"""

		self.dt_image += dt

		if self.alive:
			self.counter += dt  
			if not start:
				if self.counter > 2:  #wait 2 seconds before letting hawks fly in
					x_diff = chicken.rect.right - self.rect.right   
					y_diff = chicken.rect.top - self.rect.top
					vector_mag = math.sqrt(x_diff**2 + y_diff**2) * 7   #calculates how to chase the chicken
					self.xvel = self.xvel + x_diff / vector_mag 
					if self.xvel < 0:
						self.sprite_num = 2  #changes orientation of hawk based on which direction it's flying
					else:
						self.sprite_num = 1   #changes orientation based on direction of flight
					self.yvel = self.yvel + y_diff / vector_mag

					self.rect = self.rect.move(self.xvel, self.yvel)
					self.hitbox = self.hitbox.move(self.xvel, self.yvel)

				if self.dt_image > self.animation_speed:    #changes the image incrementally based on time for animation
					self.index += 1
					if self.index >= 4:
						self.index = 0
					self.dt_image = 0
					self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num * self.height, self.width, self.height))
					self.image = self.sheet.subsurface(self.sheet.get_clip())  
				
		else:

			self.sheet.set_clip(pygame.Rect(0 * self.width, 5 * self.height, self.width -17, self.height)) #subimage for dead hawk
			self.image = self.sheet.subsurface(self.sheet.get_clip())

			if self.sprite_num == 2 :   #if the hawk was facing the other direction when dying, it will flip the death image
				self.image = pygame.transform.flip(self.image, True, False)
			self.xvel = 0
			self.yvel = 10

			self.rect = self.rect.move(self.xvel, self.yvel)
			self.hitbox = self.hitbox.move(5000, 5000)

	
		self.image = pygame.transform.scale(self.image, (300,300))


		
class Flock():
	"""
	Represents all the Hawks in the game
	"""

	def __init__(self, model):

		self.model = model

		self.hawkfleet = pygame.sprite.Group()

		self.num_hawks = 0

		self.threshold = 3000
		self.counter = 0

		self.boss_threshold = 10000
		self.boss_counter = 0

		for i in range(1):  #makes a bunch of hawks
			Hawk(random.randint(-150,SCREEN_H), random.randint(1, 7), True).add(self.hawkfleet)
			Hawk(random.randint(-150,SCREEN_W), random.randint(1, 7), False).add(self.hawkfleet)
			self.num_hawks += 2

		

	def update(self, chicken, dt, start):		
		"""
		Updates hawks in the flock, checks if they're still in range
		"""

		if self.model.score >= self.threshold:
			if random.choice([True, False]):   
				Hawk(random.randint(-150,SCREEN_W), random.randint(1,7), True).add(self.hawkfleet)
				self.num_hawks += 1
			else:
				Hawk(random.randint(-150,SCREEN_H), random.randint(1,7), False).add(self.hawkfleet)
				self.num_hawks += 1

			self.counter += 3
			self.threshold = self.threshold + self.counter*1000

		if self.model.score >= self.boss_threshold:
			if random.choice([True, False]):   
				Boss_Hawk(random.randint(-300,SCREEN_W), random.randint(1,4), True).add(self.hawkfleet)
				self.num_hawks += 1
			else:
				Boss_Hawk(random.randint(-300,SCREEN_H), random.randint(1,4), False).add(self.hawkfleet)
				self.num_hawks += 1

			self.boss_counter += 2
			self.boss_threshold = self.boss_threshold + self.boss_counter*10000

		for hawk in self.hawkfleet:

			if not hawk.is_in_range():
				if not isinstance(hawk, Boss_Hawk):  #if a hawk goes out of range, kill it and replace it
					hawk.kill()
					self.num_hawks -= 1
					if random.choice([True, False]):  
						Hawk(random.randint(-150,SCREEN_W), random.randint(1,7), True).add(self.hawkfleet)
						self.num_hawks += 1
					else:
						Hawk(random.randint(-150,SCREEN_H), random.randint(1,7), False).add(self.hawkfleet)
						self.num_hawks += 1


		for hawk in self.hawkfleet:
			hawk.update(chicken, dt, start)	

class Plane(pygame.sprite.Sprite):

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

		self.sheet = pygame.image.load('plane.png')
		self.sprite_num = 0  #row of the subimage
		self.dt_image = 0.0
		self.counter = 0.0  #counter for delay of start
		self.index = 0  #column of the subimage
		self.animation_speed = 0.10  #animation speed of the hawk
		
		self.width = 120  #width ofthe subimage
		self.height = 62   #height of the subimage

		self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num * self.height, self.width, self.height))
		self.image = self.sheet.subsurface(self.sheet.get_clip())  #set and get subimage

		self.image = pygame.transform.scale(self.image, (200,100))

		self.index += 1

		self.xpos = 730
		self.ypos = 132

		self.yvel = 0
		self.xvel = 0

		self.rect = pygame.Rect(self.xpos, self.ypos, 120, 60)

	def move(self):

		self.rect = self.rect.move(self.xvel, self.yvel)

	def update(self, dt):

		if self.rect.bottom < -100:
			self.kill()

		else:
			self.move()

			self.dt_image += dt
			if self.dt_image > self.animation_speed:   #incrementally changes the subimage to make animation
				self.index += 1
				if self.index >= 4:
					self.index = 0
				self.dt_image = 0

				self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num * self.height, self.width, self.height+23))
				self.image = self.sheet.subsurface(self.sheet.get_clip())
			self.image = pygame.transform.scale(self.image, (200,100))

class Horizon(pygame.sprite.Sprite):

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('background.png')
		self.xpos = 0
		self.ypos = SCREEN_H
		self.yvel = -1
		self.animation_speed = 0.50
		self.dt_image = 0

		self.image = pygame.transform.scale(self.image, (SCREEN_W, SCREEN_H/2))
		self.rect = pygame.Rect(self.xpos, self.ypos, SCREEN_W, SCREEN_H/2)

	def move(self):

		self.rect = self.rect.move(0, self.yvel)

	def update(self, dt):

		if not self.rect.bottom < SCREEN_H:
			self.dt_image += dt
			if self.dt_image > self.animation_speed:
				self.move()
				self.dt_image = 0

		
class ChickenModel:
	"""
	Model for the game
	"""
	
	def __init__(self):
		self.width = SCREEN_W
		self.height = SCREEN_H

		self.plane = Plane()
		self.plane_group = pygame.sprite.Group(self.plane)
		self.horizon = Horizon()
		self.horizon_group = pygame.sprite.Group(self.horizon)
		self.chicken = Chicken()
		self.alive = self.chicken.alive
		self.chicken_sprite = pygame.sprite.Group(self.chicken)

		self.score = 0
		self.dt_score = 0
		self.score_speed = .1  #updates the score every .1 seconds


		self.Eggs = Eggs(self)

		self.hawks = Flock(self)

		self.sky = Sky(self, True, -10, 0)

	def update(self, dt, alive, start):
		"""
		Updates all the stuff
		"""

		if start:
			self.sky.xvel = -10
			self.sky.yvel = 0
			self.sky.left = True
			self.sky.update()
			self.plane_group.update(dt)
		else:
			self.sky.xvel = 0
			self.sky.yvel = -10
			
			self.sky.left = False

			self.sky.update()
			self.plane_group.update(dt)
			self.hawks.update(self.chicken, dt, start)
			self.chicken_sprite.update(self.hawks.hawkfleet, dt, self.alive)
			self.Eggs.update(self.hawks.hawkfleet, dt)
			self.horizon_group.update(dt)

		if self.chicken.alive:
			self.dt_score += dt

		self.alive = self.chicken.alive
		
		if self.dt_score >= self.score_speed:
			self.update_score(start)
			self.dt_score = 0	

	def update_score(self, start):
		"""
		Increements the score by 10 
		"""
		if not start:
			self.score += 10
	

	def get_drawables(self, start):
		"""
		Gives a list of things to draw in view
		"""
		if start:
			return [self.horizon_group, self.sky.clouds, self.hawks.hawkfleet, self.chicken_sprite, self.Eggs.egggroup, self.plane_group]
		else:
			return [self.horizon_group, self.plane_group, self.sky.clouds, self.hawks.hawkfleet, self.chicken_sprite, self.Eggs.egggroup]

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
		pygame.display.set_caption('CAP\'N CHICKEN')

		pygame.font.init()
		self.font2 = pygame.font.Font(CURR_DIR + '/Chicken.ttf', 100)
		self.font = pygame.font.Font(CURR_DIR + '/Chicken2.ttf', 80)
		self.font3 = pygame.font.Font(CURR_DIR + '/Chicken3.ttf', 80)

		self.start_screen = self.font2.render('CAP\'N CHICKEN', False, RED)
		self.start_screen1 = self.font.render('USE THE ARROW KEYS TO MOVE', False, BLACK)
		self.start_screen2= self.font.render('USE SPACE TO FIRE EGGS', False, BLACK)
		self.start_screen3 = self.font.render('KILL AND DODGE VILLANOUS HAWKS', False, BLACK)
		self.start_screen4 = self.font.render('LAST AS LONG AS YOU CAN!!!', False, BLACK)
		self.start_screen5 = self.font3.render('PRESS ANY KEY TO START', False, RED)

		self.game_over = self.font2.render('GAME OVER', False, RED)
		self.restart = self.font.render('Press r to restart',False, RED)
		self.quit = self.font.render('Press Esc to quit', False, RED)

		if os.path.exists(CURR_DIR + '/hiscore.txt'):
			self.hiscore = str(pickle.load(open(CURR_DIR + '/hiscore.txt', 'rb')))
		else: 
			self.hiscore = '0'
		self.hiscore_surf = self.font.render("HIGH: {}".format(self.hiscore), False, BLACK)

	def fill_gradient(self,color, gradient, rect=None, vertical=True, forward=True):
	    """fill a surface with a gradient pattern
	    Parameters:
	    color -> starting color
	    gradient -> final color
	    rect -> area to fill; default is surface's rect
	    vertical -> True=vertical; False=horizontal
	    forward -> True=forward; False=reverse
	    
	    """
	    if True: 
	    	rect = self.screen.get_rect()

	    x1 = rect.left
	    x2 = rect.right
	    y1 = rect.top
	    y2 = rect.bottom
	    if vertical: 
	    	h = y2-y1
	    else: 
	        h = x2-x1
	    if forward:
	    	a, b = color, gradient
	    else:       
	    	b, a = color, gradient
	    rate = (
	        float(b[0]-a[0])/h,
	        float(b[1]-a[1])/h,
	        float(b[2]-a[2])/h
	    )
	    fn_line = pygame.draw.line
	    if vertical:
	        for line in range(y1,y2):
	            color = (
	                min(max(a[0]+(rate[0]*(line-y1)),0),255),
	                min(max(a[1]+(rate[1]*(line-y1)),0),255),
	                min(max(a[2]+(rate[2]*(line-y1)),0),255)
	            )
	            fn_line(self.screen, color, (x1,line), (x2,line))
	    else:
	        for col in range(x1,x2):
	            color = (
	                min(max(a[0]+(rate[0]*(col-x1)),0),255),
	                min(max(a[1]+(rate[1]*(col-x1)),0),255),
	                min(max(a[2]+(rate[2]*(col-x1)),0),255)
	            )
	            fn_line(self.screen, color, (col,y1), (col,y2))	
     
	def draw(self, alive, start):
		"""
		Redraws game windows, fetching drawables from model
		"""
		self.fill_gradient(pygame.Color(0,34,102), WHITE)

		drawables = self.model.get_drawables(start)

		for g in drawables:
			g.draw(self.screen)	

		if start:
			self.screen.blit(self.start_screen, (SCREEN_W/2 - 270, 230))
			self.screen.blit(self.start_screen1, (SCREEN_W/2 - 300, 375))
			self.screen.blit(self.start_screen2, (SCREEN_W/2 - 270, 475))
			self.screen.blit(self.start_screen3, (SCREEN_W/2 - 375, 575))
			self.screen.blit(self.start_screen4, (SCREEN_W/2 - 280, 675))
			self.screen.blit(self.start_screen5, (SCREEN_W/2 - 390, 775))

		self.draw_score()	

		if not alive:
			self.screen.blit(self.game_over, (SCREEN_W/2 - 200,SCREEN_H/2 - 80))
			self.screen.blit(self.restart, (SCREEN_W/2 - 140,SCREEN_H/2 + 100))
			self.screen.blit(self.quit, (SCREEN_W/2 - 140,SCREEN_H/2 + 200))

		pygame.display.flip()	

	def draw_score(self):
		"""
		Draws the score in the upper left hand corner, both current and high
		"""
		self.score_surf = self.font.render("CURRENT: {}".format(self.model.score), False, BLACK)
		self.screen.blit(self.score_surf, (20,100))
		self.screen.blit(self.hiscore_surf, (20,10))	


class ChickenController:
	"""
	Controller for Player
	"""

	def __init__(self, model):
		self.model = model
		self.done = False
		self.restart = False
		self.quit = False

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

					if k == pygame.K_DOWN:
						self.model.chicken.yvel = 12
						self.model.chicken.animation_speed = 0.20

					if k == pygame.K_UP:
						self.model.chicken.yvel = -12
						self.model.chicken.animation_speed = 0.06

					if k == pygame.K_RIGHT:
						self.model.chicken.xvel = 12

					if k == pygame.K_LEFT:
						self.model.chicken.xvel = -12

					if k ==pygame.K_SPACE:
						if self.model.chicken.xvel > 0:
							self.model.Eggs.drop_eggs(self.model.chicken.rect.left, self.model.chicken.rect.top, self.model.chicken.xvel)
						else:
							self.model.Eggs.drop_eggs(self.model.chicken.rect.right, self.model.chicken.rect.top, self.model.chicken.xvel)


				elif event.type == pygame.KEYUP:
					k = event.key

					if k == pygame.K_DOWN and self.model.chicken.yvel == 12:
						self.model.chicken.yvel = -3
						self.model.chicken.animation_speed = 0.10		
					if k == pygame.K_UP and self.model.chicken.yvel == -12:
						self.model.chicken.yvel = -3
						self.model.chicken.animation_speed = 0.10	
					if k == pygame.K_LEFT and self.model.chicken.xvel == -12:
						self.model.chicken.xvel = -.01
					if k == pygame.K_RIGHT and self.model.chicken.xvel == 12:
						self.model.chicken.xvel = .01

		else:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					k = event.key
					if  k == pygame.K_ESCAPE:
						self.done = True
						self.quit = True

					if k == pygame.K_r:
						self.done = True
						self.restart = True				

		return self.done, self.restart, self.quit							


	

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



	def restart(self):
		"""
		Restarts the game through the game over sign, re-initializes everything and then restarts the main loop
		"""
		self.model = ChickenModel()
		self.view = ChickenView(self.model)
		self.controller = ChickenController(self.model)
		self.clock = pygame.time.Clock()
		self.MainLoop()	


	def gameover(self):
		"""
		Presentation after Chicken has died, gives option to quit or restart, upon which you enter the restart method
		"""

		done = False
		start = False
		restart = False
		quit = False
		lastGetTicks = pygame.time.get_ticks()

		loop = True

		while loop:
			t = pygame.time.get_ticks()
			dt = (t - lastGetTicks) / 1000.0
			lastGetTicks = t

			done, restart, quit = self.controller.process_events(self.model.alive)
			self.model.update(dt, self.model.alive, start)
			self.view.draw(self.model.alive, start)

			if restart ==  True:
				self.restart()
			elif quit ==  True:
				loop = False
				pygame.quit()
				sys.exit()
				break	

		
	def MainLoop(self):
		"""
		Game Loop
		"""

		lastGetTicks = pygame.time.get_ticks()

		start = True
		done = False


		while not done:  #iterates while alive

			if self.model.alive:  #while alive, will do stuff normally


				t = pygame.time.get_ticks()
				dt = (t - lastGetTicks) / 1000.0
				lastGetTicks = t

				self.model.update(dt, self.model.alive, start)
				self.view.draw(self.model.alive, start)
				if not start:
					done, restart, quit = self.controller.process_events(self.model.alive)
				else:
					for event in pygame.event.get():
						if event.type == pygame.KEYDOWN:
							start = False
							self.model.plane.yvel = -2
							self.model.plane.xvel = 2

				self.clock.tick(FRAMERATE)		

			else:                  #while dead, will go for a falling scene until out of the screen, then ends
				while self.model.chicken.rect.top < SCREEN_H:
					t = pygame.time.get_ticks()
					dt = (t - lastGetTicks) / 1000.0
					lastGetTicks = t

					done, restart, quit = self.controller.process_events(self.model.alive)
					self.model.update(dt, self.model.alive, start)
					self.view.draw(self.model.alive, start)

					self.clock.tick(FRAMERATE)
				done = True		

				if os.path.exists(CURR_DIR + '/hiscore.txt'):
					count = pickle.load(open(CURR_DIR + '/hiscore.txt', 'rb'))
				else:
					count = 0
                if self.model.score > count:
                    count = self.model.score
                pickle.dump(count,open(CURR_DIR + '/hiscore.txt', 'wb'))           






if __name__ == '__main__':
	MainWindow = ChickenMain()
	MainWindow.MainLoop()
	MainWindow.gameover()