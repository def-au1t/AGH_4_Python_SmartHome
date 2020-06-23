import tkinter as tk

from functools import partial
from tkinter import FLAT
from tkinter import ttk, PhotoImage
from PIL import Image, ImageTk
import sys, os


def configure_styles():
    """
    Tkinter styles configuration
    """
    ttk.Style().configure('deviceName.Label', font='Helvetica 13 bold', width=-30, anchor="center")
    ttk.Style().configure('roomName.Label', font='Helvetica 15 bold')
    ttk.Style().configure('deviceHeader.Label', font='Helvetica 10 bold')
    ttk.Style().configure('descriptionBold.Label', font='Helvetica 11 bold')
    ttk.Style().configure('bigText.Label', font='Helvetica 12')


class WindowsManager(object):
    """
    Class responsible for creating and modyfying views with tkinter
    """

    def __init__(self, rc):
        """
        Performs basic window configuration
        """
        self.container = None
        self.current_room = None
        self.main = rc
        self.window = tk.Tk()
        self.window.title("Smart Home Remote Control")
        self.window.configure()
        self.window.geometry("1000x600")
        self.window.resizable(False, False)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.iconphoto(True, PhotoImage(file=os.path.join(sys.path[0], "static/icon.png")))
        configure_styles()
        if self.main.logged:
            self.tk_logged()
        else:
            self.tk_start_view()

    def loop(self):
        """
        Co tu komentować... :)
        Pozdrowienia dla prowadzącego zajęcia :-D
        """
        self.window.mainloop()

    def tk_register_view(self, info=None):
        """
        Registration view
        """
        self.clean_main_window()
        container = ttk.Frame(self.window, width=950, height=550, relief=FLAT)
        container.grid()

        ttk.Label(container, text="nazwa użytkownika:", style="descriptionBold.Label").grid(pady=5)
        input_username = ttk.Entry(container)
        input_username.grid()
        ttk.Label(container, text="hasło:", style="descriptionBold.Label").grid(pady=5)
        input_password = ttk.Entry(container, show="*")
        input_password.grid()
        ttk.Label(container, text="powtórz hasło:", style="descriptionBold.Label").grid(pady=5)
        input_password2 = ttk.Entry(container, show="*")
        input_password2.grid()
        if info:
            ttk.Label(container, text=info).grid()

        button_submit = ttk.Button(container, text="Zarejestruj się",
                                   command=partial(self.main.try_register, input_username, input_password,
                                                   input_password2))
        button_submit.grid(pady=10)
        button_back = ttk.Button(container, text="Powrót", command=lambda: self.tk_start_view())
        button_back.grid()

        self.container = container

    def tk_register_code_view(self, info=None, username=None, password=None, key=None):
        """
        Registration view with QR Code.
        """
        self.clean_main_window()
        container = ttk.Frame(self.window, relief=FLAT).grid()

        ttk.Label(container, text="Zeskanuj kod QR na urządzeniu mobilnym i podaj wygenerowane hasło:",
                  style="descriptionBold.Label").grid(pady=10)
        input_code = ttk.Entry(container)
        input_code.grid(pady=5)

        if info:
            label1 = ttk.Label(container, text=info)
            label1.grid()
        button_submit = ttk.Button(container, text="Potwierdź",
                                   command=lambda: self.main.try_register_code(username, password, key, input_code))
        button_submit.grid(pady=10)
        ttk.Button(container, text="Powrót", command=lambda: self.tk_start_view()).grid()

        image = Image.open("static/qr/qr_code_" + username + ".png")
        if image.size != (300, 300):
            image = image.resize((300, 300), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)
        bg_label = tk.Label(container, image=image)
        bg_label.grid()
        bg_label.image = image

        self.container = container

    def tk_start_view(self):
        """
        Start view. Allows user to login or register
        """
        self.clean_main_window()
        container = ttk.Frame(self.window, width=950, height=550, relief=FLAT)
        container.grid()
        ttk.Label(container, text="System sterowania inteligentnym domem", style="roomName.Label") \
            .grid(row=0, column=1, columnspan=2, pady=10)

        ttk.Separator(container).grid(column=1, columnspan=2, row=1, pady=10, sticky="ew")
        ttk.Button(container, text="Zaloguj się", command=lambda: self.tk_login_view()) \
            .grid(row=2, column=1)
        ttk.Button(container, text="Zarejestruj się", command=lambda: self.tk_register_view()) \
            .grid(row=2, column=2)
        self.container = container

    def tk_login_view(self, info=None):
        """
        Login view
        """
        self.clean_main_window()
        container = ttk.Frame(self.window, relief=FLAT).grid(row=0, column=0)
        label_username = ttk.Label(container, text="nazwa użytkownika:", style="descriptionBold.Label")
        label_username.grid(row=1, column=0, pady=5)
        input_username = ttk.Entry(container)
        input_username.grid()
        label_password = ttk.Label(container, text="hasło:", style="descriptionBold.Label")
        label_password.grid(pady=5)
        input_password = ttk.Entry(container, show="*")
        input_password.grid()
        if info:
            ttk.Label(container, text=info).grid()
        ttk.Button(container, text="Zaloguj się",
                   command=lambda: self.main.try_login(input_username, input_password)).grid(pady=10)
        ttk.Button(container, text="Powrót", command=lambda: self.tk_start_view()).grid()
        self.container = container

    def tk_login_code_view(self, info=None, username=None, key=None):
        """
        2FA login view
        """
        self.clean_main_window()
        container = ttk.Frame(self.window, relief=FLAT).grid(row=0, column=0)
        label_password = ttk.Label(container, style="descriptionBold.Label",
                                   text="Weryfikacja dwuetapowa. Podaj kod z urządzenia mobilnego:")
        label_password.grid(pady=10)
        input_code = ttk.Entry(container)
        input_code.grid(pady=5)

        if info:
            label1 = ttk.Label(container, text=info)
            label1.grid(pady=5)
        button_submit = ttk.Button(container, text="Potwierdź",
                                   command=partial(self.main.try_login_code, username, key, input_code))
        button_submit.grid(pady=5)
        button_back = ttk.Button(container, text="Powrót", command=lambda: self.tk_start_view())
        button_back.grid()
        self.container = container

    def tk_logged(self):
        """
        Builds window with menu after user logs in.
        """
        self.clean_main_window()
        self.window.title("Smart Home Remote Control - " + self.main.logged)
        menu = tk.Menu(self.window)
        rooms_menu = tk.Menu(menu, tearoff=0)
        for room_id in range(len(self.main.dm.smart_objects)):
            room_name = self.main.dm.smart_objects[room_id]['name']
            rooms_menu.add_command(label=room_name, command=lambda rid=room_id: self.tk_room_view(rid))
        menu.add_command(label="Strona główna", command=lambda: self.tk_logged())
        menu.add_cascade(label="Pokoje", menu=rooms_menu)
        menu.add_command(label="Wyloguj się", command=lambda: self.main.logout())
        self.window.config(menu=menu)

        self.tk_rc_view()

    def tk_rc_view(self):
        """
        Main view after login
        """
        self.clean_main_window()
        container = ttk.Frame(self.window, width=950, height=550, relief=FLAT)
        container.grid()

        ttk.Label(container, text='Witaj, ' + self.main.logged + '!', style="roomName.Label").grid(pady=10)
        ttk.Label(container, text="Wybierz pokój z menu u góry, aby sterować urządzeniami",
                  style='bigText.Label').grid(pady=30)
        self.container = container
        image = Image.open("static/home.jpg")
        if image.size != (640, 320):
            image = image.resize((1000, 500), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)
        bg_label = tk.Label(container, image=image)
        bg_label.grid()
        bg_label.image = image

    def tk_room_view(self, room_id):
        """
        View with devices from certain room. THe most interactive part of application
        """
        self.current_room = room_id
        self.clean_main_window()
        out_container = ScrollableFrame(self.window, width=950, height=550, relief=FLAT)
        out_container.grid(column=0, row=0)
        container = out_container.get_scrollable_frame()
        room = self.main.dm.smart_objects[room_id]
        assert room
        ttk.Label(container, text=room['name'], style='roomName.Label').grid(column=0, pady=10, sticky="")

        controls_device = dict()

        for device_id in range(len(room['devices'])):
            device_container = tk.Frame(container, width=950, height=550)
            device_container.grid(column=0, row=2 * device_id + 2)

            controls_device[device_id] = dict()
            device = room['devices'][device_id]
            ttk.Label(device_container, text=device['name'], style='deviceName.Label').grid(column=0, row=0,
                                                                                            pady=5)
            right_row = 0
            if 'status' in device['settings']:
                controls_device[device_id]['button_submit'] = None
                controls_device[device_id]['button_submit'] = \
                    ttk.Button(device_container,
                               text=device['settings']['status'],
                               command=lambda dev_id=device_id, r_id=room_id:
                               self.main.dm.switch_device(
                                   dev_id, r_id, controls_device[dev_id]['button_submit']))
                controls_device[device_id]['button_submit'].grid(column=0, row=1, pady=5)

            if 'power_max' in device['settings']:
                ttk.Label(device_container, text="Moc:", style='deviceHeader.Label').grid(column=1,
                                                                                          row=right_row)
                right_row += 1
                max_power = device['settings']['power_max']
                if max_power < 100:
                    interval = 1
                else:
                    interval = max_power / 100
                if not ('power' in device['settings']):
                    initial = 0
                else:
                    initial = device['settings']['power']
                slider = tk.Scale(device_container, from_=0, to=max_power, orient=tk.HORIZONTAL, length=300,
                                  resolution=interval,
                                  command=partial(self.main.dm.device_change_power, device_id, room_id))
                slider.set(initial)

                slider.grid(column=1, row=right_row)

                right_row += 1

            if 'props' in device['settings']:
                ttk.Label(device_container, text="Opcje:", style='deviceHeader.Label').grid(column=1, row=right_row)
                right_row += 1
                props = device['settings']['props']
                if 'prop' in device['settings']:
                    current = device['settings']['prop']
                    if len(props) <= int(current):
                        print("zeruję wartość opcji inteligentnego obiektu")
                        current = 0
                else:
                    current = 0

                ttk.OptionMenu(device_container, tk.StringVar(), props[current], *props,
                               command=partial(self.main.dm.device_change_prop, device_id, room_id)) \
                    .grid(column=1, row=right_row)

                right_row += 1
            if not 'power_max' in device['settings']:
                placeholder = ttk.Label(device_container, text="\t", style='deviceHeader.Label')
                placeholder.config(width=44)
                placeholder.grid(column=1, row=right_row)

            ttk.Separator(container).grid(column=0, row=2 * device_id + 3, pady=5, sticky="ew")

        self.container = container

    def clean_main_window(self):
        for widget in self.window.winfo_children():
            if widget.winfo_class() != 'Menu':
                widget.destroy()


class ScrollableFrame(ttk.Frame):
    """
    Supporting class to provide frame with scrollbar
    """

    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, width=980, height=580, relief=FLAT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, width=950, height=300, relief=FLAT)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.frame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="n")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.grid(row=0, column=0)

        self.canvas.grid_columnconfigure(1, weight=1)
        scrollbar.grid(row=0, column=1, sticky="ns")

    def get_scrollable_frame(self):
        return self.scrollable_frame
