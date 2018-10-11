import sys
from  PyQt5 import QtWidgets
import numpy as np

class Window( QtWidgets.QWidget):

    def __init__(self):
        # the constructer of parent class which is Qtwidget
        super().__init__()

        # create a function to initialize our User Interface
        self.init_ui()
        self.matrixA = []
        self.matrixB = []
    # We make the fuction
    def init_ui(self):
        self.BClear = QtWidgets.QPushButton("Clear")
        self.BReadfile = QtWidgets.QPushButton("Transformation report ")
        self.Amatrix = QtWidgets.QPushButton("Load A matrix")
        self.Bmatrix = QtWidgets.QPushButton("Load B matrix")
        self.L = QtWidgets.QLabel ("Button not pushed yet ")
        # line edit
        self.Le = QtWidgets.QLineEdit()

         # We set a layout (Configuration,dispostion)
            ### Horizontal : box near box

        h_box = QtWidgets.QHBoxLayout()

        h_box.addWidget(self.Amatrix)
        h_box.addWidget(self.Bmatrix)

        ### Vertical Box benaeth box
        v_box = QtWidgets.QVBoxLayout()

        v_box.addWidget(self.Le)
        v_box.addLayout(h_box)
        v_box.addWidget(self.BReadfile)
        v_box.addWidget(self.BClear)
        v_box.addWidget(self.L)

        #Create the v_box layout
        self.setLayout(v_box)

            ###Note our class is Qwidget sowe can set a title
        self.setWindowTitle("Exemple of Window")
        #self.setGeometry(100,100,700,700)

            # We create a cooncetion between the signal the click and the slot between the parenteses

        self.BClear.clicked.connect(self.Button_click)
        self.BReadfile.clicked.connect(self.Button_click)
        self.Amatrix.clicked.connect(self.Button_click)
        self.Bmatrix.clicked.connect(self.Button_click)

        self.show()
        return

    def Button_click(self):

        # find wich button clicked
        sender = self.sender()
        matrix_read = ReadFile()


        if sender.text() == "Load A matrix":
            self.L.setText("Load A matrix button clicked")
            matrix_read.A_file_path = self.Le.text()
            self.matrixA =matrix_read.dataset()
            print("matrixA=\n",self.matrixA)


        if sender.text() == "Load B matrix":
            self.L.setText("Load B matrix button clicked")
            matrix_read.A_file_path = self.Le.text()
            self.matrixB = matrix_read.dataset()
            print("matrixB=\n", self.matrixB)

        if sender.text() == "Transformation report ":
            self.L.setText("Transformation report clicked ")
            print("Transformation Report Clicked")

            transfo = RigiTransformation3D(self.matrixA,self.matrixA)

            R,T= transfo.rigid_transform_3D()
            print("R=\n",R)
            print("T=\n",T)

        if sender.text() == "Clear":
            self.L.setText("Clear button clicked")
            self.Le.clear()
        return



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


class RigiTransformation3D:

    def __init__(self,A,B):
        self.A = A
        self.B = B

    def rigid_transform_3D(self):
        print("Hello)")

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


def Window_():
    # define argument for my applicaion
    my_app=QtWidgets.QApplication(sys.argv)
    # Create our first widget
    w= QtWidgets.QWidget()
    B= QtWidgets.QPushButton(w)
    L=QtWidgets.QLabel(w)

    B.setText("Push the button")
    L.setText("Look at the results")
    w.setWindowTitle("Testing this application")

    B.move(10,10)
    L.move(10,100)
    w.setGeometry(100,100,900,700)
    # show the widget
    w.show()

    # infinite loop to see the window
    sys.exit(my_app.exec())



def main():

    systemA_file_path = "System A_.txt"
    systemB_file_path = "System B_.txt"

    files = ReadFile()
    files.A_file_path = systemA_file_path
    A = files.dataset()
    files.A_file_path = systemB_file_path
    B = files.dataset()


    # Window_()
    transfo = RigiTransformation3D(A, B)
    print(transfo.rigid_transform_3D())

    return

if __name__ == '__main__':
    #main()


        ## To run the class we should create the application loop
    app =QtWidgets.QApplication(sys.argv)
        # create an instance of our class
    a_window = Window()
        # set the application loop running
    sys.exit(app.exec_())








