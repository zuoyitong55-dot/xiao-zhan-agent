import subprocess
import sys

def run(cmd):
    print(f"\n正在执行：{' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)

def main():
    run([sys.executable, "crawler/crawler.py"])
    run([sys.executable, "scripts/build_index.py"])
    print("\n更新完成：知识库和向量库已刷新。")

if __name__ == "__main__":
    main()
