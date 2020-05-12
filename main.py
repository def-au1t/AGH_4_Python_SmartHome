import bcrypt as bcrypt
import pyotp
import qrcode

from dotenv import load_dotenv

from db_manager import *
from devices_manager import *
from mqtt_manager import *
from views_manager import *


class Main(object):
    """
    Main application class responsible for application logic.
    """

    def __init__(self):
        """
        Creates components responsible for application parts
        """

        # Replace with some name, to avoid need to login to app:
        self.logged = None

        load_dotenv()

        self.dm = DevicesManager(self)
        self.dbm = DBManager(self)
        self.mqttm = MqttManager(self)
        self.wm = WindowsManager(self)

        self.wm.loop()

    def try_login(self, username, password):
        """
        Tries to login with username and password.
        If user exists and password matches, 2FA-login view is launched.
        Otherwise, error information is provided to user
        """
        username = username.get()
        password = password.get()
        if not self.dbm.is_connected():
            print("Nie udało się połączyć z bazą danych")
            return
        user = self.dbm.find_user(username)
        if not user:
            print("Nie znaleziono użytkownika w bazie!")
            self.wm.tk_login_view(info="Nieprawidłowa nazwa użytkownika")
        elif bcrypt.checkpw(password.encode('utf-8'), user['password']):
            self.wm.tk_login_code_view(username=username, key=user['otp_key'])
        else:
            self.wm.tk_login_view(info="Nieprawidłowe hasło")

    def try_login_code(self, username, key, input_code):
        """
        Tries to complete login with 2FA code.
        If it matches, "remote control welcome" view is launched.
        Otherwise, error information is provided to user
        """
        input_code = input_code.get()
        if not self.dbm.is_connected():
            print("Nie udało się połączyć z bazą danych")
            return
        current_key = pyotp.TOTP(key).now()
        if input_code == current_key:
            self.logged = username
            self.wm.tk_logged()
        else:
            self.wm.tk_login_code_view(username=username, key=key, info="Niepoprawny kod")

    def logout(self):
        """
        Logs out user.
        Returns to start view.
        """
        self.logged = None
        self.wm.window.destroy()
        self.wm = WindowsManager(self)

    def try_register(self, username, password, password2):
        """
        Tries to register with username and password.
        If user exists and password matches all conditions, 2FA-register view is launched
        and QR Code is generated and saved into ./static/qr/
        Otherwise, error information is provided to user.
        """
        username = username.get()
        password = password.get()
        password2 = password2.get()
        if not self.dbm.is_connected():
            print("Nie udało się połączyć z bazą danych")
            self.wm.tk_register_view(info="Nie udało się połączyć z bazą!")
            return
        if len(username) < 3:
            print("Nazwa użytkownika jest zbyt krótka!")
            self.wm.tk_register_view(info="Nazwa użytkownika jest zbyt krótka!")
            return
        if len(password) < 3:
            print("Hasło jest zbyt krótkie!")
            self.wm.tk_register_view(info="Hasło jest zbyt krótkie!")
            return
        if password != password2:
            print("Hasła nie pasują do siebie!")
            self.wm.tk_register_view(info="Hasła do siebie nie pasują!")
            return
        user = self.dbm.find_user(username)
        if user:
            print("Użytkownik już istnieje w bazie!")
            self.wm.tk_register_view(info="Nazwa użytkownika już istnieje!")
            return

        random_key = pyotp.random_base32()
        qr_string = pyotp.totp.TOTP(random_key).provisioning_uri(username, issuer_name="Smart Home Remote Control")
        qrcode.make(qr_string).save("static/qr/qr_code_" + username + ".png")

        self.wm.tk_register_code_view(username=username, password=password, key=random_key)

    def try_register_code(self, username, password, key, code):
        """
        Tries to complete registration 2FA-code.
        If it matches, user is created and save into database and login view is launched.
        Otherwise, error information is provided to user.
        """
        code = code.get()
        if not self.dbm.is_connected():
            print("Nie udało się połączyć z bazą danych")
            self.wm.tk_register_code_view(username=username, password=password, key=key)
            return

        if pyotp.TOTP(key).now() != code:
            print("Błędny kod 2FA")
            self.wm.tk_register_code_view(username=username, password=password, key=key, info="Błędny kod!")
            return

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        new_user = {"username": username,
                    "password": password_hash,
                    "otp_key": key}
        self.dbm.register(new_user)

        self.wm.tk_login_view(info="Zarejestrowano pomyślnie! Zaloguj się!")


if __name__ == '__main__':
    main = Main()
