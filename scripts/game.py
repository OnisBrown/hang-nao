#!/usr/bin/env python2.7

import sys
import time
from random import randint
from hang_nao.msg import GameState, NewTurn
import rospy
import os

class Player:
	def __init__(self):
		self.score = 0.7
		self.id = 0
		self.pos = [0, 0]
		self.cg = 0

class HangMan:  # code built on example from http://www.pythonforbeginners.com/code-snippets-source-code/game-hangman
	def __init__(self):
		lh = open("wordlist.txt", "r")
		ah = lh.read()
		self.sh = ah.split()
		self.pl = list()
		self.cp = 0

		#message publishers and message objects
		self.gp = rospy.Publisher('/game/GameState', GameState, queue_size=1)
		self.tp = rospy.Publisher('/game/NewTurn', NewTurn, queue_size=1)
		self.gm = GameState()
		self.tm = NewTurn()

		self.pCount = int(raw_input("How many players are there? "))

		for i in range(self.pCount):
			self.pl.append(Player())
			self.pl[i].id = i + 1

		print str(len(self.pl)) + " players"

	def game_start(self):
		for r in range(1, 4):
			try:

				os.system('clear')
				print "Round " + str(r) + "!"
				print "\n__________________________________________\n"


				for s in self.pl: #resets players correct guesses
					s.cg = 0

				word = self.sh[randint(0, 212)]

				print "Time to play hangman!"
				print ""
				print "Start guessing..."
				rospy.sleep(1.0)

				#creates variables to track guesses
				guesses = ''
				misses = ''
				correct = ''
				turns = 12

				self.gm.win = 0


				#check if the turns are more than zero
				while turns > 0:
					self.tm.pt = self.cp
					self.tp.publish(self.tm)
					os.system('clear')
					# make a counter that starts with zero
					failed = 0
					# for every character in
					for char in word:
						if char in guesses:
							print char,

						else:
							print "_",
							failed += 1

					if failed == 0:
						print "\nYou won"
						self.gm.win = 1
						self.gp.publish(self.gm)
						raw_input('press enter...')
						break

					print "\n__________________________________________\n"

					# ask the user go guess a character
					print "Player " + str(self.pl[self.cp].id) + ' your turn\n'
					print "You have ", + turns, ' guesses remaining'
					print "\nIncorrect guesses: " + misses
					rospy.sleep(0.2)
					guess = raw_input("\nmake a guess (multiple characters or the word):\n ")
					print "\n"
					if guess == "!": # if the user inputs an exclamation mark exit the game
						break
					# set the players guess to guesses
					guesses += guess

					# if the guess is not found in the secret word
					for char in guess:
						if char not in word:
							if char not in misses:
								turns -= 1
								self.pl[self.cp].score -= 0.1
								self.gm.verify = 0
								misses += ' ' + char
								# print wrong
								print char + " is wrong"

							else:
								self.pl[self.cp].score -= 0.05
								self.gm.verify = 0
								print "You already guessed " + char

						else:
							if char in correct:
								print "You already guessed " + char
								self.pl[self.cp].score -= 0.05
							else:
								self.gm.verify = 1
								self.pl[self.cp].score += 0.1
								self.pl[self.cp].cg += 1
								print char + " is correct"

					if len(guess) > 1:
						self.gm.verify = 2

					if self.pl[self.cp].score < 0:
						self.pl[self.cp].score = 0

					if self.pl[self.cp].score > 1:
						self.pl[self.cp].score = 1

					# how many turns are left
					print "\nYou have", + turns, 'more guesses'

					# if the turns are equal to zero
					if turns < 0:
						print "\nYou Loose"
						self.gm.win = 0

					self.gm.turn = turns
					self.gp.publish(self.gm)

					rospy.sleep(2)
					os.system('clear')

					if self.cp >= self.pCount - 1:
						self.cp = 0
					else:
						self.cp += 1

			except KeyboardInterrupt:
				sys.exit()
