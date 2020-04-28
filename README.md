# Smart Home Remote Control

Application is a project for Python Classes. Allows users send messeges to MQTT broker using GUI. Two-factor authentication is implemented, and all smart-home  config is given iin *.json file.
User information is stored in MongoDB Atlas, so to run app, your access token is required.

## Running instructions
- `pip install -r requirements.txt`
- Create `.env` file in main project folder with content:

    `export CONNECTION_STRING=<your mongoDB Atlas string>`
- `python projekt.py`

---
Author: Jacek Nitychoruk
