#!/usr/bin/env python2.7
import sys
import naoqi
from naoqi import ALProxy
import time
import almath
import rospy
import roslib
from move_naoqi import Mover
import game
from hang_nao.msg import GameState, NewTurn

# message on program exit
def my_hook():
	print "shutting down"


rospy.on_shutdown(my_hook)

NM = Mover()
NM.body_reset()
NG = game.HangMan()

def look():
	NM.target()


def yes():
	if NM.score < 0.8:
		NM.head_nod()
		look()
	else:
		NM.head_nod()
		NM.cheer()
		NM.body_reset()
		look()
	return


def no():
	NM.head_shake()
	look()
	return


def victory():
	NM.cheer()
	NM.cheer()
	NM.body_reset()

def defeat():
	NM.head_shake()
	NM.head_shake()


def answer(response):
	playerID = NG.cp
	NM.score = NG.pl[playerID].score
	NM.pp = NG.pl[playerID].pos
	look()
	if response.turn > 0:
		if bool(response.win):
			victory()
		else:
			if response.verify == 1:
				yes()
			if response.verify == 0:
				no()
			if response.verify == 2:
				NM.idle()
	else:
		defeat()


def update_turn(newturn):
	NM.change = True

rospy.Subscriber('/game/GameState', GameState, answer)
rospy.Subscriber('/game/NewTurn', NewTurn, update_turn)
NG.game_start()


