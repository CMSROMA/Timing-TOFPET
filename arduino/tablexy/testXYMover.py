from xyMover import XYMover


print "++++ Testing XYMover +++++"

aMover=XYMover(8820)
aMover.moveXY(10,15)
myPos=aMover.position()
print ("XYMover now @"+myPos)

aMover.moveXY(15,15)
myPos=aMover.position()
print ("XYMover now @"+myPos)

aMover.relativeX(5)
myPos=aMover.position()
print ("XYMover now @"+myPos)

aMover.relativeX(-5)
myPos=aMover.position()
print ("XYMover now @"+myPos)

aMover.relativeY(5)
myPos=aMover.position()
print ("XYMover now @"+myPos)

aMover.relativeY(-5)
myPos=aMover.position()
print ("XYMover now @"+myPos)

print "----> Going home"
aMover.home()
myPos=aMover.position()
print ("XYMover now @"+myPos)
