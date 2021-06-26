from random import randint


class Snake:
	def __init__(self, *, rows=10, cols=10, mode="diffs"):
		# mode determines return type
		# either the whole game grid or just the changes
		self.mode = mode

		# game grid size, denoted by number of rows and columns (cols)
		self.rows = rows
		self.cols = cols

		# builds up a blank game grid
		self.grid_blank = {}
		for r in range(rows):
			for c in range(cols):
				self.grid_blank[chr(65 + r) + "|" + str(c)] = "."

		# sets some default starting values for the game
		self.direction = "down"
		self.last_dir = "down"
		self.body = ["A|0"]

		# initialise a copy of the blank grid for the game
		self.grid = self.grid_blank.copy()

		# create the first apple at a random place.
		non_snake = list(self.grid.keys())
		non_snake.remove(self.body[0])
		self.apple = non_snake[randint(0, len(non_snake) - 1)]

		self.grid[self.apple] = 'O'
		for coord in self.body:
			self.grid.update({coord: "#"})

	def update_direction(self, new_dir):
		oppo_table = {"up": "down", "down": "up", "left": "right", "right": "left"}
		if new_dir != oppo_table[self.last_dir]:
			self.direction = new_dir

	def game_tick(self):
		diffs = {}
		row, col = self.body[-1].split("|")
		row, col = ord(row), int(col)
		old_grid = self.grid.copy()

		# modify the row and column of the head based on the snakes direction
		if self.direction in ["up", "down"]:
			row += {"up": -1, "down": 1}[self.direction]
		elif self.direction in ["left", "right"]:
			col += {"left": -1, "right": 1}[self.direction]

		# build the position string of the new head
		new_head = chr(row) + "|" + str(col)

		# a series of checks to determine if the new snake head position is valid
		validity = (col >= 0) and (col < self.cols)  # check if the column coord is in a valid range
		validity *= (row >= 65) and (row < self.rows + 65)  # check if the row coord is in a valid range
		validity *= not (new_head in self.body)  # check the new head position is not part of the snake body

		# if the new head is valid, have the snake move
		if validity:
			status = "safe"

			# save the last direction the snake moved
			self.last_dir = self.direction

			# add the new snake head position to the list of snake body coords
			self.body.append(new_head)
			# add the snake head to the grid
			diffs[new_head] = "#"
			self.grid[new_head] = "#"

			if new_head != self.apple:
				# if the new head is not the apple position, remove the snake tail
				tail = self.body.pop(0)
				self.grid[tail] = "."
				diffs[tail] = self.grid[tail]
			else:
				# if new head is the apple position, randomly place the next apple
				non_snake = list(set(self.grid.keys()).difference(set(self.body)))
				new_apple = non_snake[randint(0, len(non_snake) - 1)]
				self.grid[new_apple] = "O"
				diffs[new_apple] = self.grid[new_apple]
				self.apple = new_apple
		else:
			# if the new head position is not valid, reset the game
			status = "fail"
			diffs = self.reset()

		if self.mode == "diffs":
			return diffs, status
		else:
			return self.grid.copy(), status

	def reset(self):
		old_grid = self.grid.copy()
		# reinitialise the class with the same inputs as before
		self.__init__(rows=self.rows, cols=self.cols, mode=self.mode)
		# suppressing an incorrect warning
		# noinspection PyTypeChecker
		diffs = dict(set(self.grid.items()).difference(set(old_grid.items())))
		if self.mode == "diffs":
			return diffs
		else:
			return self.grid.copy()

	def diffs_from_blank(self):
		# suppressing an incorrect warning
		# noinspection PyTypeChecker
		diffs = dict(set(self.grid.items()).difference(set(self.grid_blank.items())))
		return diffs
