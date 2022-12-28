import pickle
from pathlib import Path

import streamlit_authenticator as stauth

names = ["pupuk indonesia", "data science"]
usernames = ["ppuk2022", "ds2022"]
passwords = ["desember1", "desember2"]

hashed_passwords = stauth.Hasher(passwords).generate()

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)