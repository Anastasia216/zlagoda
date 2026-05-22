from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from sqlite_db import get_db_connection

app = Flask(__name__)

