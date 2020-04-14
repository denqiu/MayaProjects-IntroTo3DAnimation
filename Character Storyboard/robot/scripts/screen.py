class RobotPart:
    def __init__(self, name, shape):
        self.name = name
        self.shape = shape
        self.minimum()
        self.move()
        self.con = []
        print(self.toString())
        
    def translate(self, x = 0, y = 0, z = 0):
        self.translateX = x
        self.translateY = y
        self.translateZ = z
        print("Translate: x = {}, y = {}, z = {}".format(x, y, z))
        
    def rotate(self, x = 0, y = 0, z = 0):
        self.rotateX = x
        self.rotateY = y
        self.rotateZ = z
        print("Rotate: x = {}, y = {}, z = {}".format(x, y, z))

    def minimum(self, x = 0, y = 0, z = 0):
        self.minX = x
        self.minY = y
        self.minZ = z
        print("Minimum: x = {}, y = {}, z = {}".format(x, y, z))

    def move(self, t = 0, rx = 0, ry = 0, rz = 0):
        print("Degree =", t)
        self.translate(self.minX+t, self.minY+t, self.minZ+t)
        self.rotate(rx, ry, rz)
        
    def toString(self):
        return "Part: name = {}, shape = {}".format(self.name, self.shape)
        
    def connect(self, robotPart, x = 0, y = 0, z = 0, isConnect = True):
        if isConnect:
            self.con.append((robotPart, x, y, z))
        else:
            self.con = [p for p in self.con if robotPart != p[0]]
        print(self.toString(), "->", tuple(r[0].toString() for r in self.con))
        
    def getPart(self, part):
        return [p[0] for p in self.connect if p[0].name == part][0]
        
class Robot:
    def __init__(self, robotBuild = "robot", left = "screen", right = "claws"):
        self.build = robotBuild
        self.head = RobotPart("head", "football")
        self.body = RobotPart("body", "top")
        limb = self.createLimb()
        self.frontLeft = limb
        self.frontLeft.minimum(0.176, -0.096, -0.223)
        self.frontLeft.move(t = 0.115, rx = 15, rz = 90)
        self.frontRight = limb
        self.frontRight.minimum(0.223, -0.096, 0.176)
        self.frontRight.move(t = 0.115, rx = -15, rz = 90)
        self.backLeft = limb
        self.backLeft.minimum(-0.223, -0.096, 0.223)
        self.backLeft.move(t = 0.115, rx = 195, rz = 90)
        self.backRight = limb
        self.backRight.minimum(-0.176, -0.096, -0.176)
        self.backRight.move(t = 0.115, rx = 165, rz = 90)
        if robotBuild == "robot":
            self.leftArm = limb
            self.leftArm.connect(RobotPart("joint2", "smallCylinder"))
            self.leftArm.connect(RobotPart(left, "computerScreen"))
        elif robotBuild == "worker":
            self.leftArm = self.createClaw(left, limb)
        self.rightArm = self.createClaw(right, limb)
        self.translate()
                
    def translate(self, x = 0, y = 0, z = 0):
        self.translateX = x
        self.translateY = y
        self.translateZ = z
        print("Translate: x = {}, y = {}, z = {}".format(x, y, z))
        
    def connectHead(self, isConnect = True):
        self.body.connect(self.head, y = 0.78, isConnect = isConnect)
        
    def connectLeftArm(self, isConnect = True):
        self.body.connect(self.leftArm, y = 0.484, z = -0.74, isConnect = isConnect)

    def connectRightArm(self, isConnect = True):
        self.body.connect(self.rightArm, y = 0.484, z = 0.74, isConnect = isConnect)
        
    def connectFrontLeft(self, isConnect = True):
        self.body.connect(self.frontLeft, isConnect = isConnect)

    def connectFrontRight(self, isConnect = True):
        self.body.connect(self.frontRight, isConnect = isConnect)

    def connectBackLeft(self, isConnect = True):
        self.body.connect(self.backLeft, isConnect = isConnect)

    def connectBackRight(self, isConnect = True):
        self.body.connect(self.backRight, isConnect = isConnect)

    def createLimb(self):
        ball2 = RobotPart("ball2", "sphere")
        joint1 = RobotPart("joint1", "cylinder")
        joint1.connect(ball2)
        ball1 = RobotPart("ball1", "sphere")
        ball1.connect(joint1, z = -90)
        ball = RobotPart("ball", "sphere")
        joint = RobotPart("joint", "cylinder")
        joint.connect(ball1)
        ball.connect(joint)
        return ball
    
    def createClaw(self, name, limb):
        limb.connect(RobotPart(name, "claw"))
        return limb
    
    def test(self, worker):
        worker.testing()
    
class Worker(Robot):
    def __init__(self):
        Robot.__init__(self, "worker", "clawsLeft", "clawsRight")
        
    def testing(self):
        print("Testing worker...")
        
r = Robot()
w = Worker()
r.test(w)