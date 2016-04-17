"""
The  Interactive Vertical-Scrolling Shooting Game of Chickens, made with pygame

Cap'n Chicken the Game

Kevin Zhang and Daniel Daugherty
Software Design Spring 2016
"""


import pygame, sys, os
from pygame.locals import *
import random, math
import pickle
import alsaaudio
import audioop

FRAMERATE = 60  #fps for the game

# Colors
BLACK    = (  0,   0,   0)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
SCREEN_W = 1600
SCREEN_H = 900

CURR_DIR = os.path.dirname(os.path.realpath(__file__))  #used for filepathing


class Cloud(pygame.sprite.Sprite):
	"""
	Clouds for the game background
	"""

	def __init__(self, xpos, ypos, xvel, yvel):
		"""
		xpos: x position of cloud on screen
		ypos: y position of cloud on screen
		xvel: speed in which cloud moves across the screen horizontally
		yvel: speed in which cloud moves across the screen vertically
		"""
		pygame.sprite.Sprite.__init__(self)


		#making the image

		self.image = pygame.image.load('cloud2.png')   #loading cloud picture

		self.scale = random.random() + 1  #scaling number for cloud size and cloud speed
		self.image = pygame.transform.scale(self.image, (int(self.scale*200),int(self.scale*100)))   #scales the clouds to a randomly set size
		self.image.fill((255, 255, 255, 200), None, pygame.BLEND_RGBA_MULT) #makes the clouds transparent for better visibility
		if random.randint(0,1):
			self.image = pygame.transform.flip(self.image, True, False)   #randomly flips the clouds for variety

		#determining position
		
		self.xpos = xpos
		self.ypos = ypos
		self.rect = pygame.Rect(self.xpos, self.ypos, self.image.get_width(), self.image.get_height())   #rect for Sprite
		self.yvel = yvel
		self.xvel = xvel


	def is_in_range(self):
		"""
		Checks if the cloud hit the top, or the right in regards to the starting screen
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

	def __init__(self, left, xvel, yvel):
		"""
		left: Boolean to see if clouds are at start screen sequence
		xvel: speed in which cloud moves across the screen horizontally
		yvel: speed in which cloud moves across the screen vertically
		"""

		# self.model = model
		self.clouds = pygame.sprite.Group() #creates a group to hold all clouds on the screen
		self.left = left
		self.xvel = xvel
		self.yvel = yvel

		self.num_clouds = 0

		for i in range(10):
			self.clouds.add(Cloud(random.randint(0,SCREEN_W), random.randint(0,SCREEN_H), xvel, yvel))  #adds clouds to the group
			self.num_clouds += 1
	

	def update(self):	
		"""
		makes the clouds scroll up
		"""

		if not self.left:  #updating the starting screen
			for cloud in self.clouds:
				if not cloud.is_in_range():   #if the cloud is out of range, kill it and replace it with new a one
					cloud.kill()
					Cloud(random.randint(0,SCREEN_W), SCREEN_H, self.xvel, self.yvel).add(self.clouds)


		else:
			for cloud in self.clouds:   #updating the actual game
				if not cloud.is_in_range():   #if the cloud is out of range, kill it and replace it with new a one
					cloud.kill()
					Cloud(SCREEN_W, random.randint(0, SCREEN_H), self.xvel, self.yvel).add(self.clouds)

		for cloud in self.clouds:    # update all clouds to move up
			cloud.xvel = self.xvel
			cloud.yvel = self.yvel
			cloud.update()





class Chicken(pygame.sprite.Sprite):
	"""
	The main character, the Chicken class
	"""

	def __init__ (self):
		pygame.sprite.Sprite.__init__(self)

		#making the image

		self.alive = True # the chicken's life

		self.sheet = pygame.image.load('chickenspritesheet.png')  #chicken sprite sheet

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

		#determining the position

		
		self.xpos = SCREEN_W/2 -50
		self.ypos = 100
		self.xvel = 0
		self.yvel = 0
		self.rect = pygame.Rect(self.xpos, self.ypos, 100, 100)   #rect for Sprite
		self.hitbox = pygame.Rect(self.xpos + 25, self.ypos + 25, 50, 50)  #hitbox of the chicken, defined as 3/4 of its size
		

	def move(self, xvel, yvel):
		"""
		Moves the chicken around based on its rectangle

		xvel: speed in which chicken moves across the screen horizontally
		yvel: speed in which chicken moves across the screen vertically
		"""
		if self.alive:
			if not self.rect.right <= SCREEN_W:    #checks boundaries: top, bottom, left, right, and if out will reset it to be just inside the boundary
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

		hawks: array of existing hawks on the screen
		dt: updated time
		alive: boolean to check if chicken is alive
		"""


		self.correct_boxes()  #makes sure that the hitbox stays within the chicken's model
		self.move(self.xvel, self.yvel)  #moves the chicken
		self.collide(hawks)   #checks for collisions with hawks


		if alive:    #allows the chicken to update normally assuming it is alive

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
					self.image = pygame.transform.flip(self.image, True, False)  # if the chicken is flying the other way, flip the image

		else:   #makes the chicken take the dead subimage when it's no longer alive
			self.sheet.set_clip(pygame.Rect(2 * self.width+3, 3 * self.height+82, self.width, self.height+23))
			self.image = self.sheet.subsurface(self.sheet.get_clip())

		self.image = pygame.transform.scale(self.image, (125,100))


	def collide(self, hawks):
		"""
		Checks for collisions with hawks and chickens

		hawks: array of existing hawks on the screen
		"""

		for hawk in hawks:
			if self.hitbox.colliderect(hawk.hitbox):  #checks for collision between hitboxes
				self.alive = False  #officially rules the hawk as dead
				self.yvel = 10   #the chicken just drops off the screen
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
		"""
		side: side of the rectangle the chicken's butt is on
		top: top of the chicken rectangle box
		xvel: speed in which the egg travels across the screen horizontally
		model: model of the program
		"""

		pygame.sprite.Sprite.__init__(self)


		#making the image and animation
		self.model = model

		self.sheet = pygame.image.load('rolling_eggs.png')   #egg sprite sheet
		self.sprite_num = 0  #row of the subimage
		self.dt_image = 0.0
		self.index = 0   #column of the subimage
		self.animation_speed = .10  #animation speed of the egg rolling

		self.width = 20  #width of the subimage
		self.height = 20  #height of the subimage

		self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num * self.height, self.width, self.height))  #making the subimage for the egg
		self.image = self.sheet.subsurface(self.sheet.get_clip())

		self.image = pygame.transform.scale(self.image, (50, 50))
		self.index += 1

		#determining where the image is in the screen

		self.yvel = 20
		self.xvel = xvel  #x velocity is the same as the chicken's upon proc

		self.rect = pygame.Rect(side , top, 50, 50)

		if self.xvel > 0:    #makes the hitbox depending on where it was shot (from the left or right side of the chicken)
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

		xvel: speed in which the egg travels across the screen horizontally
		yvel: speed in which the egg travels across the screen vertically
		"""

		self.rect = self.rect.move(xvel, yvel)
		self.hitbox = self.hitbox.move(xvel, yvel)	

	def update(self, hawks, dt):
		"""
		Updates the egg, making it fall, checking for range and collisions.

		hawks: array of existing hawks on the screen
		dt: updated time
		"""
		self.dt_image +=dt

		self.move(self.xvel, self.yvel)   #moves the egg
		self.collide(hawks)  #checks for collisions for hawks

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

		hawks: array of existing hawks on the screen
		"""

		for hawk in hawks:
			if self.hitbox.colliderect(hawk.hitbox):
				if isinstance(hawk, Boss_Hawk):    #if the hawk is a Boss, then increment the score differently
					hawk.lives -= 1
					if hawk.lives == 0:
						hawk.alive = False    #hawk is officially no longer alive
						hawk.yvel = 15     #hawks drop off the screen
						hawk.xvel = 0
						self.model.score += 5000
					self.kill()

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
		"""
		model: model for the program
		"""

		self.model = model
		self.egggroup = pygame.sprite.Group()   #makes the Sprite Group for eggs

		self.num_eggs = 0

	def drop_eggs(self, side, top, xvel):
		"""
		Creates a new egg shot given a key press on space, adds it to the group

		side: side of the rectangle the chicken's butt is on
		top: top of the chicken's rectangle
		xvel: speed in which the egg travels across the screen horizontally
		"""
		temp = EggShot(side, top, xvel, self.model)    

		temp.add(self.egggroup)

	def update(self, hawks, dt):
		"""
		updates the eggs, checking for out of range and moving them

		hawks: array of existing hawks on the screen
		dt: updated time
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
		"""
		pos: position of hawk on the screen
		xvel: speed in which the hawk travels across the screen horizontally
		top_hawk: boolean determining whether hawk initilizes at top/bottom of screen or side of screen
		"""

		pygame.sprite.Sprite.__init__(self)


		self.alive = True # The hawk's life, in reference to eggs


		#makes the image

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


		#determines position
		

		if top_hawk:   #if top hawk, then determines where the hawk will appear from on the top and bottom
			self.ypos = pos
			if pos == -150 or pos == SCREEN_H:
				self.xpos = random.randint(-150, SCREEN_W)
			else:
				self.xpos = random.choice([-150, SCREEN_W])	

		else:		      #if not, then determines where the hawk will appear from the sides
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
		self.hitbox = pygame.Rect(self.xpos + 37.5, self.ypos + 37.5, 75, 75)

	def is_in_range(self):
		"""
		Checks if still within screen boundaries
		"""

		return self.rect.right <= SCREEN_W +150 and self.rect.left >= -150 and self.rect.bottom <= SCREEN_H+150 and self.rect.top >= -150	

	def update(self, chicken, dt, start):
		"""
		Updates hawks to chase the chicken

		chicken: chicken object
		dt: updated time
		start: boolean determing whether game has started yet
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

					self.rect = self.rect.move(self.xvel, self.yvel)  #moves the hawks
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
			self.yvel = 10   #the hawk drops off the screen

			self.rect = self.rect.move(self.xvel, self.yvel)   #move the hawk
			self.hitbox = self.hitbox.move(5000, 5000)    #the hitbox is essentially removed from the screen

	
		self.image = pygame.transform.scale(self.image, (150,150))


class Boss_Hawk(pygame.sprite.Sprite):
	"""
	The Alpha Hawk Class, the head honcho worth millions
	"""

	def __init__(self, pos, xvel, top_hawk):
		"""
		pos: position of hawk on the screen
		xvel: speed in which the hawk travels across the screen horizontally
		top_hawk: boolean determining whether hawk initilizes at top/bottom of screen or side of screen
		"""

		pygame.sprite.Sprite.__init__(self)


		self.alive = True # The  Boss hawk's life, in reference to eggs


		#making the image

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
		self.lives = 3

		#determining the position

		

		if top_hawk:   #if top hawk, then determines where the hawk will appear from on the top and bottom
			self.ypos = pos
			if pos == -300 or pos == SCREEN_H:
				self.xpos = random.randint(-300, SCREEN_W)
			else:
				self.xpos = random.choice([-300, SCREEN_W])	
		else:		      #if not, then determines where the hawk will appear from the sides
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

		self.rect = pygame.Rect(self.xpos, self.ypos, 300, 300)	   #bigger size for the hawk
		self.hitbox = pygame.Rect(self.xpos + 37.5, self.ypos + 37.5, 225, 225)

	def is_in_range(self):
		"""
		Checks if still within screen boundaries
		"""

		return self.rect.right <= SCREEN_W +300 and self.rect.left >= -300 and self.rect.bottom <= SCREEN_H+300 and self.rect.top >= -300	

	def update(self, chicken, dt, start):
		"""
		Updates hawks to chase the chicken

		chicken: chicken object
		dt: updated time
		start: boolean determing whether game has started
		"""

		self.dt_image += dt

		if self.alive:
			self.counter += dt  
			if not start:
				if self.counter > 2:  #wait 2 seconds before letting boss fly in
					x_diff = chicken.rect.right - self.rect.right   
					y_diff = chicken.rect.top - self.rect.top
					vector_mag = math.sqrt(x_diff**2 + y_diff**2) * 7   #calculates how to chase the chicken
					self.xvel = self.xvel + x_diff / vector_mag 
					if self.xvel < 0:
						self.sprite_num = 2  #changes orientation of hawk based on which direction it's flying
					else:
						self.sprite_num = 1   #changes orientation based on direction of flight
					self.yvel = self.yvel + y_diff / vector_mag

					self.rect = self.rect.move(self.xvel, self.yvel)   #moves the boss hawk
					self.hitbox = self.hitbox.move(self.xvel, self.yvel)

				if self.dt_image > self.animation_speed:    #changes the image incrementally based on time for animation
					self.index += 1
					if self.index >= 4:
						self.index = 0
					self.dt_image = 0
					self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num * self.height, self.width, self.height))
					self.image = self.sheet.subsurface(self.sheet.get_clip())  
				
		else:

			self.sheet.set_clip(pygame.Rect(0 * self.width, 5 * self.height, self.width -17, self.height)) #subimage for dead boss
			self.image = self.sheet.subsurface(self.sheet.get_clip())

			if self.sprite_num == 2 :   #if the hawk was facing the other direction when dying, it will flip the death image
				self.image = pygame.transform.flip(self.image, True, False)
			self.xvel = 0
			self.yvel = 10  #boss drops off the screen

			self.rect = self.rect.move(self.xvel, self.yvel)   #moves the boss
			self.hitbox = self.hitbox.move(5000, 5000)  #boss's hitbox is removed from the game

	
		self.image = pygame.transform.scale(self.image, (300,300))


		
class Flock():
	"""
	Represents all the Hawks in the game
	"""

	def __init__(self, model):
		"""
		model: model for the game
		"""

		self.model = model

		self.hawkfleet = pygame.sprite.Group()  #group for all hawks, both little and alpha

		self.num_hawks = 0

		self.threshold = 3000    #threshold for increasing the number of hawks
		self.counter = 0   #counter for increasing the threshold

		self.boss_threshold = 10000  #theshold for releasing boss hawks into the game
		self.boss_counter = 0   #counter for increasing the boss threshold

		for i in range(1):  #makes a bunch of hawks
			Hawk(random.randint(-150,SCREEN_H), random.randint(1, 7), True).add(self.hawkfleet)
			Hawk(random.randint(-150,SCREEN_W), random.randint(1, 7), False).add(self.hawkfleet)
			self.num_hawks += 2

		

	def update(self, chicken, dt, start):		
		"""
		Updates hawks in the flock, checks if they're still in range

		chicken: chicken object
		dt: updated time
		start: boolean determining whether game has started
		"""

		if self.model.score >= self.threshold:    #if the score passes the regular threshold, make a new hawk
			if random.choice([True, False]):   
				Hawk(random.randint(-150,SCREEN_W), random.randint(1,7), True).add(self.hawkfleet)
				self.num_hawks += 1
			else:
				Hawk(random.randint(-150,SCREEN_H), random.randint(1,7), False).add(self.hawkfleet)
				self.num_hawks += 1

			self.counter += 4   #increment the counter
			self.threshold = self.threshold + self.counter*1000  #set the new threshold to be a function higher than the previous one

		if self.model.score >= self.boss_threshold:   #if the score passes the boss threshold, summon a boss
			if random.choice([True, False]):   
				Boss_Hawk(random.randint(-300,SCREEN_W), random.randint(1,4), True).add(self.hawkfleet)
				self.num_hawks += 1
			else:
				Boss_Hawk(random.randint(-300,SCREEN_H), random.randint(1,4), False).add(self.hawkfleet)
				self.num_hawks += 1

			self.boss_counter += 2   #increment the counter 
			self.boss_threshold = self.boss_threshold + self.boss_counter*10000  #set the new threshold to be a function higher than the previous one

		for hawk in self.hawkfleet:

			if not hawk.is_in_range():    #if a hawk goes out of range, kill it and replace it
				if not isinstance(hawk, Boss_Hawk):  #makes sure that the boss hawks never leave the game until they're killed
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

	"""
	The Plane for the start screen
	"""

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)


		#makes the image

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

		#determines position

		self.xpos = 730
		self.ypos = 132

		self.yvel = 0
		self.xvel = 0

		self.rect = pygame.Rect(self.xpos, self.ypos, 120, 60)

	def move(self):
		"""
		moves the plane to slowly fly out of the screen upon start
		"""

		self.rect = self.rect.move(self.xvel, self.yvel)

	def update(self, dt):
		"""
		updates the plane, basically making it move

		dt: updated time
		"""

		if self.rect.bottom < -100:   #if it's out of the screen, then kill the plane
			self.kill()

		else:
			self.move()   #else move the plane

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
	"""
	Makes the background horizon
	"""

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)


		#makes the image and position

		self.image = pygame.image.load('background.png')
		self.xpos = 0
		self.ypos = SCREEN_H
		self.yvel = -1
		self.animation_speed = 0.50
		self.dt_image = 0

		self.image = pygame.transform.scale(self.image, (SCREEN_W, SCREEN_H/2))
		self.rect = pygame.Rect(self.xpos, self.ypos, SCREEN_W, SCREEN_H/2)

	def move(self):
		"""
		moves the horizon slowly to come up
		"""

		self.rect = self.rect.move(0, self.yvel)

	def update(self, dt):
		"""
		updates the horizon to slowly rise, making it appear as though you were falling in the sky

		dt: updated time
		"""
		if not self.rect.bottom < SCREEN_H:  #makes sure the picture doesn't come off the bottom of the screen
			self.dt_image += dt   
			if self.dt_image > self.animation_speed:  #moves the pictures based on an increment
				self.move()
				self.dt_image = 0

		
class ChickenModel:
	"""
	Model for the game
	"""
	
	def __init__(self):
		self.width = SCREEN_W
		self.height = SCREEN_H

		self.plane = Plane()    #makes the plane
		self.plane_group = pygame.sprite.Group(self.plane)  #puts the plane in its own group for drawing
		self.horizon = Horizon()   #makes the horizon
		self.horizon_group = pygame.sprite.Group(self.horizon)  #puts the horizon in its own group for drawing
		self.chicken = Chicken() #makes the chicken
		self.alive = self.chicken.alive  #gets the life of the chicken
		self.chicken_sprite = pygame.sprite.Group(self.chicken)  #puts the chicken in its own group for drawing
		self.score = 0  #initializes the score
		self.dt_score = 0
		self.score_speed = .1  #updates the score every .1 seconds


		self.Eggs = Eggs(self)

		self.hawks = Flock(self)

		self.sky = Sky(True, -10, 0)

	def update(self, dt, alive, start):
		"""
		Updates all the stuff

		dt: updated time
		alive: boolean determing whether chicken is alive or not
		start: boolean determining whether game has started
		"""

		if start:   #separate updating for the start screen
			self.sky.xvel = -10
			self.sky.yvel = 0
			self.sky.left = True
			self.sky.update()
			self.plane_group.update(dt)
		else:   #updating for the real game
			self.sky.xvel = 0
			self.sky.yvel = -10
			
			self.sky.left = False


			#update everything

			self.sky.update()
			self.plane_group.update(dt)
			self.hawks.update(self.chicken, dt, start)
			self.chicken_sprite.update(self.hawks.hawkfleet, dt, self.alive)
			self.Eggs.update(self.hawks.hawkfleet, dt)
			self.horizon_group.update(dt)

		if self.chicken.alive:   #increments the score as long as the chicken is alive
			self.dt_score += dt

		self.alive = self.chicken.alive
		
		if self.dt_score >= self.score_speed:   #updates the score
			self.update_score(start)
			self.dt_score = 0	

	def update_score(self, start):
		"""
		Increements the score by 10 

		start: boolean determining whether game has started
		"""
		if not start:
			self.score += 10
	

	def get_drawables(self, start):
		"""
		Gives a list of things to draw in view

		start: boolean determining whether game has started
		"""
		if start:   #different list for the start screen
			return [self.horizon_group, self.sky.clouds, self.hawks.hawkfleet, self.chicken_sprite, self.Eggs.egggroup, self.plane_group]
		else:
			return [self.horizon_group, self.plane_group, self.sky.clouds, self.hawks.hawkfleet, self.chicken_sprite, self.Eggs.egggroup]

class ChickenView:
	"""
	View for Game
	"""
	def __init__(self, model):
		"""
		model: model for game
		"""

		pygame.init() 

		self.width = SCREEN_W
		self.height = SCREEN_H
		self.model = model
		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption('CAP\'N CHICKEN')


		#text for the game

		pygame.font.init()
		self.font2 = pygame.font.Font(CURR_DIR + '/Chicken.ttf', 100)
		self.font = pygame.font.Font(CURR_DIR + '/Chicken2.ttf', 80)
		self.font3 = pygame.font.Font(CURR_DIR + '/Chicken3.ttf', 80)

		self.start_screen = self.font2.render('CAP\'N CHICKEN', False, RED)
		self.start_screen1 = self.font.render('USE THE ARROW KEYS TO MOVE', False, BLACK)
		self.start_screen2= self.font.render('SCREAM TO FIRE EGGS', False, BLACK)
		self.start_screen3 = self.font.render('KILL AND DODGE VILLANOUS HAWKS', False, BLACK)
		self.start_screen4 = self.font.render('LAST AS LONG AS YOU CAN!!!', False, BLACK)
		self.start_screen5 = self.font3.render('PRESS ANY KEY TO START', False, RED)

		self.game_over = self.font2.render('GAME OVER', False, RED)
		self.restart = self.font.render('Press r to restart',False, RED)
		self.quit = self.font.render('Press Esc to quit', False, RED)


		#getting the score

		if os.path.exists(CURR_DIR + '/hiscore.txt'):
			self.hiscore = str(pickle.load(open(CURR_DIR + '/hiscore.txt', 'rb')))
		else: 
			self.hiscore = '0'
		self.hiscore_surf = self.font.render("HIGH: {}".format(self.hiscore), False, BLACK)
	
	def fill_gradient(self, color, gradient):
		"""
		fill the surface with a gradient 

		color: pygame color
		gradient: pygame color
		"""
		rect = self.screen.get_rect()
		x1 = rect.left
		x2 = rect.right
		y1 = rect.top
		y2 = rect.bottom

		h = y2 - y1 #defines the length of the gradient
		a, b = color, gradient

		rate = (float(b[0]-a[0])/h, float(b[1]-a[1])/h, float(b[2]-a[2])/h)  #rate of change for the three rgb values

		fn_line = pygame.draw.line   #makes the lines for the gradient

		for line in range(y1, y2):
			color = (min(max(a[0]+(rate[0]*(line-y1)),0),255), min(max(a[1]+(rate[1]*(line-y1)),0),255), min(max(a[2]+(rate[2]*(line-y1)),0),255))
			fn_line(self.screen, color, (x1, line), (x2, line))	
	def draw(self, alive, start):
		"""
		Redraws game windows, fetching drawables from model

		alive: boolean determining whether chicken is alive or not
		start: boolean determining whether game has started
		"""
		self.fill_gradient(pygame.Color(0,34,102), WHITE)  #draws the gradient

		drawables = self.model.get_drawables(start)  

		for g in drawables:   #for all things in drawables, draws them. Must be in a Group
			g.draw(self.screen)	

		if start:   #makes the start screen text
			self.screen.blit(self.start_screen, (SCREEN_W/2 - 270, 230))
			self.screen.blit(self.start_screen1, (SCREEN_W/2 - 300, 375))
			self.screen.blit(self.start_screen2, (SCREEN_W/2 - 240, 475))
			self.screen.blit(self.start_screen3, (SCREEN_W/2 - 375, 575))
			self.screen.blit(self.start_screen4, (SCREEN_W/2 - 280, 675))
			self.screen.blit(self.start_screen5, (SCREEN_W/2 - 390, 775))

		self.draw_score()	  #draws the score on the screen

		if not alive:  #if dead, draws the gameover screen
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
		"""
		model: model for game
		"""

		self.model = model
		self.done = False
		self.restart = False
		self.quit = False
		self.counter = 0
		self.volume_threshold = 500

	def process_events(self, alive, dt = 0):		
		"""
		Manages keypresses

		alive: boolean determining whether chicken is alive or not
		dt: updated time
		"""

		pygame.event.pump

		if alive:   #if alive, allow all controls
			self.eggFire(dt)
			for event in pygame.event.get():
				if event.type == QUIT:
					self.done = True

				elif event.type == pygame.KEYDOWN:	
					k = event.key

					if k == pygame.K_DOWN:
						self.model.chicken.yvel = 12
						self.model.chicken.animation_speed = 0.20  #flaps slower if going down

					if k == pygame.K_UP:  
						self.model.chicken.yvel = -12
						self.model.chicken.animation_speed = 0.06  #flaps faster if going up

					if k == pygame.K_RIGHT:
						self.model.chicken.xvel = 12

					if k == pygame.K_LEFT:
						self.model.chicken.xvel = -12

					# if k == pygame.K_SPACE:    #if press space, then make an egg object, which the egg being shot

				elif event.type == pygame.KEYUP:
					k = event.key

					if k == pygame.K_DOWN and self.model.chicken.yvel == 12:
						self.model.chicken.yvel = -3   #makes the chicken continually float up
						self.model.chicken.animation_speed = 0.10		
					if k == pygame.K_UP and self.model.chicken.yvel == -12:
						self.model.chicken.yvel = -3  #makes the chicken continually float up
						self.model.chicken.animation_speed = 0.10	
					if k == pygame.K_LEFT and self.model.chicken.xvel == -12:
						self.model.chicken.xvel = -.01
					if k == pygame.K_RIGHT and self.model.chicken.xvel == 12:
						self.model.chicken.xvel = .01

		else:   #if the chicken is dead, only allows two options, restarting or quitting the game
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

	def eggFire(self, dt):
		"""
		Checks if volume is loud enough to fire an egg periodically

		dt: updated time
		"""

		self.counter += dt
		if self.counter > 0.125:        # Will check if volume is loud enough after enough ticks happen (Reduces lag)
			inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,0)
			inp.setchannels(1)
			inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
			inp.setperiodsize(160)
			l,data = inp.read()        # Read volume levels
			if l:
				volume = audioop.rms(data,2)
			self.counter = 0           # Reset counter
			if volume >= self.volume_threshold:    #if loud enough, then make an egg object, which the egg being shot
				if self.model.chicken.xvel > 0:
					self.model.Eggs.drop_eggs(self.model.chicken.rect.left, self.model.chicken.rect.top, self.model.chicken.xvel)
				else:
					self.model.Eggs.drop_eggs(self.model.chicken.rect.right, self.model.chicken.rect.top, self.model.chicken.xvel)


class ChickenMain(object):
	"""
	Main Class
	"""

	def __init__(self, width = SCREEN_W, height = SCREEN_H):
		"""
		width: width of the screen in pixels
		height: height of the screen in pixels
		"""

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
		restart = False  #if True, will restart the game
		quit = False   #if True, will quit the game
		lastGetTicks = pygame.time.get_ticks()

		loop = True

		while loop:  #will continually loop until a control is pressed
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
					done, restart, quit = self.controller.process_events(self.model.alive, dt)
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
					
					done, restart, quit = self.controller.process_events(self.model.alive, dt)
					self.model.update(dt, self.model.alive, start)
					self.view.draw(self.model.alive, start)

					self.clock.tick(FRAMERATE)
				done = True		


				#pickles the score into a file

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