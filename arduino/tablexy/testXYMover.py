from xyMover import XYMover
import time

print ("++++ Testing XYMover +++++")

aMover=XYMover(8820)
#print (aMover.estimatedPosition())

print ("++++ Moving to 20,25 +++++")
print (aMover.moveAbsoluteXY(20,25))
print (aMover.estimatedPosition())
print ("++++ Done +++++")

print ("++++ Moving 100,30 out of bounds +++++")
print (aMover.moveAbsoluteXY(100,30))
print (aMover.estimatedPosition())
print ("++++ Done +++++")


