#!/usr/bin/env python3
"""
日语学习书籍翻译脚本
将src目录下的所有.md文件翻译为中文，保存到src-zh目录
"""

import os
import shutil
from pathlib import Path
import openai
from typing import List, Tuple
import time
import re

class MarkdownTranslator:
    def __init__(self, api_key: str = None):
        """
        初始化翻译器
        
        Args:
            api_key: OpenAI API密钥，如果不提供则从环境变量OPENAI_API_KEY获取
        """
        if api_key:
            openai.api_key = api_key
        else:
            openai.api_key = os.getenv('OPENAI_API_KEY')
            if not openai.api_key:
                raise ValueError("请设置OPENAI_API_KEY环境变量或提供api_key参数")
        
        self.client = openai.OpenAI()
        
    def translate_text(self, text: str) -> str:
        """
        使用OpenAI API翻译文本
        
        Args:
            text: 要翻译的英文文本
            
        Returns:
            翻译后的中文文本
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": """你是一个专业的日语教学内容翻译专家。请将英文的日语学习教程翻译成中文。

翻译要求：
1. 保持markdown格式不变
2. 日语例句或英语例句保持原样不翻译，<pre></pre>标签之间的内容不翻译
3. 英文解释和说明翻译成中文
4. 保持专业术语的准确性
5. 语言要通俗易懂，适合中文读者
6. 保持原文的教学逻辑和结构
7. HTML标签保持不变
8. 链接地址保持不变，只翻译链接文本
9. 代码块和预格式化文本中的内容保持原样不翻译"""
                    },
                    {
                        "role": "user", 
                        "content": f"请翻译以下内容：\n\n{text}"
                    }
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            translated_text = response.choices[0].message.content.strip()
            return translated_text
            
        except Exception as e:
            print(f"翻译出错: {e}")
            return text  # 如果翻译失败，返回原文
    
    def split_content(self, content: str, max_length: int = 3000) -> List[str]:
        """
        将长文本按段落分割成较小的块，避免超过API限制
        
        Args:
            content: 要分割的内容
            max_length: 每块的最大长度
            
        Returns:
            分割后的文本块列表
        """
        if len(content) <= max_length:
            return [content]
        
        # 按段落分割
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk + paragraph + '\n\n') <= max_length:
                if current_chunk:
                    current_chunk += '\n\n' + paragraph
                else:
                    current_chunk = paragraph
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = paragraph
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def translate_markdown_file(self, input_path: Path, output_path: Path):
        """
        翻译单个markdown文件
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
        """
        print(f"正在翻译: {input_path}")
        
        try:
            # 读取原文件
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 如果文件为空，直接复制
            if not content.strip():
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return
            
            # 分割内容
            chunks = self.split_content(content)
            translated_chunks = []
            
            # 翻译每个块
            for i, chunk in enumerate(chunks):
                print(f"  翻译块 {i+1}/{len(chunks)}")
                translated_chunk = self.translate_text(chunk)
                translated_chunks.append(translated_chunk)
                
                # 添加延迟避免API限制
                if i < len(chunks) - 1:
                    time.sleep(1)
            
            # 合并翻译结果
            translated_content = '\n\n'.join(translated_chunks)
            
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入翻译后的文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            
            print(f"  完成: {output_path}")
            
        except Exception as e:
            print(f"翻译文件 {input_path} 时出错: {e}")
    
    def find_markdown_files(self, src_dir: Path) -> List[Path]:
        """
        查找src目录下的所有.md文件
        
        Args:
            src_dir: 源目录路径
            
        Returns:
            所有.md文件的路径列表
        """
        md_files = []
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if file.endswith('.md'):
                    md_files.append(Path(root) / file)
        return sorted(md_files)
    
    def translate_all_files(self, src_dir: str = "src", output_dir: str = "zh/src"):
        """
        翻译所有markdown文件
        
        Args:
            src_dir: 源目录
            output_dir: 输出目录
        """
        src_path = Path(src_dir)
        output_path = Path(output_dir)
        
        if not src_path.exists():
            print(f"源目录 {src_dir} 不存在")
            return
        
        # 查找所有markdown文件
        md_files = self.find_markdown_files(src_path)
        
        if not md_files:
            print(f"在 {src_dir} 目录下没有找到.md文件")
            return
        
        print(f"找到 {len(md_files)} 个markdown文件")
        
        # 复制images目录（如果存在）
        images_src = src_path / "images"
        if images_src.exists():
            images_dst = output_path / "images"
            if images_dst.exists():
                shutil.rmtree(images_dst)
            shutil.copytree(images_src, images_dst)
            print(f"已复制images目录到 {images_dst}")
        
        # 翻译每个文件
        for i, md_file in enumerate(md_files, 1):
            # 计算相对路径
            relative_path = md_file.relative_to(src_path)
            output_file = output_path / relative_path
            
            print(f"\n[{i}/{len(md_files)}] 处理文件: {relative_path}")
            
            self.translate_markdown_file(md_file, output_file)
        
        print(f"\n翻译完成！所有文件已保存到 {output_dir} 目录")


def main():
    """主函数"""
    print("日语学习书籍翻译工具")
    print("=" * 50)
    
    # 检查API密钥
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("错误: 请设置OPENAI_API_KEY环境变量")
        print("例如: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    try:
        # 创建翻译器
        translator = MarkdownTranslator()
        
        # 开始翻译
        translator.translate_all_files()
        
    except Exception as e:
        print(f"程序执行出错: {e}")


if __name__ == "__main__":
    main()