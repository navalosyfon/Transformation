from PyQt5.QtWidgets import *
import sys
import numpy as np
import pandas as pd



class RigiTransformation3D:

    def __init__(self,A,B):
        self.A = A
        self.B = B

    def rigid_transform_3D(self):


        assert len(self.A) == len(self.B)


        N = self.A.shape[0]  # total points

        centroid_A = np.mean(self.A, axis=0)
        centroid_B = np.mean(self.B, axis=0)

                   # centre the points
        AA = self.A - np.tile(centroid_A, (N, 1))
        BB = self.B - np.tile(centroid_B, (N, 1))

        H = np.dot(np.transpose(AA),BB)

        U, S, Vt = np.linalg.svd(H)

        R = np.dot(Vt.T, U.T)

        # special reflection case
        if np.linalg.det(R) < 0:
            print("Reflection detected")
            Vt[2, :] *= -1
            R = np.dot(Vt.T * U.T)

        t = -np.dot(R,centroid_A.T) + centroid_B.T

        return (R, t)

class ReadFile:

    #===========================Loading Data========================================#
    def __init__(self):
        self.A_file_path = ""


    def dataset(self):


        line_number_ =0
        # The transormation matrix will takes point from A system to B system
        data_file_A = self.A_file_path  # "CloudPoints System A.txt"

        #data_file_B = self.B_file_path     #"CloudPoints System B.txt"

        with open(data_file_A) as f:
            for line in f :
                line_number_=line_number_+1


        f.close()

                #A.append(float(line[0:9]))
        A= np.zeros((line_number_,3))
        line_number=0
        with open(data_file_A,encoding="utf-8") as fff:
            for line in fff:
                x,y,z= line.split()
                A[line_number,0]= float(x)
                A[line_number, 1] =float(y)
                A[line_number, 2] = float(z)
                line_number = line_number + 1
        fff.close()

        return (A)

class Page2(QWizardPage):
    def __init__(self,parent=None):
        QWizardPage.__init__(self)
        super(Page2, self).__init__(parent)
        """
        layout = QGridLayout()
        self.setLayout(layout)
        self.lineedit = QLineEdit()
        
        layout.addWidget(self.lineedit, 0, 0)
        """
        self.label1 = QLabel()
        self.Le = QLineEdit()

        layout = QHBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.Le)

        self.label1.setText("Path of points")

        self.setLayout(layout)

class Window(QWidget):
    def __init__(self,parent=None):
        super(Window, self).__init__(parent)
        #QWidget.__init__(self)
        self.title = "Transformation Matrix"
        self.fileName_ = ""
        self.matrixA=[]
        self.matrixB=[]
        self.wizard = QWizard(self)

        self.init_ui()


    def init_ui(self):
        self.setWindowTitle(self.title)

        layout = QGridLayout()
        self.setLayout(layout)
        radiobutton = QRadioButton("To align Points")
        #radiobutton.setChecked(True)
        radiobutton.country = "To align Points"
        radiobutton.toggled.connect(self.on_radio_button_toggled)
        layout.addWidget(radiobutton, 0, 0)

        radiobutton = QRadioButton("Reference Points")
        radiobutton.country = "Reference Points"
        radiobutton.toggled.connect(self.on_radio_button_toggled)
        layout.addWidget(radiobutton, 0, 1)

        # self.lineedit = QLineEdit()
        # self.lineedit.returnPressed.connect(self.return_pressed)
        # layout.addWidget(self.lineedit, 1, 0)


        radiobutton = QRadioButton("Transformation Report ")
        radiobutton.country = "Transformation Report"
        radiobutton.toggled.connect(self.on_radio_button_toggled)
        layout.addWidget(radiobutton, 0, 2)

        self.show()


    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                      "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            self.fileName_ = fileName

    def on_radio_button_toggled(self):
        sender = self.sender()
        #page = Page2(self)
        matrix_read = ReadFile()
        messagebox = QMessageBox()

        if sender.isChecked():
            if (sender.country == "To align Points"):
                print("Selected selector is %s" % (sender.country))
                self.openFileNameDialog()

                matrix_read.A_file_path= self.fileName_
                self.matrixA = matrix_read.dataset()
                print("matrixA=\n", self.matrixA)

                txt = ""
                for line in self.matrixA:
                    txt = txt + "\n" + str(line)

                messagebox.setWindowTitle("To align points")
                messagebox.setInformativeText("To align points")
                messagebox.setIcon(QMessageBox.Information)
                messagebox.setText(txt)
                messagebox.setStandardButtons(QMessageBox.Close)
                messagebox.exec_()


            if (sender.country == "Reference Points"):
                print("Selected selector is %s" % (sender.country))
                self.openFileNameDialog()

                matrix_read.A_file_path = self.fileName_
                self.matrixB = matrix_read.dataset()
                print("matrixB=\n", self.matrixB)
                txt=""
                for line in self.matrixB:
                    txt= txt+"\n" +str(line)

                messagebox.setWindowTitle("Reference points")
                messagebox.setInformativeText("Reference points")
                messagebox.setIcon(QMessageBox.Information)
                messagebox.setText(txt)
                messagebox.setStandardButtons(QMessageBox.Close)
                messagebox.exec_()

            if sender.country == "Transformation Report":
                transfo = RigiTransformation3D(self.matrixA, self.matrixA)
                R, T = transfo.rigid_transform_3D()

                T=T.reshape((1,3))
                R=R.reshape((3,3))
                Transformation = np.zeros((4, 4))
                Hom_coord= np.array([0,0,0,1])
                Hom_coord= Hom_coord.reshape((4,1))

                Transformation = np.concatenate((np.concatenate((R, T), axis=0),Hom_coord),axis=1)

                print("Transformation_Matrix=\n",Transformation)


def main():
    app = QApplication(sys.argv)
    screen = Window()
    sys.exit(app.exec_())



if __name__ == '__main__':
    main()



