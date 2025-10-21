"""
构建辅助工具

功能说明：
- 提供构建过程中的环境检查
- 分析项目依赖关系
- 收集资源文件信息
- 诊断构建问题

设计思路：
- 模块化设计，每个功能独立
- 提供详细的诊断信息
- 支持自动化和手动检查
- 集成现有的项目工具

使用示例：
    helper = BuildHelper()
    env_info = helper.check_environment()
    deps = helper.analyze_dependencies()
    resources = helper.collect_resources()
"""

import os
import sys
import ast
import json
import shutil
import subprocess
from typing import List, Dict, Set, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass


@dataclass
class DependencyInfo:
    """依赖信息数据类"""
    name: str
    is_standard_library: bool
    is_third_party: bool
    is_local: bool
    module_path: Optional[str]
    import_locations: List[str]


@dataclass
class ResourceInfo:
    """资源文件信息数据类"""
    path: str
    type: str  # config, data, static, etc.
    size: int
    description: str


@dataclass
class EnvironmentInfo:
    """环境信息数据类"""
    python_version: str
    python_executable: str
    platform: str
    architecture: str
    required_packages: Dict[str, bool]
    disk_space: int
    memory: int


class BuildHelper:
    """构建辅助工具

    提供构建过程中所需的各种辅助功能，包括环境检查、
    依赖分析、资源收集等。
    """

    def __init__(self, project_root: Optional[str] = None):
        """初始化构建辅助工具

        Args:
            project_root: 项目根目录，默认为当前文件所在的项目根目录
        """
        if project_root is None:
            self.project_root = Path(__file__).parent.parent
        else:
            self.project_root = Path(project_root)

        self.standard_libs = self._get_standard_library_modules()
        self.third_party_cache: Optional[Set[str]] = None

    def check_environment(self) -> EnvironmentInfo:
        """检查构建环境

        Returns:
            环境信息对象

        Raises:
            EnvironmentError: 环境不满足要求时抛出
        """
        import platform
        import psutil

        # 基本系统信息
        env_info = EnvironmentInfo(
            python_version=sys.version,
            python_executable=sys.executable,
            platform=platform.platform(),
            architecture=platform.architecture()[0],
            required_packages=self._check_required_packages(),
            disk_space=self._get_disk_space(),
            memory=self._get_memory_info()
        )

        # 检查Python版本
        if sys.version_info < (3, 8):
            raise EnvironmentError(f"Python版本过低: {sys.version_info}，需要3.8+")

        # 检查磁盘空间 (至少需要500MB)
        if env_info.disk_space < 500 * 1024 * 1024:
            raise EnvironmentError(f"磁盘空间不足: {env_info.disk_space // (1024*1024)}MB，需要至少500MB")

        return env_info

    def analyze_dependencies(self) -> List[DependencyInfo]:
        """分析项目依赖

        Returns:
            依赖信息列表
        """
        dependencies = []

        # 查找所有Python文件
        python_files = list(self.project_root.rglob("*.py"))

        # 排除测试文件和构建文件
        python_files = [f for f in python_files
                       if not any(part.startswith(('.', '__pycache__', 'test', 'build', 'dist'))
                                 for part in f.parts)]

        for py_file in python_files:
            try:
                file_deps = self._analyze_file_dependencies(py_file)
                dependencies.extend(file_deps)
            except Exception as e:
                print(f"警告: 分析文件 {py_file} 时出错: {e}")

        # 去重并合并信息
        unique_deps = self._merge_dependencies(dependencies)
        return unique_deps

    def collect_resources(self) -> List[ResourceInfo]:
        """收集资源文件

        Returns:
            资源文件信息列表
        """
        resources = []

        # 配置文件
        config_patterns = [
            "config.json",
            "*.ini",
            "*.cfg",
            "*.yaml",
            "*.yml",
            "config/*.json"
        ]

        # 静态资源
        static_patterns = [
            "*.ico",
            "*.png",
            "*.jpg",
            "*.jpeg",
            "*.gif",
            "*.svg",
            "*.ttf",
            "*.otf"
        ]

        # 数据文件
        data_patterns = [
            "*.txt",
            "*.md",
            "*.json",
            "*.csv"
        ]

        all_patterns = config_patterns + static_patterns + data_patterns

        for pattern in all_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file() and not self._should_exclude_file(file_path):
                    resource_info = self._create_resource_info(file_path, pattern)
                    resources.append(resource_info)

        return resources

    def diagnose_build_issues(self) -> Dict[str, List[str]]:
        """诊断潜在的构建问题

        Returns:
            问题分类字典，键为问题类型，值为问题列表
        """
        issues = {
            "missing_dependencies": [],
            "missing_resources": [],
            "path_issues": [],
            "encoding_issues": [],
            "permission_issues": []
        }

        # 检查依赖
        try:
            dependencies = self.analyze_dependencies()
            for dep in dependencies:
                if dep.is_third_party and not dep.module_path:
                    issues["missing_dependencies"].append(dep.name)
        except Exception as e:
            issues["missing_dependencies"].append(f"依赖分析失败: {e}")

        # 检查路径问题
        issues["path_issues"] = self._check_path_issues()

        # 检查编码问题
        issues["encoding_issues"] = self._check_encoding_issues()

        # 检查权限问题
        issues["permission_issues"] = self._check_permission_issues()

        return issues

    def generate_build_report(self) -> Dict[str, Any]:
        """生成构建报告

        Returns:
            包含环境、依赖、资源等信息的完整报告
        """
        try:
            environment = self.check_environment()
        except Exception as e:
            environment = {"error": str(e)}

        try:
            dependencies = self.analyze_dependencies()
        except Exception as e:
            dependencies = {"error": str(e)}

        try:
            resources = self.collect_resources()
        except Exception as e:
            resources = {"error": str(e)}

        try:
            issues = self.diagnose_build_issues()
        except Exception as e:
            issues = {"error": str(e)}

        report = {
            "project_root": str(self.project_root),
            "environment": environment,
            "dependencies": dependencies,
            "resources": resources,
            "issues": issues,
            "generated_at": str(Path(__file__).stat().st_mtime)
        }

        return report

    def _get_standard_library_modules(self) -> Set[str]:
        """获取标准库模块列表"""
        try:
            import stdlib_list
            # 使用stdlib_list库获取标准库列表
            version = f"{sys.version_info.major}.{sys.version_info.minor}"
            return set(stdlib_list.stdlib_list(version))
        except ImportError:
            # 如果没有stdlib_list，使用硬编码的基本列表
            return set([
                'os', 'sys', 'json', 'time', 'datetime', 'threading',
                'pathlib', 'subprocess', 'logging', 'argparse', 'shutil',
                'tempfile', 'collections', 'itertools', 'functools',
                'operator', 're', 'math', 'random', 'string',
                'typing', 'dataclasses', 'enum', 'abc', 'contextlib',
                'ast', 'io', 'importlib', 'inspect', 'textwrap',
                'unittest', 'hashlib', 'base64', 'urllib', 'http',
                'socket', 'email', 'xml', 'sqlite3', 'csv',
                'configparser', 'pickle', 'struct', 'array',
                'heapq', 'bisect', 'queue', 'weakref', 'copy',
                'pprint', 'repr', 'stringprep', 'codecs',
                'encodings', 'codecs', 'unicodedata'
            ])

    def _check_required_packages(self) -> Dict[str, bool]:
        """检查必需的包是否已安装"""
        required_packages = ['customtkinter', 'watchdog', 'PyInstaller']
        installed = {}

        for package in required_packages:
            try:
                __import__(package)
                installed[package] = True
            except ImportError:
                installed[package] = False

        return installed

    def _get_disk_space(self) -> int:
        """获取可用磁盘空间（字节）"""
        try:
            # 使用shutil.disk_usage，这是Python标准库
            stat = shutil.disk_usage(self.project_root)
            return stat.free
        except Exception as e:
            # 如果获取失败，返回一个合理的默认值
            print(f"警告: 无法获取磁盘空间信息: {e}")
            return 1024 * 1024 * 1024  # 1GB默认值

    def _get_memory_info(self) -> int:
        """获取内存信息（字节）"""
        try:
            import psutil
            return psutil.virtual_memory().total
        except ImportError:
            return 0  # 无法获取内存信息

    def _analyze_file_dependencies(self, file_path: Path) -> List[DependencyInfo]:
        """分析单个文件的依赖"""
        dependencies = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dep_info = self._create_dependency_info(
                            alias.name, str(file_path), node.lineno
                        )
                        dependencies.append(dep_info)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dep_info = self._create_dependency_info(
                            node.module, str(file_path), node.lineno
                        )
                        dependencies.append(dep_info)

        except Exception as e:
            print(f"警告: 解析文件 {file_path} 时出错: {e}")

        return dependencies

    def _create_dependency_info(self, module_name: str,
                               file_path: str, line_no: int) -> DependencyInfo:
        """创建依赖信息对象"""
        is_standard = module_name in self.standard_libs
        is_local = module_name.startswith('.')
        is_third_party = not is_standard and not is_local

        # 尝试找到模块路径
        module_path = None
        try:
            if not is_standard:
                module = __import__(module_name, fromlist=[''])
                if hasattr(module, '__file__'):
                    module_path = module.__file__
        except ImportError:
            pass

        return DependencyInfo(
            name=module_name,
            is_standard_library=is_standard,
            is_third_party=is_third_party,
            is_local=is_local,
            module_path=module_path,
            import_locations=[f"{file_path}:{line_no}"]
        )

    def _merge_dependencies(self, dependencies: List[DependencyInfo]) -> List[DependencyInfo]:
        """合并重复的依赖信息"""
        merged = {}

        for dep in dependencies:
            if dep.name not in merged:
                merged[dep.name] = dep
            else:
                # 合并导入位置
                existing = merged[dep.name]
                existing.import_locations.extend(dep.import_locations)
                existing.import_locations = list(set(existing.import_locations))

        return list(merged.values())

    def _should_exclude_file(self, file_path: Path) -> bool:
        """判断文件是否应该被排除"""
        exclude_patterns = [
            '__pycache__',
            '.git',
            'node_modules',
            '.pytest_cache',
            'build',
            'dist',
            '*.pyc',
            '.DS_Store',
            'Thumbs.db'
        ]

        path_str = str(file_path)
        return any(pattern in path_str for pattern in exclude_patterns)

    def _create_resource_info(self, file_path: Path, pattern: str) -> ResourceInfo:
        """创建资源文件信息对象"""
        # 确定资源类型
        if pattern.startswith("config"):
            resource_type = "config"
        elif pattern.endswith(('.ico', '.png', '.jpg', '.jpeg', '.gif', '.svg')):
            resource_type = "image"
        elif pattern.endswith(('.ttf', '.otf')):
            resource_type = "font"
        else:
            resource_type = "data"

        # 获取文件大小
        try:
            size = file_path.stat().st_size
        except OSError:
            size = 0

        description = f"{resource_type.title()} file: {file_path.name}"

        return ResourceInfo(
            path=str(file_path.relative_to(self.project_root)),
            type=resource_type,
            size=size,
            description=description
        )

    def _check_path_issues(self) -> List[str]:
        """检查路径相关问题"""
        issues = []

        # 检查路径长度
        for file_path in self.project_root.rglob("*"):
            if len(str(file_path)) > 260:  # Windows路径长度限制
                issues.append(f"路径过长: {file_path}")

        # 检查特殊字符
        for file_path in self.project_root.rglob("*"):
            if any(char in str(file_path) for char in ['<', '>', '|', '?', '*']):
                issues.append(f"路径包含特殊字符: {file_path}")

        return issues

    def _check_encoding_issues(self) -> List[str]:
        """检查编码问题"""
        issues = []

        for py_file in self.project_root.rglob("*.py"):
            if self._should_exclude_file(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    f.read()
            except UnicodeDecodeError:
                issues.append(f"文件编码问题: {py_file}")
            except Exception:
                pass  # 忽略其他错误

        return issues

    def _check_permission_issues(self) -> List[str]:
        """检查权限问题"""
        issues = []

        # 检查读取权限
        test_file = self.project_root / "build_permission_test.txt"
        try:
            test_file.write_text("test")
            test_file.unlink()
        except PermissionError:
            issues.append("没有写入权限")
        except Exception:
            pass

        return issues