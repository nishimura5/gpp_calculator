import os

import pandas as pd

import lectures
from credit_pool import CreditPool
from input_formatting import preprocess

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
        toml["columns_in_students"]["grade"],
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
    if toml["params"].get("year_filter", False):
        use_cols.append("year")
        append_cols = pd.Index(["point", "GP", "year"])
    else:
        append_cols = pd.Index(["point", "GP"])

    gpts = {k: {"credit": 0, "gpp": 0} for k in t_categories.keys()}
    gpts["Overflow_pool"] = {"credit": 0, "gpp": 0}

    # CreditPool
    credit_pools = {}
    for k, v in secondary_categories.items():
        credit_pools[k] = CreditPool(v["max_credits"], v["category"])

    # concat用のDataFrameを作成、column名を揃える
    columns = lectures_df.columns
    columns = columns.append(append_cols)
    pool_df = pd.DataFrame(columns=columns)

    used_by_secondary_credits = 0
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
                log_str += f"<From secondary categories: {got_credits:+}>\n"
                used_by_secondary_credits += got_credits

        log_str += (
            f"Points: {total_point:.1f}  Credits: {total_credits}/{max_credits}\n"
        )
        if len(b_df) > 0:
            log_str += "-------- Overflow --------\n"
            log_str += str(b_df[use_cols].set_index(col["key"])) + "\n"

        gpts[k]["credits"] = total_credits
        gpts[k]["gpp"] = total_point

        # b_dfのうちis_homeがTrueの行を抽出してpool_dfに追加
        if b_df.columns.str.contains("is_home").any():
            home_df = b_df[b_df["is_home"]]
            if (
                not home_df.empty
                and home_df.shape[1] > 0
                and not home_df.isna().all().all()
            ):
                if pool_df.empty:
                    pool_df = home_df.copy()
                else:
                    pool_df = pd.concat([pool_df, home_df], ignore_index=True)

    total_point = pool_df["point"].sum()
    pool_credits = pool_df[col["credit"]].sum() - used_by_secondary_credits
    gpts["Overflow_pool"]["credits"] = pool_credits
    gpts["Overflow_pool"]["gpp"] = total_point
    log_str += "\n======== [Overflow Pool] ========\n"
    log_str += str(pool_df[use_cols].set_index(col["key"])) + "\n"
    if used_by_secondary_credits > 0:
        log_str += f"<To secondary categories: {used_by_secondary_credits * (-1):+}>\n"
    log_str += f"Points: {total_point:.1f}  Credits: {pool_credits}\n"
    log_str += f"\nTotal Points: {sum(v['gpp'] for v in gpts.values()):.1f}"

    # calculate GPA. Not use gpp
    gpa = pl.calculate_gpa()
    log_str += f" (GPA: {gpa:.2f})"

    return gpts, gpa, log_str


def extrapolate_by_gpa(toml, gpp, total_credits, gpa):
    target_credits = toml["params"]["extrapolate_target_credits"]
    if not isinstance(target_credits, (int, float, str)):
        raise ValueError(f"total_gpp must be an integer or float: {target_credits}")
    else:
        target_credits = int(target_credits)

    if total_credits >= target_credits:
        result = gpp
    else:
        result = gpp + gpa * (target_credits - total_credits)
    return result

def calc_all(toml, csv_encoding: str = "utf-8", progress_bar=None, master=None):
    root_path = os.path.dirname(os.path.abspath(__file__))
    lecture_csv_path = os.path.join(root_path, "lectures.csv")
    student_csv_path = os.path.join(root_path, "students.csv")

    preprocess.update_lectures_csv(lecture_csv_path, toml)
    preprocess.update_students_csv(student_csv_path, toml)

    log_path = os.path.join(root_path, "log")
    os.makedirs(log_path, exist_ok=True)

    lecture_key_col_name = toml["columns_in_lectures"]["key"]
    student_id_col_name = toml["columns_in_students"]["key"]
    student_name = toml["columns_in_students"]["name"]

    lec = lectures.Lectures(
        toml,
        lecture_csv_path,
    )

    lectures_df = lec.get_lectures()

    students_df = pd.read_csv(student_csv_path, encoding=csv_encoding)
    students_list = students_df[student_id_col_name].unique().tolist()

    if toml["params"].get("year_filter", False):
        season_map_dict = {
            "1": ["春学期"],
            "2": ["夏学期", "前期", "前期集中"],
            "3": ["秋学期"],
            "4": ["冬学期", "後期", "後期集中", "通期集中"],
        }
        season_sr = students_df["履修学期"].map(
            {v: k for k, vs in season_map_dict.items() for v in vs}
        )
        # nanを想定した整数型に変換
        students_df["year"] = students_df["履修年度"].astype(str) + season_sr
        students_df = students_df[students_df["year"].astype("Int64") <= 20243]

    calc_res = []
    if progress_bar is not None and master is not None:
        total_students = len(students_list)
        progress_bar.configure(maximum=total_students)
    for student_id in students_list:
        if progress_bar is not None and master is not None:
            progress_bar.configure(value=students_list.index(student_id) + 1)
            master.update_idletasks()  # Update UI

        grade_df = students_df[students_df[student_id_col_name] == student_id]
        if grade_df.empty:
            print(f"Warning: No grades found for student {student_id}. Skipping.")
            res_dict = {
                "student_id": student_id,
                "student_name": "Unknown",
                "gpp": 0,
                "gpa": 0,
                "total_credits": 0,
                "extrapolate_gpp": 0,
                "credits_in_pool": 0,
            }
            calc_res.append(res_dict)
            continue

        res_dict = {
            "student_id": student_id,
            "student_name": students_df[students_df[student_id_col_name] == student_id][
                student_name
            ].values[0],
            "gpp": 0,
            "gpa": 0,
            "total_credits": 0,
            "extrapolate_gpt": 0,
        }

        lecture_key_list = grade_df[lecture_key_col_name].unique().tolist()
        lec.check_undefined_lectures(lecture_key_list, student_id)

        gpts, gpa, log_str = calc_gpt_score(toml, lectures_df, grade_df)
        with open(
            os.path.join(log_path, f"{student_id}.txt"), "w", encoding="utf-8"
        ) as f:
            f.write(log_str)
        gpt_score = 0
        total_credits = 0
        for k, v in gpts.items():
            gpt_score += v["gpp"]
            if k != "Overflow_pool":
                total_credits += v["credits"]
        extrapolate_gpt = extrapolate_by_gpa(toml, gpt_score, total_credits, gpa)
        res_dict["gpp"] = gpt_score
        res_dict["gpa"] = gpa
        res_dict["total_credits"] = total_credits
        res_dict["extrapolate_gpp"] = extrapolate_gpt
        res_dict["credits_in_pool"] = gpts["Overflow_pool"]["credits"]
        calc_res.append(res_dict)
    return calc_res
