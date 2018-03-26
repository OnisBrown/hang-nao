#!/usr/bin/env python2.7
import sys
import naoqi
from naoqi import ALProxy
import time
import almath
import rospy
import roslib
from movement import Mover
import game
from hang_nao.msg import GameState, NewTurn
import cv2, cv_bridge
from sensor_msgs.msg import Image
from threading import Timer
from random import uniform, randint

class Decisions:
	def __init__(self):
		self.NM = Mover()
		self.NM.body_reset()
		self.NG = game.HangMan()
		self.bridge = cv_bridge.CvBridge()
		cv2.namedWindow("window", 1)
		rospy.Subscriber('/game/GameState', GameState, self.answer)
		rospy.Subscriber('/game/NewTurn', NewTurn, self.update_turn)
		rospy.Subscriber('/nao_robot/camera/top/image_raw', Image, self.head_view)
		self.NG.game_start()
		self.score = 0.7
		self.cp = 0
		self.change = False

	def head_view(self, img):
		image = self.bridge.imgmsg_to_cv2(img, desired_encoding='bgr8')
		cv2.imshow("window", image)
		cv2.waitKey(3)


	def yes(self):
		if self.score < 0.8:
			self.NM.head_nod(self.score)
			self.look()
		else:
			self.NM.head_nod(self.score)
			self.NM.cheer()
			self.NM.body_reset()
			self.look()
		return

	def look(self):
		self.NM.target()
		print str(self.NM.pp)

	def look_away(self):
		if self.change:
			self.NM.idle()
			bt = uniform(1.5, 2.0) - self.score  # time before nao looks back
			btt = Timer(bt, self.look)
			btt.start()
		print str(self.NM.pp)


	def no(self):
		self.NM.head_shake(self.score)
		self.look()

	def victory(self):
		self.NM.cheer()
		self.NM.cheer()
		self.NM.body_reset()

	def defeat(self):
		self.NM.head_shake(0)
		self.NM.head_shake(0)

	def answer(self, response):
		self.look()
		self.change = False
		if response.turn > 0:
			if bool(response.win):
				self.victory()
			else:
				if response.verify == 1:
					self.yes()
				if response.verify == 0:
					self.no()
		else:
			self.defeat()

	def update_turn(self, newturn):
		self.look()
		self.NM.body_reset()
		self.cp = newturn.pt
		self.change = True
		player = self.NG.pl[self.cp]
		self.NM.pp = player.pos
		self.score = player.score
		lt = uniform(2.0, 3.0) + self.score  # time before nao looks away
		rospy.sleep(0.5)
		ltt = Timer(lt, self.look_away)
		ltt.start()
		self.look()


def my_hook():
	print "shutting down"


rospy.on_shutdown(my_hook)
start = Decisions()