import csv


def export_csv(calc_res, file_path):
    if not calc_res:
        return

    with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["student_id", "gpp", "total_credits", "extrapolate_gpp"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for res in calc_res:
            writer.writerow(
                {
                    "student_id": res["student_id"],
                    "gpp": f"{res['gpp']:.1f}",
                    "total_credits": f"{res['total_credits']:.1f}",
                    "extrapolate_gpp": f"{res['extrapolate_gpp']:.1f}",
                }
            )
    print(f"Results exported to {file_path}")
