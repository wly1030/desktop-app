#!/usr/bin/env python3
"""
示例 Python 脚本
桌面应用会将表单参数以 JSON 字符串的形式通过命令行参数传入。
用法: python3 example.py '{"name":"test", "inputDir":"/tmp", ...}'
"""

import sys
import json


def main():
    if len(sys.argv) < 2:
        print("错误: 请提供 JSON 参数")
        print(f"用法: {sys.argv[0]} '<json_params>'")
        sys.exit(1)

    # 解析参数
    params = json.loads(sys.argv[1])

    print("=" * 50)
    print("收到参数:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    print("=" * 50)

    # 在这里编写你的业务逻辑
    name = params.get("name", "unnamed")
    input_dir = params.get("inputDir", "")
    output_dir = params.get("outputDir", "")
    threads = params.get("threads", 1)
    mode = params.get("mode", "normal")
    enable_log = params.get("enableLog", False)

    print(f"\n开始处理任务: {name}")
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print(f"线程数: {threads}")
    print(f"模式: {mode}")
    print(f"日志: {'启用' if enable_log else '禁用'}")
    print("\n任务执行完毕。")


if __name__ == "__main__":
    main()
