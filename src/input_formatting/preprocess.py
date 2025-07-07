import os

import pandas as pd


def update_lectures_csv(lectures_csv_path, toml):
    suffix = ""
    if os.path.exists(lectures_csv_path):
        suffix = ".bak"
        os.rename(lectures_csv_path, lectures_csv_path + suffix)

    encoding = toml["params"]["csv_encoding"]
    df = pd.read_csv(lectures_csv_path + suffix, encoding=encoding)

    df.to_csv(lectures_csv_path, encoding=encoding, index=False, header=True)


def update_students_csv(students_csv_path, toml):
    suffix = ""
    if os.path.exists(students_csv_path):
        suffix = ".bak"
        os.rename(students_csv_path, students_csv_path + suffix)

    encoding = toml["params"]["csv_encoding"]
    df = pd.read_csv(students_csv_path + suffix, encoding=encoding)

    # 上書き再履修が1の行を削除
    df = df[df["上書き再履修"] != 1]

    df.to_csv(students_csv_path, encoding=encoding, index=False, header=True)
