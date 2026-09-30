"""Create importable, unpublished placeholder problems for ZIP import tests."""

import argparse
import io
import json
import zipfile
from pathlib import Path


def add_file(archive, name, content):
    info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, content)


def problem_data(number):
    blank = {"format": "markdown", "value": ""}
    return {
        "title": f"占位题 {number:02d}",
        "description": blank,
        "input_description": blank,
        "output_description": blank,
        "hint": blank,
        "test_case_score": [
            {"score": 100, "input_name": "1.in", "output_name": "1.out"}
        ],
        "time_limit": 1000,
        "memory_limit": 256,
        "samples": [],
        "template": {},
        "spj": None,
        "rule_type": "ACM",
        "source": "ZIP 导入测试占位题；发布前请补全题面与数据",
        "tags": ["导入测试"],
        "difficulty": "Low",
        "visible": False,
        "languages": ["C++", "Python3"],
    }


def make_single(number):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        add_file(archive, "problem.json", json.dumps(
            problem_data(number), ensure_ascii=False, indent=2
        ).encode("utf-8"))
        # The importer requires a numbered input/output pair. These empty
        # files only exercise import; they are not real judging data.
        add_file(archive, "testcase/1.in", b"")
        add_file(archive, "testcase/1.out", b"")
    return output.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument(
        "--output", type=Path,
        default=Path(__file__).resolve().parents[1] / "test-fixtures" / "blank-problem-bank",
    )
    args = parser.parse_args()
    if not 1 <= args.count <= 999:
        parser.error("--count must be between 1 and 999")
    args.output.mkdir(parents=True, exist_ok=True)

    single_path = args.output / "blank-single.zip"
    batch_path = args.output / f"blank-{args.count:02d}-batch.zip"
    single_path.write_bytes(make_single(1))
    with zipfile.ZipFile(batch_path, "w") as archive:
        for number in range(1, args.count + 1):
            add_file(archive, f"{number:03d}.zip", make_single(number))

    readme = args.output / "README.md"
    readme.write_text(
        "# ZIP 导入测试占位题库\n\n"
        "- `blank-single.zip`：根目录单题 ZIP，含 `problem.json` 和空的 `testcase/1.in`、`1.out`。\n"
        f"- `{batch_path.name}`：由 {args.count} 个独立单题 ZIP 组成，根目录仅含 `001.zip` 等文件。\n"
        "- 在管理端「导入 ZIP 题库」选择其中一个 ZIP 上传。导入时 OJ 自动分配显示 ID。\n"
        "- 所有题目默认不可见，题面与测试数据为空；只用于导入和页面测试。请补全数据再发布或判题。\n",
        encoding="utf-8",
    )
    print(single_path)
    print(batch_path)


if __name__ == "__main__":
    main()
