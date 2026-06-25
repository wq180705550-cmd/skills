#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商品期货产业链分析 - 依赖检测脚本
自动检测并安装必要的依赖
"""

import os
import sys
import subprocess
import shutil

def check_python():
    """检查Python环境"""
    print("[1/6] 检查Python环境...")
    version = sys.version_info
    print(f"  Python版本: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  [WARN] 建议使用Python 3.8+")
    else:
        print("  [OK] Python版本满足要求")
    return True

def check_pip():
    """检查pip"""
    print("\n[2/6] 检查pip...")
    try:
        import pip
        print(f"  pip版本: {pip.__version__}")
        print("  [OK] pip可用")
        return True
    except ImportError:
        print("  [ERROR] pip未安装")
        return False

def install_package(package_name, import_name=None):
    """安装Python包"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        return True
    except ImportError:
        print(f"  安装{package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name, "-q"])
            print(f"  [OK] {package_name}安装成功")
            return True
        except subprocess.CalledProcessError:
            print(f"  [ERROR] {package_name}安装失败")
            return False

def check_tqsdk():
    """检查TqSdk"""
    print("\n[3/6] 检查TqSdk...")
    
    # 检查环境变量（支持两种命名）
    tq_user = os.environ.get('TQSDK_USERNAME') or os.environ.get('TQ_USER')
    tq_password = os.environ.get('TQSDK_PASSWORD') or os.environ.get('TQ_PASSWORD')
    
    if tq_user and tq_password:
        print(f"  用户: {tq_user[:3]}***")
        print("  密码: ****")
        print("  [OK] 环境变量已设置")
    else:
        print("  [WARN] 环境变量TQSDK_USERNAME/TQSDK_PASSWORD或TQ_USER/TQ_PASSWORD未设置")
        print("  请设置环境变量后重试")
    
    # 检查tqsdk包
    return install_package("tqsdk")

def check_akshare():
    """检查AKshare"""
    print("\n[4/6] 检查AKshare...")
    return install_package("akshare")

def check_neodata():
    """检查neodata token"""
    print("\n[5/6] 检查neodata token...")
    
    token_path = os.path.expanduser("~/.workbuddy/skills/.neodata_token")
    if os.path.exists(token_path):
        print(f"  Token文件: {token_path}")
        print("  [OK] Token文件存在")
        return True
    else:
        print("  [WARN] Token文件不存在")
        print("  首次使用时会自动获取")
        return True

def check_analysis_modules():
    """检查分析模块"""
    print("\n[6/6] 检查分析模块...")
    
    # 检查industry_chain模块
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    industry_chain_path = os.path.join(skill_dir, "references", "industry_chain.py")
    
    if os.path.exists(industry_chain_path):
        print(f"  industry_chain.py: {industry_chain_path}")
        print("  [OK] 产业链模块存在")
    else:
        print("  [WARN] 产业链模块不存在")
    
    # 检查trading-analysis skill
    trading_analysis_path = os.path.expanduser(
        "~/.workbuddy/plugins/marketplaces/cb_teams_marketplace/plugins/trading-agent/skills/trading-analysis/SKILL.md"
    )
    if os.path.exists(trading_analysis_path):
        print("  [OK] trading-analysis skill已安装")
    else:
        print("  [WARN] trading-analysis skill未安装")
        print("  请安装trading-analysis skill")
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("商品期货产业链分析 - 依赖检测")
    print("=" * 60)
    
    results = []
    
    # 检查各项依赖
    results.append(("Python", check_python()))
    results.append(("pip", check_pip()))
    results.append(("TqSdk", check_tqsdk()))
    results.append(("AKshare", check_akshare()))
    results.append(("neodata", check_neodata()))
    results.append(("分析模块", check_analysis_modules()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("检测结果汇总:")
    print("=" * 60)
    
    all_ok = True
    for name, ok in results:
        status = "[OK]" if ok else "[FAIL]"
        print(f"  {name}: {status}")
        if not ok:
            all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok:
        print("所有依赖检测通过！")
        print("可以开始使用商品期货产业链分析功能。")
    else:
        print("部分依赖检测失败，请根据上述提示修复。")
    print("=" * 60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
