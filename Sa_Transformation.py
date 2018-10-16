from PyQt5.QtWidgets import *

import sys
import numpy as np
import logging

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

class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)



class Window(QWidget):
    def __init__(self,parent=None):
        super(Window, self).__init__(parent)
        #QWidget.__init__(self)
        self.title = "Transformation Matrix"
        self.fileName_ = ""
        self.matrixA=[]
        self.matrixB=[]
        self.wizard = QWizard(self)

        #self.init_ui()


    #def init_ui(self):
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


        logTextBox = QTextEditLogger(self)
        # You can format what is printed to text box
        # logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.DEBUG)

        self._button = QPushButton()
        self._button.setText('Transformation Report_ ')

        #layout = QVBoxLayout()
        # Add the new logging box widget to the layout
        layout.addWidget(logTextBox.widget,1,1)
        layout.addWidget(self._button,1,0)
        #self.setLayout(layout)

        # Connect signal to slot
        self._button.clicked.connect(self.Transformation)


        self.show()

    def Transformation(self):
        transfo = RigiTransformation3D(self.matrixA, self.matrixB)
        R, T = transfo.rigid_transform_3D()

        T = T.reshape((3, 1))
        R = R.reshape((3, 3))

        Hom_coord = np.array([0, 0, 0, 1])
        Hom_coord = Hom_coord.reshape((1, 4))
        Transformation = np.concatenate((np.concatenate((R, T), axis=1), Hom_coord), axis=0)

        logging.debug("Transformation_Matrix=\n")
        np.savetxt('log.txt', Transformation)
        with open('log.txt') as f:
            for line in f:
                logging.debug(line)
        f.close()

        n = np.shape(self.matrixA)[0]
        Homm_coord_to_matrixA = np.ones((n, 1))
        MatrixA_Homm = np.concatenate((self.matrixA, Homm_coord_to_matrixA), axis=1)
        To_align_Matrix_estim = np.dot(Transformation, np.transpose(MatrixA_Homm))
        To_align_Matrix_estim = To_align_Matrix_estim.T
        To_align_Matrix_estim = np.delete(To_align_Matrix_estim, (3), axis=1)
        logging.debug("To_align_Matrix_estim=\n")
        np.savetxt('log.txt', To_align_Matrix_estim)
        with open('log.txt') as f:
            for line in f :
                logging.debug(line)
        f.close()

        err = To_align_Matrix_estim - self.matrixB

        resi = err
        # print(resi)
        err = np.multiply(err, err)
        err = np.sum(err)
        rmse = np.sqrt(err / n)
        rmse = rmse*1000 # en mm

        logging.debug("RMSE=" + str(rmse)+" mm")













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
                transfo = RigiTransformation3D(self.matrixA, self.matrixB)
                R, T = transfo.rigid_transform_3D()

                T=T.reshape((3,1))
                R=R.reshape((3,3))

                Hom_coord = np.array([0, 0, 0, 1])
                Hom_coord = Hom_coord.reshape((1, 4))
                Transformation = np.concatenate((np.concatenate((R, T), axis=1),Hom_coord),axis=0)

                print("Transformation_Matrix=\n",Transformation)

                n= np.shape(self.matrixA)[0]
                Homm_coord_to_matrixA = np.ones((n, 1))
                MatrixA_Homm = np.concatenate((self.matrixA, Homm_coord_to_matrixA), axis=1)
                To_align_Matrix_estim = np.dot(Transformation, np.transpose(MatrixA_Homm))
                To_align_Matrix_estim =To_align_Matrix_estim.T
                To_align_Matrix_estim = np.delete(To_align_Matrix_estim,(3),axis=1)
                print("To_align_Matrix_estim=\n",To_align_Matrix_estim)


                err = To_align_Matrix_estim - self.matrixB

                resi = err
                # print(resi)
                err = np.multiply(err, err)
                err = np.sum(err)
                rmse = np.sqrt(err / n)

                print("RMSE=",rmse*1000," mm")





def main():
    app = QApplication(sys.argv)
    screen = Window()
    sys.exit(app.exec_())



if __name__ == '__main__':
    main()



