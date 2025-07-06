from decimal import ROUND_HALF_UP, Decimal, getcontext

import pandas as pd

pd.set_option("display.unicode.east_asian", True)
pd.set_option("display.unicode.ambiguous_as_wide", True)


class Lectures:
    def __init__(self, toml, csv_path):
        """
        Read CSV and separate basic tables based on key_col_name in the constructor.
        self.all_lectures_df: All lecture information
        :param toml: Dictionary containing column definitions and other settings
        :param csv_path: Path to the CSV file
        :param encoding: Encoding of the CSV file
        """

        self.key_col_name = toml["columns_in_lectures"]["key"]
        self.category_col_name = toml["columns_in_lectures"]["category"]
        self.all_lectures_df = pd.read_csv(
            csv_path, encoding=toml["params"]["csv_encoding"], dtype=str, header=0
        )

        # duplicate check
        duplicate_lectures = self.all_lectures_df[
            self.all_lectures_df.duplicated(subset=[self.key_col_name], keep=False)
        ]
        if not duplicate_lectures.empty:
            # extract the duplicate values
            duplicate_values = duplicate_lectures[self.key_col_name].unique()
            duplicate_values_str = ", ".join(duplicate_values)
            print(
                f"Duplicate values found in {self.key_col_name}: {duplicate_values_str}"
            )
            raise ValueError(f"Duplicate values found in {self.key_col_name}.")

    def get_category_names(self, tar_col_name):
        return self.all_lectures_df[tar_col_name].unique().tolist()

    def get_lectures(self):
        return self.all_lectures_df

    def check_undefined_lectures(self, key_list, student_id=None):
        """
        Extract IDs that exist in key_list but not in self.all_lectures_df.
        :param key_list: List of lecture IDs
        :return: List of undefined lecture IDs
        """
        all_lectures = self.all_lectures_df[self.key_col_name].tolist()
        undefined_lectures = list(set(key_list) - set(all_lectures))
        if undefined_lectures:
            print(f"===== undefined lecture for student {student_id} =====")
            print(undefined_lectures)
            return undefined_lectures
        else:
            return []

    def _extract_by_lecture_code(self, pattern):
        """
        Extract rows where key_col_name matches the regular expression.
        :param pattern: Regular expression
        :return: Extracted DataFrame
        """
        dst_df = self.all_lectures_df[
            self.all_lectures_df[self.key_col_name].str.match(pattern)
        ]
        print(f"rows: {dst_df.shape[0]} ({pattern})")
        return dst_df


class PersonalLectures:
    def __init__(
        self,
        lectures_df: pd.DataFrame,
        key_col_name: str,
        category_col_name: str,
        credit_col_name: str,
        grade_col_name: str,
    ):
        """
        Extract lecture information based on category_col_name
        :param lectures_df: All lecture information
        :param key_col_name: Column name for lecture ID
        """
        self.key_col_name = key_col_name
        self.category_col_name = category_col_name
        self.credit_col_name = credit_col_name
        self.grade_col_name = grade_col_name

        # Convert credits to float type
        lectures_df = lectures_df.copy()
        lectures_df[credit_col_name] = lectures_df[credit_col_name].astype(float)
        self.all_lectures_df = lectures_df

    def get_home_lecture_categories(self):
        """
        For debugging.
        :return: Unique categories in self.my_lectures_df[self.category_col_name]
        """
        lecture_category_list = self.all_lectures_df[self.category_col_name].unique()

        return lecture_category_list

    def set_grades(self, grades_df: pd.DataFrame):
        # convert SABC grades to GP
        grades_df = grades_df.copy()
        grades_df = grades_df[grades_df[self.grade_col_name].isin(["Ｓ", "Ａ", "Ｂ", "Ｃ", "Ｆ", "S", "A", "B", "C", "F", "s", "a", "b", "c", "f"])]
        grades_df["GP"] = grades_df[self.grade_col_name].map(
            {"Ｓ": 4.0, "Ａ": 3.0, "Ｂ": 2.0, "Ｃ": 1.0, "Ｆ": 0.0, "S": 4.0, "A": 3.0, "B": 2.0, "C": 1.0, "F": 0.0, "s": 4.0, "a": 3.0, "b": 2.0, "c": 1.0, "f": 0.0}
        )
        self.grades_df = grades_df

    def make_grades_df(self):
        codes = self.grades_df[self.key_col_name].tolist()
        pattern = "|".join(codes)
        dst_df = self.all_lectures_df[
            self.all_lectures_df[self.key_col_name].str.fullmatch(pattern)
        ]
        dst_df = dst_df.merge(
            self.grades_df, on=self.key_col_name, how="left", suffixes=("", "_student")
        )
        dst_df["point"] = dst_df[self.credit_col_name].astype(float) * dst_df[
            "GP"
        ].astype(float)

        # If blank, it seems the lecture was not offered in the relevant year, so replace with Closed
        dst_df[self.category_col_name] = dst_df[self.category_col_name].fillna("Closed")

        self.my_lectures_df = dst_df

    def extract_lecture_by_category(self, categories: list[str]):
        """
        Extract lectures from self.my_lectures_df whose category matches any of the given categories.
        :param categories: List of category patterns (regular expressions)
        :return: DataFrame of matched lectures, sorted by GP and credit
        """
        dst_df = pd.DataFrame()
        for category in categories:
            # Extract lecture information
            tmp_df = self.my_lectures_df[
                self.my_lectures_df[self.category_col_name].str.fullmatch(category)
            ]
            dst_df = pd.concat([dst_df, tmp_df], ignore_index=True)
        # sort by GP
        dst_df = dst_df.sort_values(
            by=["GP", self.credit_col_name], ascending=[False, True]
        )
        return dst_df

    def calculate_gpa(self):
        """
        Calculate GPA based on the GP and credit columns.
        :return: GPA value
        """
        if self.my_lectures_df.empty:
            return 0.0

        total_points = (
            self.my_lectures_df["GP"] * self.my_lectures_df[self.credit_col_name]
        ).sum()
        total_credits = self.my_lectures_df[self.credit_col_name].sum()

        if total_credits == 0:
            return 0.0

        decimal_total_points = Decimal(str(total_points))
        decimal_total_credits = Decimal(str(total_credits))
        # Calculate GPA
        getcontext().prec = 3  # Set precision for Decimal calculations
        gpa = float(decimal_total_points / decimal_total_credits)
        rounded_gpa = Decimal(gpa).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return float(rounded_gpa)

    def check_undefined_lectures(self, categories: list[str]):
        """
        Search the list of categories.category described in the TOML file and combine into a single list
        :return: List of categories
        """
        valid_categories = []
        for v in categories.values():
            for k, vv in v.items():
                if k == "category":
                    valid_categories.extend(vv)
        # Extract lecture information that does not match valid_categories
        dst_df = self.my_lectures_df[
            ~self.my_lectures_df[self.category_col_name].str.fullmatch(
                "|".join(valid_categories)
            )
        ]
        if not dst_df.empty:
            print("===== invalid lecture =====")
            print(dst_df)


def add_is_home_col(src_df: pd.DataFrame, col_name: str, categories: list[str]):
    """
    Add a boolean column 'is_home' to src_df based on whether the value in col_name matches any of the given categories.
    :param src_df: DataFrame of lecture information
    :param col_name: Name of the column to match categories against
    :param categories: List of categories to match
    :return: DataFrame with 'is_home' column added
    """
    category_stmt = "|".join(categories)
    src_df["is_home"] = src_df[col_name].str.match(category_stmt)
    return src_df


def select_lecture_to_knapsack(
    src_df: pd.DataFrame, max_credits: float, col_names: dict
):
    """
    src_df contains lecture information, and each lecture has a credit value between 0.5 and 4.0.
    This function is for solving the knapsack problem, selecting lectures to maximize GP while considering credits.
    Step 1: Sort src_df in descending order of GP (or is_home and GP).
    Step 2: Select lectures so as not to exceed max_credits.
    Step 3: If max_credits is not reached, select one more lecture from idx.
    Step 4: If max_credits is exceeded, split the last record.

    :param src_df: DataFrame of lecture information
    :param max_credits: Maximum number of credits
    :param col_names: Definition of column names
    :return: selected_df, unselected_df
    """

    selected_df = pd.DataFrame(columns=src_df.columns)

    # Step 1: Sort the DataFrame based on priority
    # If 'is_home' column exists, prioritize False values first, then by GP
    if "is_home" in src_df.columns:
        sorted_df = src_df.sort_values(
            by=["is_home", "GP", col_names["credit"]],
            ascending=[True, False, True],
        ).reset_index(drop=True)
    else:
        # If column doesn't exist, just sort by GP (high to low)
        sorted_df = src_df.sort_values(
            by=["GP", col_names["credit"]], ascending=[False, True]
        ).reset_index(drop=True)

    # Step 2: Select lectures to maximize points while staying within credit limit
    total_credits = 0
    idx = 0
    for idx, row in sorted_df.iterrows():
        if total_credits + row[col_names["credit"]] > max_credits:
            break
        selected_df = pd.concat([selected_df, row.to_frame().T], ignore_index=False)
        total_credits += row[col_names["credit"]]

    # Step 3: If we haven't reached the minimum credits, add one more lectures from idx
    if total_credits < max_credits and idx + 1 < len(sorted_df):
        idx += 1
        selected_df = pd.concat([selected_df, sorted_df.loc[[idx]]], ignore_index=False)
        total_credits += sorted_df.loc[idx, col_names["credit"]]

    # Extract unselected lecture information
    unselected_df = sorted_df[~sorted_df.index.isin(selected_df.index)]

    # Step 4: If we exceed the max credits, split the last lecture
    if total_credits > max_credits:
        over_credits = total_credits - max_credits

        last_row = selected_df.iloc[-1].copy()
        org_last_row = last_row.copy()
        # update 'credit' and 'point' columns
        last_row[col_names["credit"]] = org_last_row[col_names["credit"]] - over_credits
        last_row["point"] = org_last_row["point"] - over_credits * org_last_row["GP"]

        selected_df.iloc[-1] = last_row

        # Add the split lecture to unselected_df
        unselected_row = org_last_row.copy()
        unselected_row[col_names["key"]] = org_last_row[col_names["key"]] + "-sep"
        unselected_row[col_names["credit"]] = total_credits - max_credits
        unselected_row["point"] = over_credits * unselected_row["GP"]
        unselected_df = pd.concat(
            [unselected_df, unselected_row.to_frame().T], ignore_index=False
        )

    return selected_df, unselected_df
