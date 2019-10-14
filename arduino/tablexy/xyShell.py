import npyscreen
from xyMover import XYMover
import csv
import time

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
        self.port = self.add(npyscreen.TitleFilename, name="PORT     :", value="8820", editable=False)
        self.xyMover = XYMover(int(self.port.value))
        self.xpos = self.add(npyscreen.TitleText, name="X_POS       :", value="0")
        self.ypos = self.add(npyscreen.TitleText, name="Y_POS       :", value="0")

    def on_ok(self):
        (xpos,ypos)=self.xyMover.position().split(" ")
        try:
            if (int(xpos) != int(self.xpos.value) or 
                int(ypos) != int(self.ypos.value)):
                xpos=self.xpos.value
                ypos=self.ypos.value
                self.xpos.value="Moving"
                self.ypos.value="Moving"
                self.xpos.display()
                self.ypos.display()
                self.xyMover.moveAbsoluteXY(int(xpos),int(ypos))
                time.sleep(0.5)
                (xpos,ypos)=self.xyMover.position().split(" ")
                self.xpos.value=xpos
                self.ypos.value=ypos
                self.xpos.display()
                self.ypos.display()

        except ValueError as ve:
            self.xpos.value = "Please use an integer number"
            self.ypos.value = "Please use an integer number"
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
