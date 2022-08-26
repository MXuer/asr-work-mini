from QCandyUi.CandyWindow import colorful

@colorful('blueDeep')

class MainWindow(QMainWindow, Ui_MainWindow):


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
