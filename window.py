import tkinter as tk

class Window:
    def __init__(self):
        self.connection_window = tk.Tk()
        self.connection_window.title("Shalom Friend!")

        self.ranges_window = tk.Tk()
        self.ranges_window.withdraw()
        self.ranges_window.title("MD5, RUSH!")

    def connection(self):
        self.connection_window.mainloop()
        self.connection_window.quit()
        ...









        #window.deiconify()

if __name__ == "__main__":
    w = Window()
    w.connection()