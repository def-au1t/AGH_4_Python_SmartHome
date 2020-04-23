from functools import partial
import tkinter as tk
from tkinter import ttk, Frame, Label
from tkinter import Tk, RIGHT, BOTH, RAISED


def tk_login_view(args):
    pass


def tk_register_view(args):
    pass


def tk_start_view(window):
    container = tk.Frame(window, width=950, height=550, relief=RAISED)
    container.pack()
    label1 = ttk.Label(container, text="System sterowania inteligentnym domem")
    # label1.configure(background="#000FFF")
    label1.pack(side='top')
    button_login = ttk.Button(container, text="Zaloguj się", command=partial(tk_login_view, window))
    # button_login.configure(bg="#000FFF")
    button_login.pack(side='top')
    button_register = ttk.Button(container, text="Zarejestruj się", command=partial(tk_register_view, window))
    # button_register.configure(background="#000FFF")
    button_register.pack(side='bottom')
