import os
import tomllib

import pandas as pd

import lectures
from credit_pool import CreditPool


def calc_gpt_score(toml, lectures_df, grade_df):
    t_categories = toml["categories"]
    secondary_categories = toml["secondary_categories"]
    col = toml["columns_in_lectures"]

    log_str = ""
    pl = lectures.PersonalLectures(
        lectures_df,
        col["key"],
        col["category"],
        col["credit"],
    )
    pl.set_grades(grade_df)
    pl.make_grades_df()
    use_cols = [
        col["key"],
        col["name"],
        col["category"],
        col["credit"],
        "GP",
        "point",
    ]
    pl.check_undefined_lectures(t_categories)

    gpts = {k: {"credit": 0, "gpt": 0} for k in t_categories.keys()}
    gpts["Overflow_pool"] = {"credit": 0, "gpt": 0}

    # CreditPool
    credit_pools = {}
    print("Credit Pools:")
    for k, v in secondary_categories.items():
        credit_pools[k] = CreditPool(v["max_credits"], v["category"])
        print(f"{k}: {v['max_credits']} credits")

    # concat用のDataFrameを作成、column名を揃える
    pool_df = pd.DataFrame(columns=lectures_df.columns)
    for k, v in t_categories.items():
        log_str += f"\n======== [{k}] ========\n"
        categories = v["category"]
        max_credits = v["max_credits"]
        my_courses = v["my_courses"]
        home_lecture_df = pl.extract_lecture_by_category(categories)

        # 自コースの講義がある場合は、is_homeを追加
        if len(my_courses) > 0:
            home_lecture_df = lectures.add_is_home_col(
                home_lecture_df, col["category"], my_courses
            )
            # sort by is_home
            home_lecture_df = home_lecture_df.sort_values(
                by=["is_home", "GP", col["credit"]],
                ascending=[True, False, True],
            )

        a_df, b_df = lectures.select_lecture_to_knapsack(
            home_lecture_df, float(max_credits), col
        )
        log_str += str(a_df[use_cols].set_index(col["key"])) + "\n"
        total_point = a_df["point"].sum()
        total_credits = home_lecture_df[col["credit"]].sum()

        # secondary categories
        if total_credits > max_credits:
            for cp in credit_pools.values():
                v_df = b_df[
                    b_df[col["category"]].str.fullmatch(
                        "|".join(cp.get_category_names())
                    )
                ]
                surplus_credits = v_df[col["credit"]].sum()
                surplus_credits = cp.add_credits(surplus_credits)
            total_credits = max_credits
        elif total_credits < max_credits:
            shortage_credits = max_credits - total_credits
            if k in credit_pools:
                got_credits = credit_pools[k].use_credits(shortage_credits)
                total_credits += got_credits
                log_str += f"Got from secondary categories: {got_credits}\n"

        log_str += f"合計ポイント: {total_point:.2f}  合計単位数: {total_credits}/{max_credits}\n"
        if len(b_df) > 0:
            log_str += "--- Overflow ---\n"
            log_str += str(b_df[use_cols].set_index(col["key"])) + "\n"

        gpts[k]["credits"] = total_credits
        gpts[k]["gpt"] = total_point

        # b_dfのうちis_homeがTrueの行を抽出してpool_dfに追加
        if b_df.columns.str.contains("is_home").any():
            pool_df = pd.concat([pool_df, b_df[b_df["is_home"]]])

    total_point = pool_df["point"].sum()
    total_credits = pool_df[col["credit"]].sum()
    gpts["Overflow_pool"]["credits"] = 0
    gpts["Overflow_pool"]["gpt"] = total_point
    log_str += "\n======== [Overflow Pool] ========\n"
    log_str += str(pool_df[use_cols].set_index(col["key"])) + "\n"
    log_str += f"合計ポイント: {total_point:.2f}\n"

    return gpts, log_str


def extrapolate_by_gpa(toml, gpt_score, total_credits, gpa):
    target_credits = toml["params"]["extrapolate_target_credits"]
    if not isinstance(target_credits, (int, float)):
        raise ValueError("total_gpt must be an integer or float")
    else:
        target_credits = int(target_credits)

    if total_credits >= target_credits:
        result = gpt_score
    else:
        result = gpt_score + gpa * (target_credits - total_credits)
    return result


def calc_all(lecture_csv_path: str, student_csv_path: str, csv_encoding: str = "utf-8"):
    rules_toml_path = os.path.join(os.path.dirname(__file__), "rules.toml")
    with open(rules_toml_path, "rb") as f:
        toml = tomllib.load(f)

    log_path = os.path.join(os.path.dirname(__file__), "log")
    os.makedirs(log_path, exist_ok=True)

    csv_path = os.path.join(os.path.dirname(__file__), "csv", lecture_csv_path)
    l = lectures.Lectures(
        toml,
        csv_path,
    )

    lectures_df = l.get_lectures()

    students_df = pd.read_csv(student_csv_path, encoding=csv_encoding)
    students_list = students_df["学生番号"].unique().tolist()

    calc_res = []
    for student_id in students_list:
        res_dict = {
            "student_id": student_id,
            "gpt_score": 0,
            "total_credits": 0,
            "extrapolate_gpt": 0,
        }
        print(f"===== [{student_id}] =====")
        # load test data
        grade_df = students_df[students_df["学生番号"] == student_id]

        lecture_key_list = grade_df["講義コード"].unique().tolist()
        l.check_undefined_lectures(lecture_key_list)

        gpts, log_str = calc_gpt_score(toml, lectures_df, grade_df)
        with open(
            os.path.join(log_path, f"{student_id}.txt"), "w", encoding="utf-8"
        ) as f:
            f.write(log_str)
        gpt_score = 0
        total_credits = 0
        for k, v in gpts.items():
            print(f"{k}: {v['gpt']:.2f} Credits: {v['credits']}")
            gpt_score += v["gpt"]
            total_credits += v["credits"]
        extrapolate_gpt = extrapolate_by_gpa(toml, gpt_score, total_credits, 3.8)
        res_dict["gpt_score"] = gpt_score
        res_dict["total_credits"] = total_credits
        res_dict["extrapolate_gpt"] = extrapolate_gpt
        calc_res.append(res_dict)
    return calc_res
