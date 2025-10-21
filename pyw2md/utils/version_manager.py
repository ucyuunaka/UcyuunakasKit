"""
版本管理工具

功能说明：
- 提供语义化版本号管理
- 支持版本号的读取、更新和写入
- 支持Git标签集成
- 提供版本比较和验证功能

设计思路：
- 遵循语义化版本规范 (MAJOR.MINOR.PATCH)
- 支持从文件或代码中读取版本信息
- 提供灵活的版本更新策略
- 集成Git工作流

使用示例：
    vm = VersionManager()
    current = vm.get_version()
    new_version = vm.bump_version('minor')
    vm.write_version(new_version)
"""

import os
import re
import subprocess
from typing import Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Version:
    """版本信息数据类"""
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other: 'Version') -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __eq__(self, other: 'Version') -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)


class VersionManager:
    """版本管理器

    负责管理项目的版本号，包括读取、更新和写入版本信息。
    支持从多个源读取版本信息，并提供灵活的更新策略。
    """

    def __init__(self, project_root: Optional[str] = None):
        """初始化版本管理器

        Args:
            project_root: 项目根目录，默认为当前文件所在的项目根目录
        """
        if project_root is None:
            self.project_root = Path(__file__).parent.parent
        else:
            self.project_root = Path(project_root)

        self.version_file = self.project_root / "VERSION"
        self.init_file = self.project_root / "core" / "__init__.py"

    def get_version(self) -> Version:
        """获取当前版本号

        按优先级从以下位置读取：
        1. VERSION文件
        2. core/__init__.py中的__version__
        3. 默认版本 1.0.0

        Returns:
            当前版本号

        Raises:
            ValueError: 版本号格式无效
        """
        # 尝试从VERSION文件读取
        if self.version_file.exists():
            try:
                content = self.version_file.read_text().strip()
                return self._parse_version(content)
            except Exception as e:
                print(f"警告: 无法读取VERSION文件: {e}")

        # 尝试从__init__.py读取
        if self.init_file.exists():
            try:
                content = self.init_file.read_text()
                match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return self._parse_version(match.group(1))
            except Exception as e:
                print(f"警告: 无法从__init__.py读取版本: {e}")

        # 返回默认版本
        return Version(1, 0, 0)

    def write_version(self, version: Version, target: str = "both") -> None:
        """写入版本号

        Args:
            version: 要写入的版本号
            target: 写入目标 ("file", "init", "both")
        """
        version_str = str(version)

        if target in ("file", "both"):
            # 写入VERSION文件
            self.version_file.write_text(version_str + "\n")
            print(f"版本号已写入VERSION文件: {version_str}")

        if target in ("init", "both"):
            # 写入__init__.py
            if self.init_file.exists():
                try:
                    content = self.init_file.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    # 如果UTF-8解码失败，尝试其他编码
                    try:
                        content = self.init_file.read_text(encoding='gbk')
                    except UnicodeDecodeError:
                        content = self.init_file.read_bytes().decode('utf-8', errors='ignore')

                # 查找并替换__version__
                pattern = r'__version__\s*=\s*["\'][^"\']+["\']'
                replacement = f'__version__ = "{version_str}"'

                if re.search(pattern, content):
                    new_content = re.sub(pattern, replacement, content)
                    self.init_file.write_text(new_content, encoding='utf-8')
                    print(f"版本号已写入__init__.py: {version_str}")
                else:
                    # 在文件开头添加版本信息
                    new_content = f'__version__ = "{version_str}"\n\n{content}'
                    self.init_file.write_text(new_content, encoding='utf-8')
                    print(f"版本信息已添加到__init__.py: {version_str}")
            else:
                print(f"警告: {self.init_file} 不存在，跳过写入")

    def bump_version(self, bump_type: str = "patch") -> Version:
        """递增版本号

        Args:
            bump_type: 递增类型 ("major", "minor", "patch")

        Returns:
            新的版本号

        Raises:
            ValueError: 无效的递增类型
        """
        current = self.get_version()

        if bump_type == "major":
            new_version = Version(current.major + 1, 0, 0)
        elif bump_type == "minor":
            new_version = Version(current.major, current.minor + 1, 0)
        elif bump_type == "patch":
            new_version = Version(current.major, current.minor, current.patch + 1)
        else:
            raise ValueError(f"无效的递增类型: {bump_type}")

        print(f"版本号递增: {current} -> {new_version}")
        return new_version

    def create_git_tag(self, version: Version, message: Optional[str] = None) -> bool:
        """创建Git标签

        Args:
            version: 版本号
            message: 标签消息，默认使用版本号

        Returns:
            是否成功创建标签
        """
        try:
            # 检查是否在Git仓库中
            git_dir = self.project_root / ".git"
            if not git_dir.exists():
                print("警告: 当前目录不是Git仓库，跳过标签创建")
                return False

            tag_name = f"v{version}"
            if message is None:
                message = f"Release version {version}"

            # 创建标签
            result = subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", message],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"Git标签已创建: {tag_name}")
                return True
            else:
                print(f"创建Git标签失败: {result.stderr}")
                return False

        except Exception as e:
            print(f"创建Git标签时出错: {e}")
            return False

    def get_build_info(self) -> dict:
        """获取构建信息

        Returns:
            包含版本、构建日期、Git提交信息的字典
        """
        from datetime import datetime

        build_info = {
            "version": str(self.get_version()),
            "build_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "git_commit": self._get_git_commit(),
            "git_branch": self._get_git_branch()
        }

        return build_info

    def update_version_with_info(self, bump_type: str = "patch",
                                create_tag: bool = True,
                                write_to_file: bool = True) -> Version:
        """更新版本号并更新相关文件

        Args:
            bump_type: 版本递增类型
            create_tag: 是否创建Git标签
            write_to_file: 是否写入文件

        Returns:
            新的版本号
        """
        # 递增版本
        new_version = self.bump_version(bump_type)

        # 写入文件
        if write_to_file:
            self.write_version(new_version)

        # 创建Git标签
        if create_tag:
            self.create_git_tag(new_version)

        return new_version

    def _parse_version(self, version_str: str) -> Version:
        """解析版本字符串

        Args:
            version_str: 版本字符串

        Returns:
            解析后的版本对象

        Raises:
            ValueError: 版本格式无效
        """
        # 清理版本字符串
        version_str = version_str.strip().lstrip('vV')

        # 使用正则表达式解析版本号
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)', version_str)
        if match:
            return Version(
                major=int(match.group(1)),
                minor=int(match.group(2)),
                patch=int(match.group(3))
            )
        else:
            raise ValueError(f"无效的版本格式: {version_str}")

    def _get_git_commit(self) -> Optional[str]:
        """获取当前Git提交哈希

        Returns:
            提交哈希，如果不在Git仓库中则返回None
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def _get_git_branch(self) -> Optional[str]:
        """获取当前Git分支

        Returns:
            分支名，如果不在Git仓库中则返回None
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None


# 便捷函数
def get_current_version() -> str:
    """获取当前版本号的便捷函数"""
    vm = VersionManager()
    return str(vm.get_version())


def bump_and_save(bump_type: str = "patch") -> str:
    """递增并保存版本号的便捷函数"""
    vm = VersionManager()
    new_version = vm.update_version_with_info(bump_type)
    return str(new_version)