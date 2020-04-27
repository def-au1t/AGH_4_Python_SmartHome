from functools import partial
import tkinter as tk
from tkinter import ttk, Frame, Label
from tkinter import Tk, RIGHT, BOTH, RAISED, FLAT


class WindowsManager(object):

    def __init__(self, rc):
        self.container = None
        self.main = rc
        self.window = tk.Tk()
        self.window.title("Smart Home Remote Control")
        self.window.configure()
        self.window.geometry("1000x600")
        self.window.resizable(False, False)
        self.tk_start_view()

    def loop(self):
        self.window.mainloop()

    def tk_register_view(self, container=None):
        if not container:
            container = self.container
        pass


    def tk_start_view(self):
        container = ttk.Frame(self.window, width=950, height=550, relief=FLAT)
        container.pack()
        label1 = ttk.Label(container, text="System sterowania inteligentnym domem")
        # label1.configure(background="#000FFF")
        label1.pack(side='top')
        button_login = ttk.Button(container, text="Zaloguj się", command=partial(self.tk_login_view, self.container))
        # button_login.configure(bg="#000FFF")
        button_login.pack(side='top')
        button_register = ttk.Button(container, text="Zarejestruj się", command=partial(self.tk_register_view, self.container))
        # button_register.configure(background="#000FFF")
        button_register.pack(side='bottom')
        self.container = container

    def tk_login_view(self, container=None, info=None):
        if not container:
            container = self.container
        self.container.pack_forget()
        container.pack_forget()
        container = ttk.Frame(self.window, width=950, height=550, relief=FLAT)
        container.pack()
        input_username = ttk.Entry(container)
        input_username.pack()
        input_password = ttk.Entry(container)
        input_password.pack()
        if info:
            label1 = ttk.Label(container, text=info)
            # label1.configure(background="#000FFF")
            label1.pack(side='top')
        button_submit = ttk.Button(container, text="Zaloguj się",
                                   command=partial(self.main.try_login, input_username.get(), input_password.get()))
        button_submit.pack()
        self.container = container
