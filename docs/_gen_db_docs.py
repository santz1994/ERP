"""
Generate comprehensive DATABASE_SCHEMA.md from the live PostgreSQL database.
Run: python docs/_gen_db_docs.py
"""
import psycopg2
from datetime import datetime

conn = psycopg2.connect("postgresql://postgres:password123@localhost:5432/erp_quty_karunia")
cur = conn.cursor()

# ── 1. TABLES ───────────────────────────────────────────────────────────
cur.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema='public' AND table_type='BASE TABLE'
    ORDER BY table_name
""")
tables = [r[0] for r in cur.fetchall()]

# ── 2. COLUMNS ──────────────────────────────────────────────────────────
cur.execute("""
    SELECT t.table_name, c.column_name, c.ordinal_position, c.data_type,
           c.character_maximum_length, c.numeric_precision, c.numeric_scale,
           c.is_nullable, c.column_default, c.udt_name
    FROM information_schema.tables t
    JOIN information_schema.columns c
         ON t.table_name=c.table_name AND t.table_schema=c.table_schema
    WHERE t.table_schema='public' AND t.table_type='BASE TABLE'
    ORDER BY t.table_name, c.ordinal_position
""")
schema = {}
for row in cur.fetchall():
    tbl, col, pos, dtype, max_len, prec, scale, nullable, default, udt = row
    schema.setdefault(tbl, []).append({
        "col": col, "pos": pos, "type": dtype,
        "max_len": max_len, "prec": prec, "scale": scale,
        "nullable": nullable == "YES", "default": default, "udt": udt
    })

# ── 3. PRIMARY KEYS ─────────────────────────────────────────────────────
cur.execute("""
    SELECT tc.table_name, kcu.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
         ON tc.constraint_name=kcu.constraint_name AND tc.table_schema=kcu.table_schema
    WHERE tc.constraint_type='PRIMARY KEY' AND tc.table_schema='public'
    ORDER BY tc.table_name, kcu.ordinal_position
""")
pks = {}
for tbl, col in cur.fetchall():
    pks.setdefault(tbl, []).append(col)

# ── 4. FOREIGN KEYS ─────────────────────────────────────────────────────
cur.execute("""
    SELECT tc.table_name, kcu.column_name, ccu.table_name, ccu.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
         ON tc.constraint_name=kcu.constraint_name AND tc.table_schema=kcu.table_schema
    JOIN information_schema.constraint_column_usage ccu
         ON ccu.constraint_name=tc.constraint_name AND ccu.table_schema=tc.table_schema
    WHERE tc.constraint_type='FOREIGN KEY' AND tc.table_schema='public'
    ORDER BY tc.table_name, kcu.column_name
""")
fks = {}
for fk_tbl, fk_col, ref_tbl, ref_col in cur.fetchall():
    fks.setdefault(fk_tbl, []).append(
        {"col": fk_col, "ref_table": ref_tbl, "ref_col": ref_col}
    )

# ── 5. UNIQUE CONSTRAINTS ────────────────────────────────────────────────
cur.execute("""
    SELECT tc.table_name, kcu.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
         ON tc.constraint_name=kcu.constraint_name AND tc.table_schema=kcu.table_schema
    WHERE tc.constraint_type='UNIQUE' AND tc.table_schema='public'
    ORDER BY tc.table_name, kcu.column_name
""")
uniques = {}
for tbl, col in cur.fetchall():
    uniques.setdefault(tbl, []).append(col)

# ── 6. INDEXES ──────────────────────────────────────────────────────────
cur.execute("""
    SELECT indexname, tablename, indexdef
    FROM pg_indexes
    WHERE schemaname='public'
    ORDER BY tablename, indexname
""")
indexes = {}
for idxname, tbl, idxdef in cur.fetchall():
    indexes.setdefault(tbl, []).append({"name": idxname, "def": idxdef})

# ── 7. ENUM TYPES ───────────────────────────────────────────────────────
cur.execute("""
    SELECT t.typname, e.enumlabel
    FROM pg_type t
    JOIN pg_enum e ON e.enumtypid = t.oid
    WHERE t.typtype = 'e'
      AND substring(t.typname, 1, 1) != '_'
    ORDER BY t.typname, e.enumsortorder
""")
enums = {}
for typname, label in cur.fetchall():
    enums.setdefault(typname, []).append(label)

# ── 8. ROW COUNTS ───────────────────────────────────────────────────────
row_counts = {}
for tbl in tables:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        row_counts[tbl] = cur.fetchone()[0]
    except Exception:
        row_counts[tbl] = "?"

cur.close()
conn.close()

# ═══════════════════════════════════════════════════════════════════════
# BUILD MARKDOWN
# ═══════════════════════════════════════════════════════════════════════
now = datetime.now().strftime("%Y-%m-%d %H:%M")
L = []

L.append("# Database Schema — ERP Quty Karunia")
L.append(f"\n> **Generated:** {now}  ")
L.append("> **Database:** `erp_quty_karunia`  ")
L.append("> **Engine:** PostgreSQL 18  ")
L.append(f"> **Total Tables:** {len(tables)}  ")
L.append(f"> **Custom Enum Types:** {len(enums)}\n")

# ── TABLE OF CONTENTS ──
L.append("---\n## Table of Contents\n")
L.append("1. [Enum Types](#enum-types)")
L.append("2. [Table Summary](#table-summary)")
L.append("3. [Table Details](#table-details)")
for tbl in sorted(tables):
    anchor = tbl.replace("_", "-")
    L.append(f"   - [{tbl}](#{anchor})")
L.append("")

# ── ENUM TYPES ──
L.append("---\n## Enum Types\n")
L.append("Custom PostgreSQL enum types used across the schema:\n")
L.append("| Enum Type | Values |")
L.append("|-----------|--------|")
for typname, values in sorted(enums.items()):
    vals = " · ".join(f"`{v}`" for v in values)
    L.append(f"| `{typname}` | {vals} |")
L.append("")

# ── TABLE SUMMARY ──
L.append("---\n## Table Summary\n")
L.append("| Table | Columns | Rows | FK Refs |")
L.append("|-------|---------|------|---------|")
for tbl in sorted(tables):
    ncols = len(schema.get(tbl, []))
    nrows = row_counts.get(tbl, "?")
    fk_targets = ", ".join(
        f"`{f['ref_table']}`" for f in fks.get(tbl, [])
    ) or "—"
    anchor = tbl.replace("_", "-")
    L.append(f"| [`{tbl}`](#{anchor}) | {ncols} | {nrows} | {fk_targets} |")
L.append("")

# ── TABLE DETAILS ──
L.append("---\n## Table Details\n")

for tbl in sorted(tables):
    pk_cols    = pks.get(tbl, [])
    fk_list    = fks.get(tbl, [])
    fk_map     = {f["col"]: f for f in fk_list}
    uniq_cols  = uniques.get(tbl, [])
    tbl_idxs   = indexes.get(tbl, [])

    L.append(f"### `{tbl}`\n")

    L.append("| # | Column | Type | Nullable | Default | Notes |")
    L.append("|---|--------|------|----------|---------|-------|")

    for c in schema.get(tbl, []):
        col = c["col"]

        # ── Type string
        if c["type"] == "USER-DEFINED":
            dtype = f"`{c['udt']}`"
        elif c["type"] in ("character varying", "character"):
            dtype = f"`varchar({c['max_len']})`" if c["max_len"] else f"`{c['type']}`"
        elif c["type"] == "numeric":
            dtype = f"`numeric({c['prec']},{c['scale']})`" if c["prec"] else "`numeric`"
        elif c["type"] == "ARRAY":
            dtype = f"`{c['udt']}[]`"
        else:
            dtype = f"`{c['type']}`"

        nullable  = "" if c["nullable"] else "NOT NULL"
        dval = c["default"] or ""
        if "nextval" in dval:
            dval = "auto-increment"
        elif "now()" in dval or "CURRENT_TIMESTAMP" in dval:
            dval = "NOW()"
        elif len(dval) > 40:
            dval = dval[:40] + "…"

        notes = []
        if col in pk_cols:
            notes.append("🔑 PK")
        if col in fk_map:
            ref = fk_map[col]
            notes.append(f"FK → `{ref['ref_table']}.{ref['ref_col']}`")
        if col in uniq_cols:
            notes.append("UNIQUE")

        L.append(
            f"| {c['pos']} | `{col}` | {dtype} | {nullable} | {dval} | {' · '.join(notes)} |"
        )

    # FK list
    if fk_list:
        L.append("")
        L.append("**Foreign Keys:**")
        for fk in fk_list:
            L.append(f"- `{fk['col']}` → `{fk['ref_table']}.{fk['ref_col']}`")

    # Indexes
    if tbl_idxs:
        L.append("")
        L.append("**Indexes:**")
        for idx in tbl_idxs:
            # Shorten CREATE INDEX ... ON tablename USING btree (cola, colb)
            d = idx["def"]
            L.append(f"- `{idx['name']}` — `{d}`")

    L.append("")

# ── WRITE ──
out_path = r"d:\Project\ERP2026\docs\DATABASE_SCHEMA.md"
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(L))

print(f"✅  Written: {out_path}")
print(f"   Lines   : {len(L)}")
print(f"   Tables  : {len(tables)}")
print(f"   Enums   : {len(enums)}")
for k, v in sorted(enums.items()):
    print(f"      {k}: {v}")
