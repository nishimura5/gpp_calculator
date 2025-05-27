import os
import tomllib

import pandas as pd

import lectures


def test_case_1(seed):
    tar_codes = [
        "24530000",
        "24704202",
        "24704203",
        "24704205",
        "24705301",
        "24533026",
        "24531032",
        "25539080",
        "24853001",
        "24539154N",
        "24539161N",
        "24539633",
        "24539634",
        "24531701",
        "25538086",
        "24705201",
        "24705202",
        "24705203",
        "24705204",
        "24705205",
        "25705508",
        "25704116",
        "25704310",
        "24704333",
        "24705027",
        "25705013",
        "25705025",
        "24705001",
        "24705008",
        "24705310",
        "24705401",
        "25705514",
        "25705409",
        "24705422",
        "25705408",
        "25705206",
        "25705215",
        "25705314",
        "24705312",
        "24704030",
        "24704001",
        "24704002",
        "24704003",
        "25705005",
        "25705006",
        "25705007",
        "25704013",
        "25704014",
        "24704101",
        "24704117",
        "25704122",
        "25704123",
        "25704102",
        "25704105",
    ]
    import random

    random.seed(seed)
    tar_grades = [random.randint(1, 4) for _ in range(len(tar_codes))]

    grade_dict = {"講義コード": tar_codes, "GP": tar_grades}
    grade_df = pd.DataFrame(grade_dict)
    grade_df["学生番号"] = "1DS24SamP"
    # columnの並び変え 学生番号, 講義コード, GP
    grade_df = grade_df[["学生番号", "講義コード", "GP"]]
    grade_df.to_csv("ss.csv", encoding="utf-8", index=False)
    return grade_df


if __name__ == "__main__":
    rules_toml_path = os.path.join(os.path.dirname(__file__), "rules.toml")
    with open(rules_toml_path, "rb") as f:
        toml = tomllib.load(f)

    log_path = os.path.join(os.path.dirname(__file__), "log")
    os.makedirs(log_path, exist_ok=True)

    # テスト用のコード
    csv_path = os.path.join(
        os.path.dirname(__file__), "csv", "WQ_講義科目情報確認（芸工IDコース）.csv"
    )
    l = lectures.Lectures(
        toml,
        csv_path,
        "cp932",
    )
    l.separate_lectures(r"..33.*|..53.*|..85.*", r"..70.*")
    all_foundational_df, all_home_faculty_df = l.get_lectures()

    students_df = pd.read_csv("test_case_1.csv", encoding="utf-8")
    students_list = students_df["学生番号"].unique().tolist()

    for student_id in students_list:
        print(f"===== [{student_id}] =====")
        # load test data
        grade_df = students_df[students_df["学生番号"] == student_id]

        #    grade_df = test_case_1(1)
        lecture_key_list = grade_df["講義コード"].unique().tolist()
        l.check_undfined_lectures(lecture_key_list)

        gpts, log_str = lectures.calc_gpt_score(
            toml, all_foundational_df, all_home_faculty_df, grade_df
        )
        with open(
            os.path.join(log_path, f"{student_id}.txt"), "w", encoding="utf-8"
        ) as f:
            f.write(log_str)
        gpt_score = 0
        total_credits = 0
        for k, v in gpts.items():
            print(f"{k}: {v['gpt']:.2f} Credits: {v['valid_credits']}")
            gpt_score += v["gpt"]
            total_credits += v["valid_credits"]
        extrapolate_gpt = lectures.extrapolate_by_gpa(
            toml, gpt_score, total_credits, 3.8
        )
        print(
            f"GPT Score: {gpt_score:.2f} Total credits: {total_credits} ({extrapolate_gpt})\n"
        )
