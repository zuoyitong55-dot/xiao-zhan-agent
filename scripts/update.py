from pathlib import Path
import subprocess
import sys
import time

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_step(title, command):
    print("\n" + "=" * 60)
    print(f"【{title}】")
    print("=" * 60)

    start = time.time()

    result = subprocess.run(command)

    if result.returncode != 0:
        print(f"\n❌ {title} 执行失败")
        sys.exit(result.returncode)

    cost = time.time() - start

    print(f"✅ {title} 完成（{cost:.2f} 秒）")


def main():

    total_start = time.time()

    # -------------------------------------------------
    # 1. 自动搜索（如果存在）
    # -------------------------------------------------

    search_script = PROJECT_ROOT / "crawler" / "search.py"

    if search_script.exists():

        run_step(
            "自动搜索网页",
            [
                sys.executable,
                str(search_script),
            ],
        )

    else:

        print("\n跳过 search.py（尚未创建）")

    # -------------------------------------------------
    # 2. 爬虫
    # -------------------------------------------------

    crawler_script = PROJECT_ROOT / "crawler" / "crawler.py"

    if not crawler_script.exists():

        print("找不到 crawler.py")

        sys.exit(1)

    run_step(
        "更新知识库",
        [
            sys.executable,
            str(crawler_script),
        ],
    )

    # -------------------------------------------------
    # 3. 建立向量数据库
    # -------------------------------------------------

    build_script = PROJECT_ROOT / "scripts" / "build_index.py"

    if not build_script.exists():

        print("找不到 build_index.py")

        sys.exit(1)

    run_step(
        "构建向量数据库",
        [
            sys.executable,
            str(build_script),
        ],
    )

    total_cost = time.time() - total_start

    print("\n" + "=" * 60)
    print("🎉 全部更新完成")
    print(f"总耗时：{total_cost:.2f} 秒")
    print("=" * 60)


if __name__ == "__main__":
    main()
