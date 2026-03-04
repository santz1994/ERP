-- Migration 009: Add specialized material categories (missing from seed)
-- Date: 2026-03-04
--
-- NOTE: This database already has comprehensive categories:
--   Fabric - * (15 types), Label - * (4), Thread, Stuffing - Fiber/Polyester,
--   Accessories - * (8 types), Packaging - * (3), Elastic,
--   WIP Cutting/Embroidery/Finishing/Packing/Sewing, Finished Goods, Raw Materials
--
-- _detect_material_category() mapping (purchasing.py):
--   cat LIKE 'Fabric%'      → FABRIC   → PO KAIN
--   cat LIKE 'Label%'       → LABEL    → PO LABEL
--   cat LIKE 'Thread%'      → THREAD   → PO ACCESSORIES
--   cat LIKE 'Stuffing%'    → FILLING  → PO ACCESSORIES
--   cat LIKE 'Packaging%'   → ACCESSORIES
--   cat LIKE 'Accessories%' → ACCESSORIES
--   cat = 'Elastic'         → ACCESSORIES
--   cat LIKE 'WIP%'         → WIP
--
-- Only adds genuinely missing subcategories:

INSERT INTO categories (name, description)
VALUES ('Chemical / Lem', 'Adhesive, glue (lem), solvent, chemical auxiliaries')
ON CONFLICT (name) DO NOTHING;

INSERT INTO categories (name, description)
VALUES ('Isolasi / Insulation', 'Isolasi tape, masking tape, selotip, foam tape')
ON CONFLICT (name) DO NOTHING;

INSERT INTO categories (name, description)
VALUES ('Jarum / Needle', 'Sewing needles, machine needles, hand needles')
ON CONFLICT (name) DO NOTHING;
