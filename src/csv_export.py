import csv
import os
import tomllib

def export_csv(calc_res, file_path):
    if not calc_res:
        return

    root_path = os.path.dirname(os.path.abspath(__file__))
    rules_toml_path = os.path.join(root_path, "rules.toml")
    with open(rules_toml_path, "rb") as f:
        toml = tomllib.load(f)

    with open(file_path, mode="w", newline="", encoding=toml["params"]["csv_encoding"]) as csvfile:
        fieldnames = ["student_id", "student_name", "gpp", "gpa", "total_credits", "extrapolate_gpp", "credits_in_pool"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for res in calc_res:
            writer.writerow(
                {
                    "student_id": res["student_id"],
                    "student_name": res["student_name"],
                    "gpp": f"{res['gpp']:.1f}",
                    "gpa": f"{res['gpa']:.2f}",
                    "total_credits": f"{res['total_credits']:.1f}",
                    "extrapolate_gpp": f"{res['extrapolate_gpp']:.2f}",
                    "credits_in_pool": f"{res['credits_in_pool']:.1f}",
                }
            )
    print(f"Results exported to {file_path}")
