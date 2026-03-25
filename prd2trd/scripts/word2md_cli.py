# -*- coding: utf-8 -*-
"""
Word2MD CLI - Word to Markdown Command Line Converter
命令行版本的 Word 转 Markdown 工具

Usage:
    python word2md_cli.py input.docx output.md
    Word2MD_CLI.exe input.docx output.md
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Tuple, List


def ensure_dependencies():
    """确保所有必要的依赖包都已安装"""
    required_packages = [
        ("docx", "python-docx"),
        ("mammoth", "mammoth"),
        ("pypandoc", "pypandoc"),
        ("PIL", "Pillow"),
        ("lxml", "lxml")
    ]

    missing_packages = []
    for module_name, pip_name in required_packages:
        try:
            __import__(module_name)
        except ImportError:
            missing_packages.append(pip_name)

    if missing_packages:
        print(f"正在安装缺失的依赖包: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)
            print("依赖包安装完成")
        except subprocess.CalledProcessError as e:
            print(f"依赖包安装失败: {e}")
            return False
    return True


# 确保依赖包
if not ensure_dependencies():
    sys.exit(1)

# 导入依赖包
from docx import Document
import mammoth
from PIL import Image
import io
from lxml import etree
import pypandoc
import re
import html


class EnhancedWordToMarkdownConverter:
    """Word 转 Markdown 转换器"""

    def __init__(self):
        self.output_dir = None
        self.image_dir = None
        self.image_counter = 0
        self.pandoc_available = self._check_pandoc()

    def _check_pandoc(self) -> bool:
        """检查Pandoc是否可用"""
        try:
            pypandoc.get_pandoc_version()
            return True
        except OSError:
            try:
                pypandoc.download_pandoc()
                return True
            except Exception:
                return False

    def extract_images_from_docx(self, docx_path: str, output_folder: str) -> List[str]:
        """从docx文件中提取图片"""
        doc = Document(docx_path)
        self.image_counter = 0
        image_paths = []

        images_dir = ""
        images_dir.mkdir(exist_ok=True, parents=True)

        for rel in doc.part.rels.values():
            if "image" in rel.reltype:
                try:
                    image_data = rel.target_part.blob
                    ext = rel.target_part.partname.split('.')[-1].lower()
                    if ext not in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp']:
                        ext = 'png'

                    image_name = f"image_{self.image_counter:03d}.{ext}"
                    image_path = images_dir / image_name

                    with open(image_path, 'wb') as f:
                        f.write(image_data)

                    image_paths.append(str(image_path))
                    self.image_counter += 1
                except Exception as e:
                    print(f"提取图片时出错: {e}")
                    continue

        return image_paths

    def process_math_equations(self, content: str) -> str:
        """处理数学公式，将常见符号转换为LaTeX格式"""
        math_symbols = {
            'α': r'\alpha', 'β': r'\beta', 'γ': r'\gamma', 'δ': r'\delta',
            'ε': r'\varepsilon', 'θ': r'\theta', 'λ': r'\lambda', 'μ': r'\mu',
            'π': r'\pi', 'σ': r'\sigma', 'φ': r'\varphi', 'ω': r'\omega',
            '∑': r'\sum', '∫': r'\int', '∞': r'\infty', '∂': r'\partial',
            '±': r'\pm', '×': r'\times', '÷': r'\div', '≤': r'\leq',
            '≥': r'\geq', '≠': r'\neq', '≈': r'\approx', '√': r'\sqrt',
            '²': r'^2', '³': r'^3', '¹': r'^1', '₀': r'_0', '₁': r'_1',
            '₂': r'_2', '₃': r'_3', '₄': r'_4'
        }

        for symbol, latex in math_symbols.items():
            if symbol in content:
                pattern = re.compile(re.escape(symbol))
                matches = list(pattern.finditer(content))

                for match in reversed(matches):
                    start, end = match.span()
                    before = content[:start]
                    after = content[end:]

                    in_math = (before.count('$') % 2 == 1)

                    if not in_math:
                        replacement = f"${latex}$"
                    else:
                        replacement = latex

                    content = content[:start] + replacement + content[end:]

        return content

    def convert_with_pandoc(self, docx_path: str, output_path: str) -> Tuple[str, List[str]]:
        """使用Pandoc进行转换"""
        if not self.pandoc_available:
            raise RuntimeError("Pandoc不可用")

        self.output_dir = Path(output_path).parent
        base_name = Path(docx_path).stem
        media_dir = self.output_dir / f"assets"

        extra_args = [
            "--wrap=none",
            f"--extract-media={media_dir}",
            "--standalone"
        ]

        markdown_content = pypandoc.convert_file(
            docx_path,
            'gfm+tex_math_dollars+pipe_tables',
            extra_args=extra_args
        )

        markdown_content = self.process_math_equations(markdown_content)

        # 处理 Pandoc 提取的媒体文件路径
        # Pandoc 会将图片提取到 media_dir/media/ 目录
        pandoc_media_dir = media_dir
        if pandoc_media_dir.exists():
            # 将图片移动到 media_dir 根目录
            for img_file in pandoc_media_dir.iterdir():
                target = media_dir / img_file.name
                if not target.exists():
                    img_file.rename(target)
            # 删除空的 media 子目录
            try:
                pandoc_media_dir.rmdir()
            except:
                pass

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return markdown_content, []

    def convert_with_mammoth(self, docx_path: str, output_path: str) -> Tuple[str, List[str]]:
        """使用Mammoth进行转换"""
        self.output_dir = Path(output_path).parent
        self.image_dir = self.output_dir / f"{Path(output_path).stem}"
        self.image_dir.mkdir(exist_ok=True, parents=True)

        image_paths = self.extract_images_from_docx(docx_path, self.image_dir)

        def convert_image(image):
            try:
                with image.open() as image_bytes:
                    image_data = image_bytes.read()

                ext = 'png'
                if hasattr(image, 'content_type'):
                    if 'jpeg' in image.content_type:
                        ext = 'jpg'
                    elif 'png' in image.content_type:
                        ext = 'png'
                    elif 'gif' in image.content_type:
                        ext = 'gif'

                image_name = f"image_{self.image_counter:03d}.{ext}"
                image_path = self.image_dir / image_name

                with open(image_path, 'wb') as f:
                    f.write(image_data)

                self.image_counter += 1

                return {"src": f"{Path(output_path).stem}/{image_name}"}
            except Exception as e:
                print(f"处理图片时出错: {e}")
                return {"src": ""}

        with open(docx_path, "rb") as docx_file:
            result = mammoth.convert_to_html(
                docx_file,
                convert_image=mammoth.images.img_element(convert_image)
            )

        html_content = result.value
        html_content = self.process_math_equations(html_content)
        markdown_content = self.html_to_markdown(html_content)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return markdown_content, result.messages

    def html_to_markdown(self, html_content: str) -> str:
        """将HTML转换为Markdown"""
        # 转换标题
        for i in range(6, 0, -1):
            html_content = re.sub(
                f'<h{i}[^>]*>(.*?)</h{i}>',
                lambda m: f"{'#' * i} {m.group(1).strip()}\n\n",
                html_content,
                flags=re.DOTALL | re.IGNORECASE
            )

        # 转换段落
        html_content = re.sub(
            r'<p[^>]*>(.*?)</p>',
            lambda m: f"{m.group(1).strip()}\n\n" if m.group(1).strip() else "",
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # 转换格式
        html_content = re.sub(r'<(b|strong)[^>]*>(.*?)</\1>', r'**\2**', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'<(i|em)[^>]*>(.*?)</\1>', r'*\2*', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', html_content, flags=re.IGNORECASE | re.DOTALL)

        # 转换图片
        html_content = re.sub(
            r'<img[^>]*src="([^"]*)"[^>]*(?:alt="([^"]*)")?[^>]*>',
            lambda m: f'![{m.group(2) if m.group(2) else "图片"}]({m.group(1)})\n\n',
            html_content,
            flags=re.IGNORECASE
        )

        # 转换列表
        def convert_ul(match):
            items = re.findall(r'<li[^>]*>(.*?)</li>', match.group(1), re.DOTALL | re.IGNORECASE)
            result = []
            for item in items:
                item_text = re.sub(r'<[^>]+>', '', item.strip())
                if item_text:
                    result.append(f"- {item_text}")
            return '\n'.join(result) + '\n\n' if result else ''

        html_content = re.sub(r'<ul[^>]*>(.*?)</ul>', convert_ul, html_content, flags=re.DOTALL | re.IGNORECASE)

        def convert_ol(match):
            items = re.findall(r'<li[^>]*>(.*?)</li>', match.group(1), re.DOTALL | re.IGNORECASE)
            result = []
            for i, item in enumerate(items, 1):
                item_text = re.sub(r'<[^>]+>', '', item.strip())
                if item_text:
                    result.append(f"{i}. {item_text}")
            return '\n'.join(result) + '\n\n' if result else ''

        html_content = re.sub(r'<ol[^>]*>(.*?)</ol>', convert_ol, html_content, flags=re.DOTALL | re.IGNORECASE)

        # 转换表格
        def convert_table(match):
            table_html = match.group(0)
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL | re.IGNORECASE)

            if not rows:
                return ''

            markdown_table = []
            for i, row in enumerate(rows):
                cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, re.DOTALL | re.IGNORECASE)
                processed_cells = []

                for cell in cells:
                    cell_text = re.sub(r'<[^>]+>', ' ', cell.strip())
                    cell_text = re.sub(r'\s+', ' ', cell_text).strip()
                    cell_text = cell_text.replace('|', '\\|')
                    processed_cells.append(cell_text)

                if processed_cells:
                    markdown_table.append('| ' + ' | '.join(processed_cells) + ' |')

                    if i == 0:
                        separator = '| ' + ' | '.join(['---'] * len(processed_cells)) + ' |'
                        markdown_table.append(separator)

            return '\n'.join(markdown_table) + '\n\n' if markdown_table else ''

        html_content = re.sub(r'<table[^>]*>.*?</table>', convert_table, html_content, flags=re.DOTALL | re.IGNORECASE)

        # 清理
        html_content = re.sub(r'<br[^>]*>', '\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<[^>]+>', '', html_content)
        html_content = html.unescape(html_content)
        html_content = re.sub(r'\n{3,}', '\n\n', html_content)

        return html_content.strip()

    def convert(self, input_path: str, output_path: str, use_pandoc: bool = True) -> Tuple[str, List[str]]:
        """主转换方法"""
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在: {input_path}")

        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        if use_pandoc and self.pandoc_available:
            try:
                return self.convert_with_pandoc(input_path, output_path)
            except Exception as e:
                print(f"Pandoc转换失败，切换到Mammoth: {e}")
                return self.convert_with_mammoth(input_path, output_path)
        else:
            return self.convert_with_mammoth(input_path, output_path)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Word 文档转 Markdown 工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python word2md_cli.py input.docx output.md
  python word2md_cli.py "文档.docx" "输出.md"
  Word2MD_CLI.exe input.docx output.md
        '''
    )

    parser.add_argument(
        'input',
        help='输入的 Word 文件路径 (.docx/.doc)'
    )

    parser.add_argument(
        'output',
        help='输出的 Markdown 文件路径 (.md)'
    )

    parser.add_argument(
        '--no-pandoc',
        action='store_true',
        help='禁用 Pandoc，使用 Mammoth 转换'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='Word2MD CLI v1.0.0'
    )

    args = parser.parse_args()

    input_path = args.input
    output_path = args.output

    # 验证输入文件
    if not os.path.exists(input_path):
        print(f"错误: 输入文件不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    # 检查文件扩展名
    valid_extensions = ['.docx', '.doc']
    ext = Path(input_path).suffix.lower()
    if ext not in valid_extensions:
        print(f"警告: 文件扩展名 '{ext}' 可能不是有效的 Word 文档", file=sys.stderr)

    # 执行转换
    try:
        converter = EnhancedWordToMarkdownConverter()
        use_pandoc = not args.no_pandoc

        print(f"正在转换: {input_path}")
        content, messages = converter.convert(input_path, output_path, use_pandoc=use_pandoc)

        # 输出结果
        output_abs_path = os.path.abspath(output_path)
        media_dir = Path(output_path).parent / f"{Path(output_path).stem}"

        print(f"转换成功!")
        print(f"输出文件: {output_abs_path}")

        if media_dir.exists():
            image_count = len(list(media_dir.iterdir()))
            if image_count > 0:
                print(f"图片目录: {os.path.abspath(media_dir)} ({image_count} 个文件)")

        if messages:
            print(f"警告信息: {len(messages)} 条")

        sys.exit(0)

    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"转换失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()