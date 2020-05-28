import npyscreen
from xyMover import XYMover
import csv
import time
import optparse

#8820 MOTOR_0
#8821 MOTOR_1

parser = optparse.OptionParser("usage: xyShell.py --port 8820")
parser.add_option("--port", dest="myport", default=8820,
                  help="port")
(opt, args) = parser.parse_args()
print opt.myport


class App(npyscreen.StandardApp):
    def onStart(self):
        self.addForm("MAIN", XYControlPanel, name="Arduino XY Motor Control Panel")

class XYControlPanel(npyscreen.ActionForm):
    # Constructor
    def create(self):
        self.OK_BUTTON_TEXT='Apply'
        self.CANCEL_BUTTON_TEXT='Exit'
        self.__class__.CANCEL_BUTTON_BR_OFFSET = (2, 15)

        # Add the TitleText widget to the form
        self.port = self.add(npyscreen.TitleFilename, name="PORT     :", value=opt.myport, editable=True)
        self.xyMover = XYMover(int(self.port.value))
        xHome=round(float(self.xyMover.estimatedPosition().split(" ")[0]),1)
        yHome=round(float(self.xyMover.estimatedPosition().split(" ")[1]),1)
        self.xpos = self.add(npyscreen.TitleText, name="X_POS       :", value="%3.1f"%xHome, rely=4)
        self.xposSlider  = self.add(npyscreen.TitleSlider, out_of=48, name = "X_POS       :", value=xHome, editable=False)
        self.ypos = self.add(npyscreen.TitleText, name="Y_POS       :", value="%3.1f"%yHome, rely=7)
        self.yposSlider  = self.add(npyscreen.TitleSlider, out_of=48, name = "Y_POS       :", value=yHome, editable=False)


    def on_ok(self):
        (xpos,ypos)=self.xyMover.estimatedPosition().split(" ")
        try:
            if (round(float(xpos),1) != round(float(self.xpos.value),1) or 
                round(float(ypos),1) != round(float(self.ypos.value),1)):
                xpos=self.xpos.value
                ypos=self.ypos.value
                self.xpos.value="Moving"
                self.ypos.value="Moving"
                self.xpos.display()
                self.ypos.display()
                self.xyMover.moveAbsoluteXY(round(float(xpos),1),round(float(ypos),1))
                time.sleep(0.5)
                (xpos,ypos)=self.xyMover.estimatedPosition().split(" ")
                self.xpos.value=xpos
                self.ypos.value=ypos
                self.xposSlider.value=round(float(xpos),1)
                self.xpos.display()
                self.ypos.display()
                self.yposSlider.value=round(float(ypos),1)

        except ValueError as ve:
            self.xpos.value = "Invalid coordinates. Please use a float number XX.X"
            self.ypos.value = "Invalid coordinates. Please use a float number YY.Y"
            self.xpos.display()
            self.ypos.display()
        except:
            self.xpos.value = "Error moving"
            self.ypos.value = "Error moving"
            self.xpos.display()
            self.ypos.display()
            
    def while_waiting(self):
        pass

    def on_cancel(self):
        self.parentApp.setNextForm(None)



MyApp = App()
MyApp.run()
