import configparser
import json
import re, os
from telethon.errors import SessionPasswordNeededError
from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import (GetHistoryRequest)
import test
from PIL import Image
import pytesseract
import numpy as np
from flask import Flask
from models import db, MainTable


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from telethon.tl.types import (
PeerChannel
)

api_id = 22763147
api_hash = '5495b2e1a56e108aa36e7f0cf50d6bc7'