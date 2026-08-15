# -*- coding: utf-8 -*-
"""Convert .doc templates to .docx and dump header/footer + body text for inspection."""
import os
import win32com.client

DOCS_DIR = r"d:\PycharmProjects\TraceTempAI\TraceTempAI_v5\docs"
FILES = ["环境失控纠正报告.doc", "24小时温湿度监控月度回顾表.doc"]

word = win32com.client.Dispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = 0

try:
    for name in FILES:
        src = os.path.join(DOCS_DIR, name)
        dst = os.path.join(DOCS_DIR, os.path.splitext(name)[0] + "_conv.docx")
        doc = word.Documents.Open(src, ReadOnly=False)
        # Save as docx (16 = wdFormatXMLDocument)
        doc.SaveAs2(dst, FileFormat=16)
        print("=" * 80)
        print("FILE:", name)
        print("=" * 80)
        # Dump headers
        for i, hf in enumerate(doc.Sections):
            sec = hf
            for htype in ("Headers", "Footers"):
                print(f"\n--- Section {i+1} {htype} (index: {getattr(hf, 'Index', '?')}) ---")
        # Actually iterate sections headers/footers
        for i in range(1, doc.Sections.Count + 1):
            sec = doc.Sections(i)
            for j in range(1, 4):  # wdHeaderFooterPrimary=1, FirstPage=2, EvenPages=3
                try:
                    hf = sec.Headers(j)
                    txt = hf.Range.Text.strip()
                    print(f"\n[Sec {i}] Header type {j}: {txt!r}")
                    # shapes / images in header
                    for shp in hf.Range.InlineShapes:
                        print(f"    inline shape: type={shp.Type}, size={shp.Width}x{shp.Height}pt, name={shp.Title if shp.Title else ''}")
                    for shp in hf.Shapes:
                        print(f"    floating shape: type={shp.Type}, size={shp.Width}x{shp.Height}pt, text={shp.TextFrame.TextRange.Text if shp.Type == 1 else ''}")
                except Exception as e:
                    pass
            for j in range(1, 4):
                try:
                    hf = sec.Footers(j)
                    txt = hf.Range.Text.strip()
                    print(f"[Sec {i}] Footer type {j}: {txt!r}")
                    for shp in hf.Range.InlineShapes:
                        print(f"    inline shape: type={shp.Type}, size={shp.Width}x{shp.Height}pt")
                    for shp in hf.Shapes:
                        print(f"    floating shape: type={shp.Type}, size={shp.Width}x{shp.Height}pt, text={shp.TextFrame.TextRange.Text if shp.Type == 1 else ''}")
                except Exception as e:
                    pass
        # Dump first-page body paragraphs (structure overview)
        print("\n--- Body paragraphs (first 60) ---")
        count = 0
        for p in doc.Paragraphs:
            t = p.Range.Text.strip()
            if t:
                style = p.Style.NameLocal if hasattr(p.Style, "NameLocal") else p.Style.Name
                align = p.Alignment
                print(f"  [{style}|align={align}] {t[:80]}")
                count += 1
            if count >= 60:
                break
        # Dump all tables structure
        print(f"\n--- Tables: {doc.Tables.Count} ---")
        for ti in range(1, doc.Tables.Count + 1):
            tbl = doc.Tables(ti)
            rows, cols = tbl.Rows.Count, tbl.Columns.Count
            print(f"\nTable {ti}: {rows}x{cols}")
            for ri in range(1, min(rows, 8) + 1):
                cells = []
                for ci in range(1, cols + 1):
                    try:
                        cells.append(tbl.Cell(ri, ci).Range.Text.strip().replace("\r", " ")[:30])
                    except Exception:
                        cells.append("(merged)")
                print(f"  R{ri}: {cells}")
        doc.Close(SaveChanges=False)
        print("\nSAVED CONVERTED:", dst)
finally:
    word.Quit()
print("DONE")
