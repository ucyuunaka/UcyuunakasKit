#!/usr/bin/env python3
"""
pyw2md自动化构建脚本

功能说明：
- 提供一键构建pyw2md可执行文件的功能
- 支持版本管理和自动递增
- 提供详细的构建日志和错误处理
- 集成环境检查和依赖验证

设计思路：
- 基于现有的构建辅助工具和版本管理器
- 提供模块化的构建流程
- 支持灵活的配置选项
- 确保构建过程的可靠性

使用方法：
    python build.py                    # 默认构建
    python build.py --clean          # 清理后构建
    python build.py --version patch  # 递增补丁版本
    python build.py --debug          # 调试模式构建
"""

import os
import sys
import shutil
import argparse
import subprocess
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入项目模块
try:
    from utils.build_helper import BuildHelper
    from utils.version_manager import VersionManager
    from utils import packaging
except ImportError as e:
    print(f"错误: 无法导入构建工具: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)


class Pyw2mdBuilder:
    """pyw2md构建器

    负责协调整个构建流程，包括环境检查、版本管理、
    PyInstaller执行和结果验证。
    """

    def __init__(self, project_root: Path):
        """初始化构建器

        Args:
            project_root: 项目根目录
        """
        self.project_root = project_root
        self.build_dir = project_root / "build"
        self.dist_dir = project_root / "dist"
        self.spec_file = project_root / "pyw2md.spec"

        # 初始化工具
        self.build_helper = BuildHelper(str(project_root))
        self.version_manager = VersionManager(str(project_root))

        # 构建配置
        self.config = {
            "clean_first": False,
            "version_bump": None,
            "debug_mode": False,
            "verbose": False,
            "create_tag": True,
            "upx_compress": True
        }

    def build(self) -> bool:
        """执行完整构建流程

        Returns:
            构建是否成功
        """
        print("=" * 60)
        print("pyw2md 自动化构建系统")
        print("=" * 60)
        print(f"项目根目录: {self.project_root}")
        print(f"构建开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        try:
            # 1. 环境检查
            if not self._check_environment():
                return False

            # 2. 打包环境验证
            if not self._verify_packaging_environment():
                return False

            # 3. 版本管理
            if not self._handle_version():
                return False

            # 4. 清理构建目录
            if self.config["clean_first"]:
                self._clean_build_directories()

            # 5. 执行PyInstaller构建
            if not self._run_pyinstaller():
                return False

            # 6. 验证构建结果
            if not self._verify_build():
                return False

            # 7. 生成构建报告
            self._generate_build_report()

            print()
            print("=" * 60)
            print("[SUCCESS] 构建成功完成!")
            print(f"构建完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            return True

        except Exception as e:
            print(f"\n[ERROR] 构建失败: {e}")
            if self.config["debug_mode"]:
                import traceback
                traceback.print_exc()
            return False

    def _check_environment(self) -> bool:
        """检查构建环境

        Returns:
            环境检查是否通过
        """
        print("[CHECK] 检查构建环境...")

        try:
            env_info = self.build_helper.check_environment()
            print(f"  [OK] Python版本: {env_info.python_version.split()[0]}")
            print(f"  [OK] 平台: {env_info.platform}")
            print(f"  [OK] 可用磁盘空间: {env_info.disk_space // (1024*1024)}MB")

            # 检查必需包
            missing_packages = [pkg for pkg, installed in env_info.required_packages.items() if not installed]
            if missing_packages:
                print(f"  [ERROR] 缺少必需包: {', '.join(missing_packages)}")
                print("  请运行: pip install -r requirements.txt")
                return False

            print(f"  [OK] 所有必需包已安装")
            return True

        except Exception as e:
            print(f"  [ERROR] 环境检查失败: {e}")
            return False

    def _verify_packaging_environment(self) -> bool:
        """验证打包环境

        Returns:
            验证是否通过
        """
        print("[PACKAGING] 验证打包环境...")

        try:
            # 检查拖放功能依赖
            drag_drop_check = packaging.check_drag_drop_dependencies()

            if not drag_drop_check['tkinterdnd2_available']:
                print("  [ERROR] tkinterdnd2不可用")
                if drag_drop_check['errors']:
                    for error in drag_drop_check['errors']:
                        print(f"    错误: {error}")
                if drag_drop_check['suggestions']:
                    for suggestion in drag_drop_check['suggestions']:
                        print(f"    建议: {suggestion}")
                return False

            print(f"  [OK] tkinterdnd2可用")

            # 检查打包环境信息
            packaging_info = packaging.get_packaging_info()
            print(f"  [OK] 当前环境: {'打包环境' if packaging_info['is_packaged'] else '开发环境'}")
            print(f"  [OK] Python平台: {packaging_info['platform']}")

            # 如果在开发环境，检查PyInstaller可用性
            if not packaging_info['is_packaged']:
                try:
                    import PyInstaller
                    print(f"  [OK] PyInstaller版本: {PyInstaller.__version__}")
                except ImportError:
                    print("  [ERROR] PyInstaller未安装")
                    print("    请运行: pip install PyInstaller")
                    return False

            print("  [OK] 打包环境验证通过")
            return True

        except Exception as e:
            print(f"  [ERROR] 打包环境验证失败: {e}")
            return False

    def _handle_version(self) -> bool:
        """处理版本管理

        Returns:
            版本处理是否成功
        """
        print("[VERSION] 处理版本信息...")

        try:
            current_version = self.version_manager.get_version()
            print(f"  当前版本: {current_version}")

            if self.config["version_bump"]:
                new_version = self.version_manager.bump_version(self.config["version_bump"])
                self.version_manager.write_version(new_version)
                print(f"  [OK] 版本已更新: {current_version} -> {new_version}")

                if self.config["create_tag"]:
                    self.version_manager.create_git_tag(new_version)
                    print(f"  [OK] Git标签已创建: v{new_version}")

            return True

        except Exception as e:
            print(f"  [ERROR] 版本处理失败: {e}")
            return False

    def _clean_build_directories(self):
        """清理构建目录"""
        print("[CLEAN] 清理构建目录...")

        directories_to_clean = [self.build_dir, self.dist_dir]
        for directory in directories_to_clean:
            if directory.exists():
                try:
                    shutil.rmtree(directory)
                    print(f"  [OK] 已清理: {directory}")
                except Exception as e:
                    print(f"  [WARN] 清理警告: {directory} - {e}")

        # 清理临时文件
        temp_patterns = ["*.pyc", "*.pyo", "__pycache__", "*.log"]
        for pattern in temp_patterns:
            for file_path in self.project_root.rglob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                except Exception:
                    pass  # 忽略清理错误

        print("  [OK] 临时文件已清理")

    def _run_pyinstaller(self) -> bool:
        """运行PyInstaller构建

        Returns:
            构建是否成功
        """
        print("[BUILD] 执行PyInstaller构建...")

        # 检查spec文件
        if not self.spec_file.exists():
            print(f"  [ERROR] 找不到spec文件: {self.spec_file}")
            return False

        # 构建PyInstaller命令
        cmd = [
            sys.executable, "-m", "PyInstaller",
            str(self.spec_file)
        ]

        # 注意：当使用spec文件时，不能添加--windowed等选项
        # 这些选项应该在spec文件中配置
        if self.config["debug_mode"]:
            # debug模式通过spec文件配置
            pass

        if self.config["verbose"]:
            cmd.append("--log-level=DEBUG")

        if not self.config["upx_compress"]:
            # UPX配置通过spec文件处理
            pass

        print(f"  执行命令: {' '.join(cmd)}")

        try:
            # 运行PyInstaller
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=not self.config["verbose"],
                text=True,
                encoding='utf-8'
            )

            if result.returncode == 0:
                print("  [OK] PyInstaller构建成功")
                return True
            else:
                print(f"  [ERROR] PyInstaller构建失败 (退出码: {result.returncode})")
                if result.stdout:
                    print(f"  输出: {result.stdout}")
                if result.stderr:
                    print(f"  错误: {result.stderr}")
                return False

        except Exception as e:
            print(f"  [ERROR] 执行PyInstaller时出错: {e}")
            return False

    def _verify_build(self) -> bool:
        """验证构建结果

        Returns:
            验证是否通过
        """
        print("[VERIFY] 验证构建结果...")

        # 查找生成的exe文件
        exe_files = list(self.dist_dir.glob("*.exe"))
        if not exe_files:
            print("  [ERROR] 未找到生成的exe文件")
            return False

        exe_file = exe_files[0]  # 取第一个exe文件
        print(f"  [OK] 找到exe文件: {exe_file.name}")

        # 检查文件大小
        file_size = exe_file.stat().st_size
        print(f"  [OK] 文件大小: {file_size // (1024*1024)}MB")

        # 检查文件是否可执行（简单检查）
        if file_size < 1024 * 1024:  # 小于1MB可能有问题
            print("  [WARN] 警告: exe文件可能过小，可能存在问题")

        print("  [OK] 构建结果验证通过")
        return True

    def _generate_build_report(self):
        """生成构建报告"""
        print("[REPORT] 生成构建报告...")

        try:
            # 获取版本信息
            version_info = self.version_manager.get_build_info()

            # 获取依赖分析报告
            build_report = self.build_helper.generate_build_report()

            # 查找exe文件信息
            exe_files = list(self.dist_dir.glob("*.exe"))
            exe_info = {}
            if exe_files:
                exe_file = exe_files[0]
                exe_info = {
                    "name": exe_file.name,
                    "size": exe_file.stat().st_size,
                    "path": str(exe_file)
                }

            # 获取打包环境信息
            packaging_info = packaging.get_packaging_info()

            # 生成完整报告
            report = {
                "build_info": {
                    "build_time": datetime.now().isoformat(),
                    "build_config": self.config,
                    "python_version": sys.version,
                    "platform": sys.platform
                },
                "version_info": version_info,
                "exe_info": exe_info,
                "environment_report": build_report.get("environment", {}),
                "dependencies_report": build_report.get("dependencies", []),
                "issues_report": build_report.get("issues", {}),
                "packaging_report": {
                    "packaging_info": packaging_info,
                    "drag_drop_check": packaging_info.get("drag_drop_check", {})
                }
            }

            # 保存报告
            report_file = self.project_root / "build_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)

            print(f"  [OK] 构建报告已保存: {report_file}")

        except Exception as e:
            print(f"  [WARN] 生成构建报告时出错: {e}")


def setup_arg_parser() -> argparse.ArgumentParser:
    """设置命令行参数解析器

    Returns:
        配置好的参数解析器
    """
    parser = argparse.ArgumentParser(
        description="pyw2md自动化构建脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s                    # 默认构建
  %(prog)s --clean            # 清理后构建
  %(prog)s --version patch    # 递增补丁版本
  %(prog)s --version minor    # 递增次版本
  %(prog)s --version major    # 递增主版本
  %(prog)s --debug            # 调试模式构建
        """
    )

    parser.add_argument(
        "--clean", "-c",
        action="store_true",
        help="构建前清理构建目录"
    )

    parser.add_argument(
        "--version", "-v",
        choices=["major", "minor", "patch"],
        help="递增版本号"
    )

    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="启用调试模式"
    )

    parser.add_argument(
        "--verbose", "-V",
        action="store_true",
        help="详细输出"
    )

    parser.add_argument(
        "--no-tag",
        action="store_true",
        help="不创建Git标签"
    )

    parser.add_argument(
        "--no-upx",
        action="store_true",
        help="不使用UPX压缩"
    )

    return parser


def main():
    """主函数"""
    parser = setup_arg_parser()
    args = parser.parse_args()

    # 创建构建器
    builder = Pyw2mdBuilder(project_root)

    # 配置构建选项
    builder.config.update({
        "clean_first": args.clean,
        "version_bump": args.version,
        "debug_mode": args.debug,
        "verbose": args.verbose,
        "create_tag": not args.no_tag,
        "upx_compress": not args.no_upx
    })

    # 执行构建
    success = builder.build()

    # 退出程序
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()