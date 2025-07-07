import pandas as pd


def read_lectures_csv(lectures_csv_path, encoding):
    df = pd.read_csv(lectures_csv_path, encoding=encoding, dtype=str, header=0)

    #### PROCESSING BELOW ####
    # "講義コード"と"履修年度"をconcatenateして"講義コード"を上書き更新
    df["講義コード"] = df["講義コード"].astype(str) + "-" + df["履修年度"].astype(str)
    #### PROCESSING ABOVE ####

    return df


def read_students_csv(students_csv_path, encoding):
    df = pd.read_csv(students_csv_path, encoding=encoding, dtype=str, header=0)

    #### PROCESSING BELOW ####
    # 上書き再履修が1の行を削除
    if "上書き再履修" in df.columns:
        df = df[df["上書き再履修"] != 1]

    # "履修年度"と"履修学期"でフィルタリング
    if "履修年度" in df.columns and "履修学期" in df.columns:
        season_map_dict = {
            "1": ["春学期"],
            "2": ["夏学期", "前期", "前期集中"],
            "3": ["秋学期"],
            "4": ["冬学期", "後期", "後期集中", "通期集中"],
        }
        season_sr = df["履修学期"].map(
            {v: k for k, vs in season_map_dict.items() for v in vs}
        )
        # nanを想定した整数型に変換
        df["year"] = df["履修年度"].astype(str) + season_sr
        df = df[df["year"].astype("Int64") <= 20243]
    #### PROCESSING ABOVE ####

    return df
