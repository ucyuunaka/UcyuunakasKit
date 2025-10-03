"""
Markdown 转换核心模块
"""

import os
import time
from typing import Callable, Optional
from core.file_handler import FileInfo

# Markdown 模板
TEMPLATES = {
    "默认": """# {relative_path}

```{language}
{content}
```

---

""",
    
    "详细信息": """## {basename}

**路径:** `{relative_path}`
**语言:** {language}
**大小:** {size}
**修改时间:** {mtime}

```{language}
{content}
```

---

""",
    
    "GitHub 风格": """## {basename}

```{language}
{content}
```

<details>
<summary>文件信息</summary>

- **完整路径:** `{relative_path}`
- **编程语言:** {language}
- **文件大小:** {size}
- **最后修改:** {mtime}

</details>

---

""",
    
    "简洁模式": """```{language}
// {relative_path}
{content}
```

""",
    
    "带目录": """### {relative_path}

<details open>
<summary>点击展开/折叠</summary>

```{language}
{content}
```

</details>

""",

    "专业文档": """## {basename}

> 路径: `{relative_path}`
> 语言: **{language}**
> 大小: {size}

```{language}
{content}
```

**最后修改:** {mtime}

---

"""
}

class Converter:
    """Markdown 转换器"""
    
    def __init__(self, template: str = "默认"):
        self.template = template
        self.base_path = os.getcwd()
    
    def set_template(self, template: str):
        """设置模板"""
        if template in TEMPLATES:
            self.template = template
    
    def set_base_path(self, path: str):
        """设置基准路径（用于计算相对路径）"""
        self.base_path = path
    
    def convert_file(self, file_info: FileInfo) -> str:
        """转换单个文件"""
        try:
            # 读取文件内容
            with open(file_info.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 准备模板变量
            basename = os.path.basename(file_info.path)
            
            try:
                relative_path = os.path.relpath(file_info.path, self.base_path)
            except ValueError:
                relative_path = file_info.path
            
            mtime = time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(os.path.getmtime(file_info.path))
            )
            
            from core.file_handler import format_size
            size = format_size(file_info.size)
            
            # 应用模板
            template = TEMPLATES.get(self.template, TEMPLATES["默认"])
            
            return template.format(
                basename=basename,
                relative_path=relative_path,
                language=file_info.language.lower(),
                size=size,
                mtime=mtime,
                content=content
            )
            
        except Exception as e:
            return f"<!-- ❌ 错误: 无法处理文件 {file_info.path}: {str(e)} -->\n\n"
    
    def convert_files(self, 
                     files: list[FileInfo],
                     output_path: str,
                     progress_callback: Optional[Callable[[int, int, str], None]] = None) -> dict:
        """
        批量转换文件
        
        Args:
            files: 文件列表
            output_path: 输出文件路径
            progress_callback: 进度回调函数 (current, total, filename)
        
        Returns:
            dict: 转换结果统计
        """
        total = len(files)
        success = 0
        errors = []
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # 写入文档头部
                f.write(self._generate_header(files))
                
                # 转换每个文件
                for i, file_info in enumerate(files, 1):
                    try:
                        # 回调进度
                        if progress_callback:
                            progress_callback(i, total, file_info.name)
                        
                        # 转换并写入
                        markdown = self.convert_file(file_info)
                        f.write(markdown)
                        success += 1
                        
                    except Exception as e:
                        errors.append({
                            'file': file_info.path,
                            'error': str(e)
                        })
                
                # 写入文档尾部
                f.write(self._generate_footer(success, total))
        
        except Exception as e:
            return {
                'success': False,
                'message': f'写入输出文件失败: {str(e)}',
                'converted': 0,
                'total': total,
                'errors': errors
            }
        
        return {
            'success': True,
            'message': f'成功转换 {success}/{total} 个文件',
            'converted': success,
            'total': total,
            'errors': errors
        }
    
    def _generate_header(self, files: list[FileInfo]) -> str:
        """生成文档头部"""
        from core.file_handler import format_size

        total_size = sum(f.size for f in files)
        languages = set(f.language for f in files)

        header = f"""# 代码转Markdown文档

**生成时间:** {time.strftime("%Y-%m-%d %H:%M:%S")}
**文件数量:** {len(files)}
**总大小:** {format_size(total_size)}
**编程语言:** {', '.join(sorted(languages))}
**使用模板:** {self.template}

---

"""
        return header
    
    def _generate_footer(self, success: int, total: int) -> str:
        """生成文档尾部"""
        footer = f"""

---

## 转换统计

- 成功转换: **{success}** 个文件
- 总计处理: **{total}** 个文件
- 完成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}

---

文档生成完成
"""
        return footer

def get_template_names() -> list[str]:
    """获取所有模板名称"""
    return list(TEMPLATES.keys())

def preview_template(template_name: str) -> str:
    """预览模板内容"""
    return TEMPLATES.get(template_name, TEMPLATES["默认"])