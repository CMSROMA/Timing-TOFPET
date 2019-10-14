from xyMover import XYMover


print "++++ Testing XYMover +++++"

aMover=XYMover(8820)
aMover.moveAbsoluteXY(10,15)
myPos=aMover.position()
print ("XYMover now @"+myPos)

aMover.moveAbsoluteXY(15,15)
myPos=aMover.position()
print ("XYMover now @"+myPos)

aMover.moveRelativeX(5)
myPos=aMover.position()
print ("XYMover now @"+myPos)

aMover.moveRelativeX(-5)
myPos=aMover.position()
print ("XYMover now @"+myPos)

aMover.moveRelativeY(5)
myPos=aMover.position()
print ("XYMover now @"+myPos)

aMover.moveRelativeY(-5)
myPos=aMover.position()
print ("XYMover now @"+myPos)

aMover.moveAbsoluteXY(20,20)
myPos=aMover.position()
print ("XYMover now @"+myPos)

print "----> Going home"
aMover.home()
myPos=aMover.position()
print ("XYMover now @"+myPos)
