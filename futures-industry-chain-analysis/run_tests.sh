#!/bin/bash
# 运行所有测试（正确方式：从skill根目录以包模式运行）
cd "$(dirname "$0")"

echo "=== 运行硬规则测试 ==="
python -m pytest tests/test_hard_rules.py -v 2>&1

echo ""
echo "=== 运行全部测试 ==="
python -m pytest tests/ -v 2>&1
