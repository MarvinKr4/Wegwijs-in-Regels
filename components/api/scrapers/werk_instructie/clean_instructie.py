import re
from pathlib import Path

INPUT_FILE = Path(__file__).parent / "instructie.txt"
OUTPUT_FILE = Path(__file__).parent / "instructie_cleaned.txt"


def main():
    lines: list[str]
    with open(INPUT_FILE, "r") as f:
        lines = f.readlines()

    clean_lines: list[str] = []
    curr_footnote_num: int = 1
    skip: list[int] = []
    page_num = re.compile(r"\x0c\d{1,2}\n")
    for i, line in enumerate(lines):
        # print(f"{i=}", f"{line=}", f"{curr_footnote_num=}")
        if i in skip:
            # print(f"Skipping {i=}")
            continue
        elif (
            line
            == "Rijksbrede instructie voor het behandelen van Woo-verzoeken - Versie 2024\n"
        ):
            # print(f"Skipping {i=}")
            continue
        elif re.findall(page_num, line):
            # print(f"Skipping {i=}")
            continue
        elif line.startswith(f"{curr_footnote_num} "):
            possible_eol = 0

            for j in range(i + 1, i + 4):
                # print(f"{j=}", f"{lines[j]=}")

                if not lines[j].startswith(f"{curr_footnote_num + 1} "):
                    continue
                elif lines[j].startswith(f"{curr_footnote_num + 1} "):
                    r = [*range(i, j)]
                    # print(f"Adding range {r} to skip, [from {i=} to {j-1=}]")
                    skip.extend(r)
                    break
                elif lines[j][0].isupper():
                    possible_eol = j
                if j == i + 3 and possible_eol != 0:
                    r = [*range(i, possible_eol)]
                    skip.extend(r)
                    # print(f"Adding range {r} to skip, [from {i=} to {possible_eol-1=}]")
            curr_footnote_num += 1
        else:
            # print(f"Adding line: {line}")
            clean_lines.append(line)
    # print(skip)

    with open(OUTPUT_FILE, "w") as f:
        f.writelines(clean_lines)


if __name__ == "__main__":
    main()
