#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
migrate_content.py
将原始 83 个数字目录及散落文件迁移并整理为规范的 content/ 仓库结构。
按 GITHUB_PAGES_GUIDE.md 规范：
- 目录与片段使用三位补零 (004, 003)
- 提取 raw.txt 首行为章节标题
- 生成各章节 chapter.json 及全局 metadata.json
- 对比源文件与目标文件 SHA-256，保证 100% 字节无损
- 原始文件安全归档到 private-backup/raw_archive.zip，并清理根目录散落数字目录
"""

import os
import sys
import re
import json
import shutil
import hashlib
import zipfile
from pathlib import Path

def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    base_dir = Path(__file__).resolve().parent.parent
    os.chdir(base_dir)

    print("=== 开始内容迁移与整理 ===")
    
    # 查找所有数字目录
    raw_dirs = [d for d in base_dir.iterdir() if d.is_dir() and d.name.isdigit()]
    raw_dirs.sort(key=lambda d: int(d.name))
    
    print(f"检测到 {len(raw_dirs)} 个数字目录，编号范围 {raw_dirs[0].name} 至 {raw_dirs[-1].name}")

    content_dir = base_dir / "content"
    chapters_dir = content_dir / "chapters"
    prompts_dir = content_dir / "prompts"
    archive_dir = base_dir / "archive"
    backup_dir = base_dir / "private-backup"

    chapters_dir.mkdir(parents=True, exist_ok=True)
    prompts_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)
    backup_dir.mkdir(parents=True, exist_ok=True)

    # 1. 迁移与安全归档 time.epub
    epub_src = base_dir / "time.epub"
    epub_dst = archive_dir / "time.epub"
    if epub_src.exists():
        shutil.copy2(epub_src, epub_dst)
        assert sha256_file(epub_src) == sha256_file(epub_dst), "time.epub SHA256 不匹配！"
        print(f"已归档 time.epub -> archive/time.epub (SHA256 校验通过)")

    # 2. 迁移 4/ 中的 Yao_prompt 文件
    prompt_files = ["Yao_prompt.txt", "Yao_prompt_solution.md"]
    for pf in prompt_files:
        src = base_dir / "4" / pf
        dst = prompts_dir / pf
        if src.exists():
            shutil.copy2(src, dst)
            assert sha256_file(src) == sha256_file(dst), f"{pf} SHA256 不匹配！"
            print(f"已迁移提示词文档 {pf} -> content/prompts/{pf}")

    # 3. 遍历各数字目录进行迁移与元数据构建
    all_chapters_meta = []
    total_segments_count = 0
    total_paired_count = 0
    total_missing_src_count = 0
    total_missing_sol_count = 0

    migration_file_pairs = [] # (src, dst)

    for d in raw_dirs:
        d_num = int(d.name)
        cid = f"{d_num:03d}"
        ch_target = chapters_dir / cid
        ch_target.mkdir(parents=True, exist_ok=True)
        seg_target = ch_target / "segments"
        seg_target.mkdir(parents=True, exist_ok=True)

        # 处理 raw.txt
        raw_src = d / "raw.txt"
        raw_dst = ch_target / "raw.txt"
        if raw_src.exists():
            shutil.copy2(raw_src, raw_dst)
            migration_file_pairs.append((raw_src, raw_dst))
            with open(raw_src, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
            chapter_title = first_line if first_line else f"第 {d.name} 章（标题待补）"
        else:
            chapter_title = f"第 {d.name} 章（标题待补）"
            print(f"警告：目录 {d.name} 缺少 raw.txt！")

        # 扫描片段
        files = list(d.iterdir())
        txt_map = {}
        sol_map = {}
        for f in files:
            m_txt = re.match(r"^(\d+)\.txt$", f.name)
            if m_txt:
                txt_map[int(m_txt.group(1))] = f
            m_sol = re.match(r"^(\d+)_solution\.md$", f.name)
            if m_sol:
                sol_map[int(m_sol.group(1))] = f

        all_seg_ids = sorted(list(set(txt_map.keys()) | set(sol_map.keys())))
        segments_meta = []

        for sid_num in all_seg_ids:
            sid = f"{sid_num:03d}"
            txt_file = txt_map.get(sid_num)
            sol_file = sol_map.get(sid_num)

            src_rel = f"segments/{sid}.txt"
            sol_rel = f"segments/{sid}_solution.md"

            if txt_file and sol_file:
                status = "paired"
                total_paired_count += 1
                dst_txt = seg_target / f"{sid}.txt"
                dst_sol = seg_target / f"{sid}_solution.md"
                shutil.copy2(txt_file, dst_txt)
                shutil.copy2(sol_file, dst_sol)
                migration_file_pairs.append((txt_file, dst_txt))
                migration_file_pairs.append((sol_file, dst_sol))
            elif txt_file:
                status = "missing_solution"
                total_missing_sol_count += 1
                dst_txt = seg_target / f"{sid}.txt"
                shutil.copy2(txt_file, dst_txt)
                migration_file_pairs.append((txt_file, dst_txt))
            else:
                status = "missing_source"
                total_missing_src_count += 1
                dst_sol = seg_target / f"{sid}_solution.md"
                shutil.copy2(sol_file, dst_sol)
                migration_file_pairs.append((sol_file, dst_sol))

            segments_meta.append({
                "id": sid,
                "source": src_rel,
                "solution": sol_rel,
                "status": status
            })
            total_segments_count += 1

        # 生成章节 JSON
        chapter_meta = {
            "id": cid,
            "source_dir": d.name,
            "title": chapter_title,
            "raw_file": "raw.txt",
            "segments": segments_meta
        }
        with open(ch_target / "chapter.json", "w", encoding="utf-8") as f:
            json.dump(chapter_meta, f, ensure_ascii=False, indent=2)

        # 汇总信息
        all_chapters_meta.append({
            "id": cid,
            "source_dir": d.name,
            "title": chapter_title,
            "raw_file": f"chapters/{cid}/raw.txt",
            "segment_count": len(segments_meta),
            "paired_count": sum(1 for s in segments_meta if s["status"] == "paired"),
            "missing_source_count": sum(1 for s in segments_meta if s["status"] == "missing_source"),
            "missing_solution_count": sum(1 for s in segments_meta if s["status"] == "missing_solution")
        })

    # 生成全局 metadata.json
    global_meta = {
        "title": "《存在与时间》研读与逐段解析",
        "description": "海德格尔《存在与时间》中文译本分段原文、逐段深度解析与义理阐释",
        "total_chapters": len(all_chapters_meta),
        "total_segments": total_segments_count,
        "total_paired": total_paired_count,
        "total_missing_source": total_missing_src_count,
        "total_missing_solution": total_missing_sol_count,
        "chapters": all_chapters_meta
    }
    with open(content_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(global_meta, f, ensure_ascii=False, indent=2)
    print(f"已生成 content/metadata.json (包含 {len(all_chapters_meta)} 章节, {total_segments_count} 片段)")

    # 4. 全量 SHA-256 一致性校验
    print(f"正在对全部 {len(migration_file_pairs)} 个迁移文件进行 SHA-256 完整性比对...")
    mismatch_count = 0
    for src, dst in migration_file_pairs:
        h_src = sha256_file(src)
        h_dst = sha256_file(dst)
        if h_src != h_dst:
            print(f"错误: {src} 与 {dst} 哈希不匹配！")
            mismatch_count += 1
    if mismatch_count > 0:
        raise RuntimeError(f"迁移存在 {mismatch_count} 处哈希不一致，中断迁移！")
    print("全量文件 SHA-256 比对 100% 一致！")

    # 5. 安全打包原始数据至 private-backup/raw_archive.zip
    raw_archive_zip = backup_dir / "raw_archive.zip"
    if not raw_archive_zip.exists():
        print("正在打包原始数字目录至 private-backup/raw_archive.zip 作为脱机底稿备份...")
        with zipfile.ZipFile(raw_archive_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for d in raw_dirs:
                for root, _, files in os.walk(d):
                    for file in files:
                        p = Path(root) / file
                        zf.write(p, p.relative_to(base_dir))
            if epub_src.exists():
                zf.write(epub_src, "time.epub")
        print("原始目录打包备份完成。")

    # 6. 清理根目录中的原始数字目录及 epub
    print("正在清理根目录散落的数字目录与临时文件...")
    for d in raw_dirs:
        shutil.rmtree(d)
    if epub_src.exists():
        epub_src.unlink()
    print("根目录清理完毕！")
    print("=== 内容迁移全部成功完成 ===")

if __name__ == "__main__":
    main()
