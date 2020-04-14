from maya import cmds

class Object:
	def setJob(self, attribute, method):
		cmds.scriptJob(runOnce = True, attributeChange = [attribute, method])

class Robot(Object):
	def __init__(self, robot = "robot"):
		self.robot = robot
		self.body = "{}|parentBody".format(robot)
		self.limbs = "{}.adjustLimbs".format(robot)
		self.emotion = "screen.displayEmotion"
		self.code = "screen.code"
		self.keyTime = [1 if t == 0 else t for t in range(0, 81, 5)]
		self.keyRotate = [-z*22.5 for z in range(len(self.keyTime))]
		self.currentEmotion = 0
		self.currentCode = 0
		self.happy = (41, 42, 52, 63, 55, 68, 93, 104, 91, 88, 99, 86)
		self.sad = (39, 65, 66, 44, 52, 55, 99, 104)
		self.angry = (86, 99, 88, 91, 104, 93, 39, 52, 65, 66, 55, 44)
		self.surprised = (99, 104, 77, 78, 64, 52, 41, 42, 67, 55)
		self.confused = (88, 101, 102, 91, 79, 66, 54, 30)
		self.bored = (86, 87, 88, 91, 92, 93, 51, 52, 53, 54, 55, 56)
		self.emotions = ((1, self.happy), (2, self.sad), (3, self.angry), (4, self.surprised), (5, self.confused), (6, self.bored))
		self.faces = [s+f for f in range(10) for s in range(13, 122, 12)]
		self.execute()
		
	def isChildOfBody(self, name, m):
		for _, child in enumerate(m):
			if name in child:
				return True
		return False
	
	def rotateParts(self, part, rotatePart):
		m = cmds.listRelatives(self.body, children = True)
		r = "{}.{}".format(self.body, part)
		s = cmds.getAttr(r)
		if s and not self.isChildOfBody(part, m):
			cmds.parent("{}|{}".format(self.robot, part), self.body)
		elif not s and self.isChildOfBody(part, m):
			cmds.parent("{}|{}".format(self.body, part), self.robot)
		cmds.select(self.body)
		self.setJob(r, rotatePart)
		
	def rotateLeft(self, left):
		self.rotateParts(left, lambda : self.rotateLeft(left))
		
	def rotateRight(self, right):
		self.rotateParts(right, lambda : self.rotateRight(right))
		
	def rotateHead(self):
		self.rotateParts("head", self.rotateHead)
		
	def rotateFrontLeft(self):
		self.rotateParts("frontLeft", self.rotateFrontLeft)

	def rotateFrontRight(self):
		self.rotateParts("frontRight", self.rotateFrontRight)

	def rotateBackLeft(self):
		self.rotateParts("backLeft", self.rotateBackLeft)

	def rotateBackRight(self):
		self.rotateParts("backRight", self.rotateBackRight)

	def adjustClaws(self, part, adjustClaw):
		cn = "{}|{}.adjustClaws".format(self.robot, part)
		n = cmds.getAttr(cn)
		claws = [("Left", "Z", 90-n), ("Right", "Z", 90+n), ("Top", "Y", n), ("Bottom", "Y", -n)]
		claws = tuple(claw for claw in claws if cmds.getAttr("{}.claw{}".format(part, claw[0])))
		for _, claw in enumerate(claws):
			name, r, d = claw
			cmds.setAttr("{}|ballParent1|ballParent2|parentClaw{}.rotate{}".format(part, name, r), d)
		self.setJob(cn, adjustClaw)
		
	def adjustClaws1(self, claws1 = "claws"):
		self.adjustClaws(claws1, lambda : self.adjustClaws1(claws1))
		
	def adjustClaws2(self, claws2 = ""):
		self.adjustClaws(claws2, lambda : self.adjustClaws2(claws2))

	def adjustLimbs(self, maximum = 0.58, left = "screen", right = "claws"):
		def slope(sx, sy, ex, ey):
			ex = -ex if sx < 0 else ex
			y = abs(ey-sy)
			x = abs(ex-sx)
			return y/x if x > 0 else y
			
		n = cmds.getAttr(self.limbs)
		limbs = [(left, "arm", n-0.74-0.118, -n+0.484, slope(n-0.74-0.118, -n+0.484, 0, -0.096)), (right, "arm", -n+0.74+0.118, -n+0.484, slope(-n+0.74+0.118, -n+0.484, 0.278, -0.096)), ("frontLeft", "leg", n+0.176, n-0.096, slope(0.176, -0.096, 0.727, 0.385)), ("frontRight", "leg", n+0.223, n-0.096, slope(0.223, -0.096, 0.727, 0.385)), ("backLeft", "leg", -n-0.223, n-0.096, slope(-0.223, -0.096, 0.727, 0.385)), ("backRight", "leg", -n-0.176, n-0.096, slope(-0.176, -0.096, 0.727, 0.385))]
		limbs = tuple(limb for limb in limbs if cmds.getAttr("{}.{}".format(self.robot, limb[0])))
		for _, limb in enumerate(limbs):
			name, m, j, y, s = limb
			ex = 0.278 if m == "arm" else 0.727
			ey = -0.096 if m == "arm" else 0.385
			o = maximum-n if m == "arm" else n
			mov = [("Y", y), ("Z" if m == "arm" else "X", j)]
			if o > 0.481:
				mov.pop()
			for _, p in enumerate(tuple(mov)):
				t, d = p
				cmds.setAttr("{}|{}.translate{}".format(self.robot, name, t), d)
		self.setJob(self.limbs, self.adjustLimbs)
		
	def applyMaterial(self, f, color):
		cmds.select("mScreen.f[{}]".format(f))
		cmds.sets(e = True, forceElement = color)
			
	def applyEmotion(self, faces, color = "screenColor1"):
		for _, f in enumerate(faces):
			self.applyMaterial(f, color)
			
	def clearScreen(self, faces):
		self.applyEmotion(faces, "aiStandardSurface4SG")
		
	def getEmotion(self):
		return tuple(f for (e, f) in self.emotions if e == self.currentEmotion)[0]
	
	def adjustScreen(self):
		if self.currentCode > 0:
			self.clearScreen(self.faces)
		if self.currentEmotion > 0:
			self.clearScreen(self.getEmotion())
		self.currentEmotion = cmds.getAttr(self.emotion)
		if self.currentEmotion > 0:
			self.applyEmotion(self.getEmotion())
		cmds.select("screen")
		self.setJob(self.emotion, self.adjustScreen)
		
	def displayCode(self):
		if self.currentEmotion > 0:
			self.clearScreen(self.getEmotion())
		self.currentCode = cmds.getAttr(self.code)
		if self.currentCode > 0:
			faces = self.faces[:len(self.faces)]
			cmds.select("mScreen.f[{}]".format(faces.pop(0)))
			for _, f in enumerate(faces):
				cmds.select("mScreen.f[{}]".format(f), toggle = True)
			cmds.sets(e = True, forceElement = "mCode{}".format(self.currentCode))
		else:
			self.clearScreen(self.faces)
		cmds.select("screen")
		self.setJob(self.code, self.displayCode)
		
	def ballCycle(self, part, cycleMethod):
		at = "rotateZ"
		cycle = "{}.{}".format(self.robot, part)
		ball = "{}|{}|ballParent1|ballParent2".format(self.robot, part.replace("cycleF", "f").replace("cycleB", "b"))
		if cmds.getAttr(cycle):
			for i, t in enumerate(self.keyTime):
				cmds.setKeyframe(ball, value = self.keyRotate[i], attribute = at, time = t)
			cmds.keyTangent(ball, inTangentType = "linear", attribute = at, time = (0, 81))
			cmds.setInfinity(ball, attribute = at, postInfinite = "cycle")
		else:
			cmds.cutKey(ball, time = (1, 80), attribute = at)
		self.setJob(cycle, cycleMethod)
			
	def cycleFrontLeft(self):
		self.ballCycle("cycleFrontLeft", self.cycleFrontLeft)

	def cycleFrontRight(self):
		self.ballCycle("cycleFrontRight", self.cycleFrontRight)

	def cycleBackLeft(self):
		self.ballCycle("cycleBackLeft", self.cycleBackLeft)

	def cycleBackRight(self):
		self.ballCycle("cycleBackRight", self.cycleBackRight)
	
	def executeRotate(self, left = "screen", right = "claws"):
		parts = (left, right, "head", "frontLeft", "frontRight", "backLeft", "backRight")
		rotateMethods = (lambda : self.rotateLeft(left), lambda : self.rotateRight(right), self.rotateHead, self.rotateFrontLeft, self.rotateFrontRight, self.rotateBackLeft, self.rotateBackRight)
		for i, p in enumerate(parts):
			self.setJob("{}.{}".format(self.body, p), rotateMethods[i])
	
	def executeClaws(self, claws1 = "claws", claws2 = ""):
		parts = [claws1, claws2]
		clawsMethods = [lambda : self.adjustClaws1(claws1), lambda : self.adjustClaws2(claws2)]
		if claws2 == "":
			parts.pop()
			clawsMethods.pop()
		for i, p in enumerate(parts):
			self.setJob("{}|{}.adjustClaws".format(self.robot, p), clawsMethods[i])
			
	def executeCycles(self):
		parts = ("cycleFrontLeft", "cycleFrontRight", "cycleBackLeft", "cycleBackRight")
		cycleMethods = (self.cycleFrontLeft, self.cycleFrontRight, self.cycleBackLeft, self.cycleBackRight)
		for i, p in enumerate(parts):
			self.setJob("{}.{}".format(self.robot, p), cycleMethods[i])
		
	def execute(self):
		self.setJob(self.limbs, self.adjustLimbs)
		self.executeClaws()
		self.executeRotate()
		self.executeCycles()
		if self.robot == "robot":
			self.setJob(self.emotion, self.adjustScreen)
			self.setJob(self.code, self.displayCode)
		
class Worker(Robot):
	def __init__(self, num = 0):
		Robot.__init__(self, "worker" if num < 1 else "worker{}".format(num))
		
	def executeRotate(self, left = "clawsLeft", right = "clawsRight"):
		Robot.executeRotate(self, left, right)
		
	def executeClaws(self, claws1 = "clawsLeft", claws2 = "clawsRight"):
		Robot.executeClaws(self, claws1, claws2)
		
	def adjustLimbs(self, left = "clawsLeft", right = "clawsRight"):
		Robot.adjustLimbs(self, left = left, right = right)
		
class WorkShop(Object):
	def __init__(self):
		self.h = "workshop1.hideNurbs"
		self.nurbs = cmds.ls(type = 'nurbsCurve')
		self.setJob(self.h, self.hideNurbs)
		
	def hideNurbs(self):
		for _, n in enumerate(self.nurbs):
			n = "{}.visibility".format(n)
			cmds.setAttr(n, not cmds.getAttr(n))
		self.setJob(self.h, self.hideNurbs)
		
r = Robot()
w = Worker()
ws = WorkShop()