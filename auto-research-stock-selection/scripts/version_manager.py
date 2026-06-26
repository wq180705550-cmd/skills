#!/usr/bin/env python3
"""
版本管理脚本 - 稳健低波价值优选
基于华泰证券自进化Skill框架实现
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
import shutil

def load_config(config_path="skill_config.yaml"):
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def create_version_dir(version_id, hypothesis, tunable_params):
    """
    创建新版本目录
    """
    version_dir = Path("versions") / version_id
    version_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 保存版本配置
    config = load_config()
    version_config = {
        'version_id': version_id,
        'created_at': datetime.now().isoformat(),
        'hypothesis': hypothesis,
        'tunable_params': tunable_params,
        'base_config': config
    }
    
    config_file = version_dir / "config.yaml"
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(version_config, f, allow_unicode=True, default_flow_style=False)
    
    # 2. 创建子目录
    (version_dir / "holdings").mkdir(exist_ok=True)
    (version_dir / "scores").mkdir(exist_ok=True)
    (version_dir / "backtest_results").mkdir(exist_ok=True)
    
    # 3. 创建版本日志
    log_file = version_dir / "version_log.md"
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"# Version Log: {version_id}\n\n")
        f.write(f"**创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**改进假设**: {hypothesis}\n\n")
        f.write(f"**修改参数**:\n")
        for param, value in tunable_params.items():
            f.write(f"- {param}: {value}\n")
        f.write(f"\n## 回测结果\n\n")
        f.write(f"TODO: 运行回测后填写\n\n")
        f.write(f"## 是否保留\n\n")
        f.write(f"TODO: 根据验证集结果判断\n")
    
    print(f"版本目录已创建: {version_dir}")
    return version_dir

def evaluate_version(version_dir, validation_metrics, threshold=0.0):
    """
    评估版本是否保留
    基于验证集夏普比率改善
    """
    # 读取父版本的验证集结果
    parent_dir = version_dir.parent
    parent_backtest = parent_dir / "backtest_results" / "validation_set.json"
    
    if not parent_backtest.exists():
        print("警告: 父版本无验证集结果，默认保留")
        return True
    
    with open(parent_backtest, 'r', encoding='utf-8') as f:
        parent_metrics = json.load(f)['metrics']
    
    # 比较验证集夏普比率
    parent_sharpe = parent_metrics['sharpe_ratio']
    current_sharpe = validation_metrics['sharpe_ratio']
    
    improvement = current_sharpe - parent_sharpe
    
    print(f"父版本验证集夏普比率: {parent_sharpe:.4f}")
    print(f"当前版本验证集夏普比率: {current_sharpe:.4f}")
    print(f"改善幅度: {improvement:.4f}")
    
    if improvement > threshold:
        print(f"✅ 版本保留 (改善 > {threshold})")
        return True
    else:
        print(f"❌ 版本回滚 (改善 <= {threshold})")
        return False

def update_version_log(version_dir, validation_metrics, is_kept, failure_reason=None):
    """更新版本日志"""
    log_file = version_dir / "version_log.md"
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n---\n\n")
        f.write(f"## 验证集结果\n\n")
        f.write(f"- 年化收益率: {validation_metrics['annualized_return']:.2%}\n")
        f.write(f"- 年化波动率: {validation_metrics['annualized_volatility']:.2%}\n")
        f.write(f"- 夏普比率: {validation_metrics['sharpe_ratio']:.4f}\n")
        f.write(f"- 最大回撤: {validation_metrics['max_drawdown']:.2%}\n\n")
        
        f.write(f"## 版本决策\n\n")
        if is_kept:
            f.write(f"✅ **保留此版本**\n\n")
            f.write(f"理由: 验证集夏普比率改善\n")
        else:
            f.write(f"❌ **回滚此版本**\n\n")
            f.write(f"理由: {failure_reason}\n")
            f.write(f"建议: 恢复至父版本配置\n")

def list_versions():
    """列出所有版本"""
    versions_dir = Path("versions")
    
    if not versions_dir.exists():
        print("无版本目录")
        return
    
    print("版本列表:")
    for version_dir in sorted(versions_dir.iterdir()):
        if version_dir.is_dir():
            log_file = version_dir / "version_log.md"
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 提取第一行作为摘要
                    summary = content.split('\n')[0] if content else ""
                    print(f"  {version_dir.name}: {summary}")

def main():
    """主函数"""
    print("版本管理脚本框架已创建")
    print("TODO: 接入完整版本管理逻辑")
    
    # 示例: 创建新版本
    # version_dir = create_version_dir(
    #     "v0.2.28_test",
    #     "提高红利防守权重从0.33至0.40",
    #     {"dividend_weight": 0.40}
    # )
    
    # 示例: 评估版本
    # validation_metrics = {"sharpe_ratio": 0.85, ...}
    # is_kept = evaluate_version(version_dir, validation_metrics)
    
    # 示例: 更新日志
    # update_version_log(version_dir, validation_metrics, is_kept)

if __name__ == "__main__":
    main()
