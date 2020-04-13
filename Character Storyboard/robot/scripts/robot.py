from maya import cmds

class Robot:
	def __init__(self, robot = "robot"):
		self.robot = robot
		self.body = "{}|parentBody".format(robot)
		self.limbs = "{}.adjustLimbs".format(robot)
		self.execute()
		
	def isChildOfBody(self, name, m):
		for _, child in enumerate(m):
			if name in child:
				return True
		return False
	
	def rotateParts(self, part, rotatePart):
		m = cmds.listRelatives(self.body, children = True)
		s = cmds.getAttr("{}.{}".format(self.body, part))
		if s and not self.isChildOfBody(part, m):
			cmds.parent("{}|{}".format(self.robot, part), self.body)
		elif not s and self.isChildOfBody(part, m):
			cmds.parent("{}|{}".format(self.body, part), self.robot)
		cmds.select(self.body)
		self.setJob("{}.{}".format(self.body, part), rotatePart)
		
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

	def adjustClaws(self, part):	
		n = cmds.getAttr("{}|{}.adjustClaws".format(self.robot, part))
		claws = [("Left", "Z", 90-n), ("Right", "Z", 90+n), ("Top", "Y", n), ("Bottom", "Y", -n)]
		claws = tuple(claw for claw in claws if cmds.getAttr("{}.claw{}".format(part, claw[0])))
		for _, claw in enumerate(claws):
			name, r, d = claw
			cmds.setAttr("{}|ballParent1|ballParent2|parentClaw{}.rotate{}".format(part, name, r), d)
		self.setJob("{}|{}.adjustClaws".format(self.robot, part), lambda : self.adjustClaws(part))

	def adjustLimbs(self, maximum = 0.58):
		def slope(sx, sy, ex, ey):
			ex = -ex if sx < 0 else ex
			y = abs(ey-sy)
			x = abs(ex-sx)
			return y/x if x > 0 else y
			
		n = cmds.getAttr(self.limbs)
		limbs = [("claws", "arm", -n+0.74+0.118, -n+0.484, slope(-n+0.74+0.118, -n+0.484, 0.278, -0.096)), ("screen", "arm", n-0.74-0.118, -n+0.484, slope(n-0.74-0.118, -n+0.484, 0, -0.096)), ("frontLeft", "leg", n+0.176, n-0.096, slope(0.176, -0.096, 0.727, 0.385)), ("frontRight", "leg", n+0.223, n-0.096, slope(0.223, -0.096, 0.727, 0.385)), ("backLeft", "leg", -n-0.223, n-0.096, slope(-0.223, -0.096, 0.727, 0.385)), ("backRight", "leg", -n-0.176, n-0.096, slope(-0.176, -0.096, 0.727, 0.385))]
		limbs = tuple(limb for limb in limbs if cmds.getAttr("robot.{}".format(limb[0])))
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
				cmds.setAttr("{}.translate{}".format(name, t), d)
		self.setJob(self.limbs, self.adjustLimbs)

	def setJob(self, attribute, method):
		cmds.scriptJob(runOnce = True, attributeChange = [attribute, method])

	def executeRotate(self, left = "screen", right = "claws"):
		parts = (left, right, "head", "frontLeft", "frontRight", "backLeft", "backRight")
		rotateMethods = (lambda : self.rotateLeft(left), lambda : self.rotateRight(right), self.rotateHead, self.rotateFrontLeft, self.rotateFrontRight, self.rotateBackLeft, self.rotateBackRight)
		for i, p in enumerate(parts):
			self.setJob("{}.{}".format(self.body, p), rotateMethods[i])
	
	def executeClaws(self, claws1 = "claws", claws2 = ""):
		claws = tuple(c for c in (claws1, claws2) if c != "")
		for _, c in enumerate(claws):
			self.setJob("{}|{}.adjustClaws".format(self.robot, c), lambda : self.adjustClaws(c))
			
	def execute(self):
		self.setJob(self.limbs, self.adjustLimbs)
		self.executeClaws()
		self.executeRotate()
		
class Worker(Robot):
	def __init__(self, num = 0):
		Robot.__init__(self, "worker" if num < 1 else "worker{}".format(num))
		
	def executeRotate(self, left = "clawsLeft", right = "clawsRight"):
		Robot.executeRotate(self, left, right)
		
	def executeClaws(self, claws1 = "clawsLeft", claws2 = "clawsRight"):
		Robot.executeClaws(self, claws1, claws2)
		
r = Robot()
#w = Worker()