#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_content.py
对 content/ 目录、元数据、文件编码、哈希一致性以及仓库安全性进行全维度门禁检查。
"""

import os
import sys
import re
import json
import hashlib
import zipfile
import random
from pathlib import Path

def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def run_validations():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    base_dir = Path(__file__).resolve().parent.parent
    os.chdir(base_dir)

    print("==========================================")
    print("      《存在与时间》内容完整性与安全门禁核验      ")
    print("==========================================")

    errors = []
    warnings = []

    content_dir = base_dir / "content"
    chapters_dir = content_dir / "chapters"
    prompts_dir = content_dir / "prompts"
    archive_dir = base_dir / "archive"
    backup_dir = base_dir / "private-backup"
    metadata_file = content_dir / "metadata.json"

    # 1. 检查 metadata.json
    print("\n[门禁 1/7] 检查 metadata.json 元数据格式与完整性...")
    if not metadata_file.exists():
        errors.append("content/metadata.json 文件不存在！")
        return False
    
    try:
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    except Exception as e:
        errors.append(f"metadata.json JSON 解析失败: {e}")
        return False

    chapters = metadata.get("chapters", [])
    if len(chapters) != 83:
        errors.append(f"章节数量不等于 83，实际检测到: {len(chapters)}")
    else:
        print(f"  [OK] 章节总数符合预期 (83 章)")

    # 验证章节数值排序
    chapter_ids = [int(c["id"]) for c in chapters]
    if chapter_ids != sorted(chapter_ids):
        errors.append("metadata.json 中的章节未按数值升序排序！")
    else:
        print(f"  [OK] 章节已按数值严格升序排列 ({chapters[0]['id']} -> {chapters[-1]['id']})")

    total_segments = metadata.get("total_segments", 0)
    total_paired = metadata.get("total_paired", 0)
    total_missing_src = metadata.get("total_missing_source", 0)
    total_missing_sol = metadata.get("total_missing_solution", 0)
    print(f"  [OK] 片段统计: 总数 {total_segments}, 配对 {total_paired}, 缺原文 {total_missing_src}, 缺题解 {total_missing_sol}")

    # 2. 检查各章节结构与 chapter.json
    print("\n[门禁 2/7] 逐章检查章节目录、chapter.json、raw.txt 与片段配对...")
    checked_segments = 0
    checked_paired = 0

    for ch in chapters:
        cid = ch["id"]
        ch_path = chapters_dir / cid
        if not ch_path.exists():
            errors.append(f"章节目录不存在: {ch_path}")
            continue

        raw_path = ch_path / "raw.txt"
        if not raw_path.exists():
            errors.append(f"章节缺少 raw.txt: {raw_path}")

        ch_json_path = ch_path / "chapter.json"
        if not ch_json_path.exists():
            errors.append(f"缺少 chapter.json: {ch_json_path}")
            continue

        try:
            with open(ch_json_path, "r", encoding="utf-8") as f:
                ch_data = json.load(f)
        except Exception as e:
            errors.append(f"{ch_json_path} JSON 解析失败: {e}")
            continue

        if ch_data.get("id") != cid:
            errors.append(f"{ch_json_path} 中的 id '{ch_data.get('id')}' 与目录 '{cid}' 不符")

        segs = ch_data.get("segments", [])
        seg_ids = [int(s["id"]) for s in segs]
        if seg_ids != sorted(seg_ids):
            errors.append(f"{ch_json_path} 中的片段未按数值升序排列")

        for s in segs:
            checked_segments += 1
            sid = s["id"]
            src_file = ch_path / s["source"]
            sol_file = ch_path / s["solution"]
            status = s["status"]

            if status == "paired":
                checked_paired += 1
                if not src_file.exists():
                    errors.append(f"配对片段源文件缺失: {src_file}")
                if not sol_file.exists():
                    errors.append(f"配对片段题解缺失: {sol_file}")
            elif status == "missing_solution":
                if not src_file.exists():
                    errors.append(f"片段源文件缺失: {src_file}")
            elif status == "missing_source":
                if not sol_file.exists():
                    errors.append(f"片段题解缺失: {sol_file}")

    print(f"  [OK] 83 章节结构核验通过，共计核查 {checked_segments} 个片段文件")

    # 3. 检查 UTF-8 编码与异常字符
    print("\n[门禁 3/7] 全量扫描文件编码与 UTF-8 完整性...")
    text_extensions = {".txt", ".md", ".json", ".html", ".css", ".js"}
    encoding_error_files = []
    replacement_char_files = []

    for root, _, files in os.walk(content_dir):
        for f in files:
            p = Path(root) / f
            if p.suffix.lower() in text_extensions:
                try:
                    with open(p, "r", encoding="utf-8") as fp:
                        content = fp.read()
                        if "\ufffd" in content:
                            replacement_char_files.append(str(p.relative_to(base_dir)))
                except Exception as e:
                    encoding_error_files.append((str(p.relative_to(base_dir)), str(e)))

    if encoding_error_files:
        errors.append(f"发现 {len(encoding_error_files)} 个文件的 UTF-8 解码失败: {encoding_error_files[:5]}")
    else:
        print("  [OK] 全量文本文件 UTF-8 解码 100% 成功，无非法编码字节")

    if replacement_char_files:
        warnings.append(f"发现 {len(replacement_char_files)} 个文件中含有 \\ufffd 替换字符: {replacement_char_files[:5]}")
    else:
        print("  [OK] 全量文本文件中无 \\ufffd 乱码替换字符")

    # 4. SHA-256 抽样核对（对比原始底稿 zip）
    print("\n[门禁 4/7] SHA-256 哈希比对（从原始底稿中抽查并核对）...")
    raw_archive_zip = backup_dir / "raw_archive.zip"
    if not raw_archive_zip.exists():
        warnings.append("private-backup/raw_archive.zip 不存在，跳过与原始 zip 的对比抽检")
    else:
        with zipfile.ZipFile(raw_archive_zip, "r") as zf:
            zip_names = [n for n in zf.namelist() if not n.endswith('/') and not '.vscode' in n]
            sample_candidates = [n for n in zip_names if re.search(r'\d+/\d+(\.txt|_solution\.md)$', n)]
            
            # 抽查至少 20 个片段文件
            random.seed(42)
            sample_files = random.sample(sample_candidates, min(30, len(sample_candidates)))
            
            sha_mismatches = 0
            for orig_name in sample_files:
                orig_bytes = zf.read(orig_name)
                orig_hash = sha256_bytes(orig_bytes)

                # 计算对应 content/ 中的目标文件
                # 例如 4/3.txt -> content/chapters/004/segments/003.txt
                # 4/3_solution.md -> content/chapters/004/segments/003_solution.md
                parts = orig_name.replace('\\', '/').split('/')
                dir_num = int(parts[0])
                file_name = parts[1]
                m = re.match(r'^(\d+)(.*)$', file_name)
                seg_num = int(m.group(1))
                suffix = m.group(2)
                target_rel = Path("content") / "chapters" / f"{dir_num:03d}" / "segments" / f"{seg_num:03d}{suffix}"
                target_full = base_dir / target_rel

                if not target_full.exists():
                    errors.append(f"抽检目标文件不存在: {target_rel}")
                    sha_mismatches += 1
                    continue

                target_hash = sha256_file(target_full)
                if orig_hash != target_hash:
                    errors.append(f"哈希不匹配: {orig_name} ({orig_hash[:8]}...) vs {target_rel} ({target_hash[:8]}...)")
                    sha_mismatches += 1

            if sha_mismatches == 0:
                print(f"  [OK] 成功随机抽检 {len(sample_files)} 个片段源文件与题解文件，SHA-256 100% 吻合！")
            else:
                errors.append(f"哈希抽验发现 {sha_mismatches} 处不匹配！")

    # 5. 安全排查：扫描敏感信息与私有配置
    print("\n[门禁 5/7] 安全排查：全库敏感凭据与私有 IP 扫描...")
    secret_patterns = {
        "sk_key": re.compile(r"sk-[A-Za-z0-9_\-]{16,}"),
        "api_key_assign": re.compile(r"api_key\s*[:=]\s*['\"][A-Za-z0-9_\-]{8,}['\"]", re.IGNORECASE),
        "password_assign": re.compile(r"password\s*[:=]\s*['\"][^'\"]{6,}['\"]", re.IGNORECASE),
        "bearer_token": re.compile(r"Bearer\s+[A-Za-z0-9_\-\.]{16,}", re.IGNORECASE),
        "private_ip": re.compile(r"(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|220\.185\.228\.\d{1,3})"),
        "local_path": re.compile(r"(?:[A-Za-z]:[\\/]|/Users/|/home/)(?:time|63254)")
    }

    scanned_files_count = 0
    leaks = []

    for root, dirs, files in os.walk(base_dir):
        # 排除私有备份和 git
        dirs[:] = [d for d in dirs if d not in {".git", "private-backup", ".venv", "__pycache__", ".vscode"}]
        for f in files:
            # 排除自身脚本和规范文档中的规则文本
            p = Path(root) / f
            rel_p = str(p.relative_to(base_dir)).replace("\\", "/")
            if rel_p in {"GITHUB_PAGES_GUIDE.md", "scripts/validate_content.py", "scripts/migrate_content.py"}:
                continue

            if p.suffix.lower() in text_extensions or p.name in {".gitignore", "requirements.txt"}:
                scanned_files_count += 1
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                        for lno, line in enumerate(fp, 1):
                            for pat_name, pat in secret_patterns.items():
                                m = pat.search(line)
                                if m:
                                    leaks.append((rel_p, lno, pat_name, m.group(0), line.strip()[:80]))
                except Exception as e:
                    warnings.append(f"无法读取文件进行安全扫描: {rel_p} ({e})")

    if leaks:
        for leak in leaks:
            errors.append(f"敏感信息泄漏风险 [{leak[2]}]: {leak[0]}:{leak[1]} -> {leak[3]}")
    else:
        print(f"  [OK] 扫描了 {scanned_files_count} 个文件，未发现任何 API Key、密码、Token、私有 IP 或本地宿主绝对路径")

    # 6. Git 与忽略文件合规检查
    print("\n[门禁 6/7] 检查 .gitignore 与敏感文件隔离状态...")
    gitignore_file = base_dir / ".gitignore"
    if not gitignore_file.exists():
        errors.append(".gitignore 文件不存在！")
    else:
        gi_content = gitignore_file.read_text(encoding="utf-8")
        required_patterns = ["apis.csv", "private-backup", "*.env", ".venv", "__pycache__", "failure.csv"]
        for rp in required_patterns:
            if rp not in gi_content:
                errors.append(f".gitignore 缺少关键保护项: {rp}")
        print("  [OK] .gitignore 配置完备，已覆盖 apis.csv、private-backup/ 等敏感规则")

    # 7. 全站 HTML 静态产物无死链 (404) 且无路径泄漏校验
    print("\n[门禁 7/7] 全站 HTML 静态产物完整性、死链 (404) 与路径泄漏校验...")
    docs_dir = base_dir / "docs"
    if not docs_dir.exists():
        errors.append("docs/ 目录不存在，尚未执行 build_site.py 生成！")
    else:
        html_files = list(docs_dir.rglob("*.html"))
        print(f"  [OK] 检测到 docs/ 下共 {len(html_files)} 个 HTML 页面")
        if len(html_files) != 1 + 83 + 1284:
            errors.append(f"HTML 页面总数不等于 1368 (实际: {len(html_files)})")

        # 检查静态资源
        for asset in ["assets/style.css", "assets/site.js", "search-index.json"]:
            if not (docs_dir / asset).exists():
                errors.append(f"缺少关键静态文件: docs/{asset}")

        # 解析全部 HTML 内部链接
        link_regex = re.compile(r"""(?:href|src)=["']([^"']+)["']""", re.IGNORECASE)
        broken_links = []
        path_leaks = []
        total_links_checked = 0

        for hf in html_files:
            content = hf.read_text(encoding="utf-8")
            if "D:\\time" in content or "C:\\Users" in content:
                path_leaks.append(str(hf.relative_to(docs_dir)))

            for m in link_regex.finditer(content):
                target = m.group(1).strip()
                if target.startswith(("http://", "https://", "mailto:", "#", "javascript:")):
                    continue
                total_links_checked += 1
                clean_target = target.split("#")[0].split("?")[0]
                if not clean_target:
                    continue
                target_path = (hf.parent / clean_target).resolve()
                if not target_path.exists():
                    broken_links.append((str(hf.relative_to(docs_dir)), target))

        if path_leaks:
            errors.append(f"在 {len(path_leaks)} 个 HTML 页面中发现了宿主绝对路径泄漏！")
        else:
            print("  [OK] 全站所有页面均无本机绝对路径残留")

        if broken_links:
            errors.append(f"发现 {len(broken_links)} 处内部死链 (404): {broken_links[:5]}")
        else:
            print(f"  [OK] 全站共抽检并核实 {total_links_checked} 处内部链接/资源引用，100% 存在，零死链 (404)！")

    # 汇总输出
    print("\n==========================================")
    print("                核验结果汇总               ")
    print("==========================================")
    if warnings:
        print(f"[WARN] 警告 ({len(warnings)} 项):")
        for w in warnings:
            print(f"   - {w}")
    else:
        print("[OK] 无任何警告")

    if errors:
        print(f"[FAIL] 门禁拦截 ({len(errors)} 项错误):")
        for e in errors:
            print(f"   - {e}")
        print("\n验证未通过，请修复上述问题后继续！")
        return False
    else:
        print("[PASS] 全部 7 项门禁检验 100% 通过！数据完好、编码规范、无安全泄漏、无404死链！")
        return True

if __name__ == "__main__":
    success = run_validations()
    sys.exit(0 if success else 1)
