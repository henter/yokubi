#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并zh/src下Section1和Section2目录中的所有md文件为一个all.md文件
"""

import os
import glob
from pathlib import Path

def get_lesson_number(filename):
    """从文件名中提取课程编号，用于排序"""
    if 'Lesson' in filename:
        try:
            # 提取Lesson后面的数字
            lesson_num = int(filename.split('Lesson')[1].split('.')[0])
            return lesson_num
        except (ValueError, IndexError):
            return 0
    return 0

def get_part_number(filename):
    """从文件名中提取Part编号，用于排序"""
    if 'Part' in filename:
        try:
            # 提取Part后面的数字
            part_num = int(filename.split('Part')[1].split('.')[0])
            return part_num
        except (ValueError, IndexError):
            return 0
    return 0

def collect_md_files(base_path):
    """收集指定路径下的所有md文件并按逻辑顺序排序"""
    md_files = []
    
    # 使用glob递归查找所有md文件
    pattern = os.path.join(base_path, "**", "*.md")
    all_files = glob.glob(pattern, recursive=True)
    
    # 按照文件路径和名称进行排序
    for file_path in all_files:
        relative_path = os.path.relpath(file_path, base_path)
        md_files.append((file_path, relative_path))
    
    # 自定义排序函数
    def sort_key(item):
        file_path, relative_path = item
        parts = relative_path.split(os.sep)
        
        # 获取文件名
        filename = parts[-1]
        
        # 如果是Part文件（直接在Section目录下）
        if len(parts) == 1:
            if 'Part' in filename:
                return (get_part_number(filename), 0, filename)
            elif 'Section' in filename:
                return (0, 0, filename)
            else:
                return (999, 0, filename)
        
        # 如果是在子目录中的文件
        elif len(parts) == 2:
            subdir = parts[0]
            if 'Part' in subdir:
                part_num = get_part_number(subdir)
                lesson_num = get_lesson_number(filename)
                return (part_num, lesson_num, filename)
            else:
                return (999, 0, filename)
        
        return (999, 999, filename)
    
    md_files.sort(key=sort_key)
    return md_files

def merge_md_files():
    """合并md文件的主函数"""
    base_dir = "zh/src"
    sections = ["Section1", "Section2"]
    output_file = "zh/src/all.md"
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # 写入文件头部
        # outfile.write("# 合并的所有章节内容\n\n")
        # outfile.write("本文件包含了Section1和Section2的所有内容。\n\n")
        # outfile.write("---\n\n")
        
        for section in sections:
            section_path = os.path.join(base_dir, section)
            
            if not os.path.exists(section_path):
                print(f"警告: 目录 {section_path} 不存在，跳过...")
                continue
            
            print(f"处理 {section} ...")
            outfile.write(f"# {section}\n\n")
            
            # 收集该section下的所有md文件
            md_files = collect_md_files(section_path)
            
            for file_path, relative_path in md_files:
                print(f"  合并文件: {relative_path}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read().strip()
                        
                        if content:
                            # 添加文件标识
                            #outfile.write(f"## 文件: {relative_path}\n\n")
                            outfile.write(content)
                            outfile.write("\n\n---\n\n")
                        
                except Exception as e:
                    print(f"  错误: 无法读取文件 {file_path}: {e}")
                    continue
            
            #outfile.write(f"\n# {section} 结束\n\n")
            outfile.write("=" * 50 + "\n\n")
    
    print(f"合并完成！输出文件: {output_file}")
    
    # 显示统计信息
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"合并后的文件包含 {len(lines)} 行")
    except Exception as e:
        print(f"无法读取输出文件进行统计: {e}")

if __name__ == "__main__":
    print("开始合并md文件...")
    merge_md_files()
    print("合并任务完成！")