"""
验收测试运行脚本
"""
import subprocess
import sys


def run_acceptance_tests():
    """运行验收测试"""
    print("=" * 60)
    print("电商风控系统 - 验收测试")
    print("=" * 60)

    # 运行测试
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_acceptance.py",
        "-v",
        "--tb=short"
    ]

    result = subprocess.run(cmd)

    print("\n" + "=" * 60)
    if result.returncode == 0:
        print("✅ 所有验收测试通过！")
    else:
        print("❌ 部分测试失败，请检查输出")
    print("=" * 60)

    return result.returncode


if __name__ == "__main__":
    sys.exit(run_acceptance_tests())
