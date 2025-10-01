"""
Code2Markdown 核心逻辑模块
包含文件处理、语言识别、格式化等核心功能
"""

import os
import time

# 支持的编程语言
SUPPORTED_EXTENSIONS = {
    'Python': ['.py', '.pyw'],
    'JavaScript': ['.js', '.jsx', '.ts', '.tsx'],
    'Java': ['.java'],
    'C/C++': ['.c', '.cpp', '.h', '.hpp'],
    'C#': ['.cs'],
    'PHP': ['.php'],
    'Ruby': ['.rb'],
    'Go': ['.go'],
    'Rust': ['.rs'],
    'HTML': ['.html', '.htm'],
    'CSS': ['.css', '.scss', '.sass', '.less'],
    'SQL': ['.sql'],
    'Shell': ['.sh', '.bash', '.zsh'],
    'YAML': ['.yml', '.yaml'],
    'JSON': ['.json'],
    'XML': ['.xml'],
    'Markdown': ['.md'],
    'Text': ['.txt']
}

# Markdown 模板
TEMPLATES = {
    "默认": "# {relative_path}\n```{language}\n{content}\n```\n\n",
    "带注释": """# 文件: {relative_path}

语言: {language}
大小: {size} 字节
最后修改: {mtime}

```{language}
{content}
```
""",
    "GitHub风格": """## {basename}

```{language}
{content}
```
<details>
<summary>文件信息</summary>

路径: {relative_path}
语言: {language}
大小: {size} 字节
</details>
""",
    "简洁": """```{language}
// {relative_path}
{content}
```

"""
}

def get_language_from_extension(file_path):
    """根据文件扩展名获取编程语言"""
    _, ext = os.path.splitext(file_path.lower())
    for language, extensions in SUPPORTED_EXTENSIONS.items():
        if ext in extensions:
            return language
    return "Text"

def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f}KB"
    else:
        return f"{size_bytes/(1024*1024):.1f}MB"

def get_all_supported_files_in_folder(folder_path):
    """递归获取文件夹中所有支持的代码文件"""
    supported_files = []
    all_extensions = [ext for exts in SUPPORTED_EXTENSIONS.values() for ext in exts]

    for root_dir, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root_dir, file)
            _, ext = os.path.splitext(file_path.lower())
            if ext in all_extensions:
                supported_files.append(file_path)

    return supported_files

def format_file_content(file_path, template_name):
    """使用指定模板格式化文件内容"""
    try:
        current_dir = os.getcwd()
        basename = os.path.basename(file_path)
        language = get_language_from_extension(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        file_size = os.path.getsize(file_path)
        mtime = os.path.getmtime(file_path)

        try:
            relative_path = os.path.relpath(file_path, current_dir)
        except ValueError:
            relative_path = file_path

        template = TEMPLATES[template_name]
        formatted = template.format(
            relative_path=relative_path,
            basename=basename,
            language=language,
            size=file_size,
            mtime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime)),
            content=content
        )

        return formatted

    except Exception as e:
        return f"<!-- 错误处理文件 {file_path}: {str(e)} -->\n"
