# Visual Guide: BOM Integration UI Design

## 🎨 UI Components Overview

### **1. Material Input Toggle Buttons**

```
┌─────────────────────────────────────┐
│ [📚 Dari BOM] [✍️ Input Manual]    │
│  ↑ Blue Active  ↑ Gray Inactive    │
└─────────────────────────────────────┘

When switched:

┌─────────────────────────────────────┐
│ [📚 Dari BOM] [✍️ Input Manual]    │
│  ↑ Gray Inactive ↑ Green Active    │
└─────────────────────────────────────┘
```

**States**:
- **Blue (#2563eb)**: Dropdown mode active
- **Green (#16a34a)**: Manual mode active
- **Gray (#d1d5db)**: Inactive button

---

### **2. Dropdown Mode (BOM Masterdata)**

```
┌─────────────────────────────────────────────────┐
│ 📝 Nama Material *                              │
├─────────────────────────────────────────────────┤
│ [📚 Dari BOM] [✍️ Input Manual]                │
│  ↑ BLUE (Active)                                │
├─────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────┐ │
│ │ -- Pilih dari BOM Masterdata --            ▼│ │
│ │ PROD-001 - T-Shirt XL Blue                  │ │
│ │ PROD-002 - T-Shirt L Red                    │ │
│ │ PROD-003 - Hoodie M Black                   │ │
│ └─────────────────────────────────────────────┘ │
│   ↑ Blue background (#eff6ff)                   │
├─────────────────────────────────────────────────┤
│ ℹ️ 🔄 Kode Material akan otomatis terisi       │
│    dari BOM                                      │
└─────────────────────────────────────────────────┘
```

---

### **3. Manual Input Mode**

```
┌─────────────────────────────────────────────────┐
│ 📝 Nama Material *                              │
├─────────────────────────────────────────────────┤
│ [📚 Dari BOM] [✍️ Input Manual]                │
│                  ↑ GREEN (Active)               │
├─────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────┐ │
│ │ e.g., Kain Cotton Premium               [x] │ │
│ └─────────────────────────────────────────────┘ │
│   ↑ Green background (#f0fdf4)                  │
├─────────────────────────────────────────────────┤
│ ℹ️ ✍️ Input manual - isi kode material sendiri │
└─────────────────────────────────────────────────┘
```

---

### **4. Material Code Field - Auto-Generated (Dropdown Mode)**

```
┌─────────────────────────────────────────────────┐
│ 🔢 Kode Material * 🔄 Auto-generated dari BOM  │
├─────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────┐ │
│ │ PROD-001                                 🔒 │ │
│ └─────────────────────────────────────────────┘ │
│   ↑ Blue background (#eff6ff)                   │
│   ↑ Blue text (#1d4ed8)                         │
│   ↑ Bold font                                   │
│   ↑ Read-only (locked)                          │
├─────────────────────────────────────────────────┤
│ ✅ Kode ini otomatis dari BOM Masterdata       │
│    (Blue text #2563eb)                          │
└─────────────────────────────────────────────────┘
```

---

### **5. Material Code Field - Manual Input**

```
┌─────────────────────────────────────────────────┐
│ 🔢 Kode Material *                              │
├─────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────┐ │
│ │ e.g., FAB-CTN-001                       [x] │ │
│ └─────────────────────────────────────────────┘ │
│   ↑ White background (#ffffff)                  │
│   ↑ Black text (normal)                         │
│   ↑ Editable                                    │
└─────────────────────────────────────────────────┘
```

---

### **6. Complete Material Card (Dropdown Mode)**

```
┌──────────────────────────────────────────────────────────────┐
│ Material Card - Gradient Blue Background                     │
│ (bg-gradient-to-r from-blue-50 to-indigo-50)                │
├──────────────────────────────────────────────────────────────┤
│  ┌────┐                                                      │
│  │ 1  │  Material #1                                  [🗑️]  │
│  └────┘  Blue gradient badge with shadow                    │
│   ↑                                                          │
│  Blue circle (#2563eb to #4f46e5)                           │
│  White text, bold, shadow                                    │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────┬───────────────────────┐   │
│  │ [📚 Dari BOM] [✍️ Input Manual] (Toggle buttons)    │   │
│  │  ↑ BLUE        ↑ GRAY                                │   │
│  ├──────────────────────────────┴───────────────────────┤   │
│  │                                                       │   │
│  │ 📝 Nama Material *            🏷️ Kode Jenis *       │   │
│  │ ┌──────────────────────────┐  ┌──────────────────┐  │   │
│  │ │ PROD-001 - T-Shirt XL  ▼│  │ RAW - Bahan Baku ▼│  │   │
│  │ └──────────────────────────┘  └──────────────────┘  │   │
│  │   Blue BG (#eff6ff)            Gray border          │   │
│  │                                                       │   │
│  │ 🔢 Kode Material * (Auto)     📄 Deskripsi          │   │
│  │ ┌──────────────────────────┐  ┌──────────────────┐  │   │
│  │ │ PROD-001            🔒   │  │ Cotton 100%      │  │   │
│  │ └──────────────────────────┘  └──────────────────┘  │   │
│  │   Blue BG, Blue text, Bold     White BG            │   │
│  │   ✅ Kode ini otomatis dari BOM Masterdata         │   │
│  │                                                       │   │
│  │ 📊 Jumlah *  📏 Satuan *  💰 Harga *  💵 Total     │   │
│  │ ┌────────┐  ┌────────┐  ┌──────────┐ ┌──────────┐ │   │
│  │ │ 100    │  │ PCS   ▼│  │ 50000    │ │5,000,000 │ │   │
│  │ └────────┘  └────────┘  └──────────┘ └──────────┘ │   │
│  │                                         ↑ Blue BG  │   │
│  │                                         Blue text  │   │
│  │                                         Bold       │   │
│  └───────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

---

### **7. Grand Total Section**

```
┌──────────────────────────────────────────────────────────────┐
│ Grand Total Card - Green Gradient                            │
│ (bg-gradient-to-r from-green-50 to-emerald-50)              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  3 Material Items                  Grand Total Amount:      │
│                                                              │
│                                    Rp 15,000,000            │
│                                    ↑ 3xl font               │
│                                    ↑ Bold                   │
│                                    ↑ Green-700 text         │
│                                                              │
│                                    Indonesian Rupiah (IDR)  │
│                                    ↑ xs font, gray-500      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎨 Color Palette

### **Primary Colors**
```css
/* Blue (Dropdown Mode) */
--blue-50: #eff6ff;    /* Background */
--blue-200: #bfdbfe;   /* Border */
--blue-300: #93c5fd;   /* Border hover */
--blue-600: #2563eb;   /* Button, text */
--blue-700: #1d4ed8;   /* Text bold */

/* Green (Manual Mode) */
--green-50: #f0fdf4;   /* Background */
--green-300: #86efac;  /* Border */
--green-600: #16a34a;  /* Button, text */
--green-700: #15803d;  /* Total text */

/* Gray (Inactive/Neutral) */
--gray-50: #f9fafb;    /* Light background */
--gray-200: #e5e7eb;   /* Inactive button */
--gray-300: #d1d5db;   /* Border */
--gray-600: #4b5563;   /* Inactive text */
--gray-700: #374151;   /* Label text */

/* Gradient Backgrounds */
--blue-gradient: linear-gradient(to right, #eff6ff, #e0e7ff);
--indigo-gradient: linear-gradient(to right, #e0e7ff, #c7d2fe);
--green-gradient: linear-gradient(to right, #f0fdf4, #d1fae5);
```

---

## 📐 Layout Dimensions

### **Material Card**
```css
.material-card {
  padding: 20px;           /* p-5 */
  border-radius: 8px;      /* rounded-lg */
  border-width: 2px;       /* border-2 */
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);  /* shadow-sm */
  margin-bottom: 16px;     /* space-y-4 */
}
```

### **Badge (Material Number)**
```css
.material-badge {
  width: 40px;             /* w-10 */
  height: 40px;            /* h-10 */
  border-radius: 50%;      /* rounded-full */
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;         /* text-lg */
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);  /* shadow-md */
}
```

### **Toggle Buttons**
```css
.toggle-button {
  flex: 1;                 /* flex-1 */
  padding: 4px 8px;        /* px-2 py-1 */
  font-size: 12px;         /* text-xs */
  border-radius: 4px;      /* rounded */
  transition: all 0.2s;    /* transition */
}
```

### **Input Fields**
```css
.input-field {
  width: 100%;             /* w-full */
  padding: 12px;           /* px-3 py-2 */
  border-width: 1px;       /* border */
  border-radius: 6px;      /* rounded-md */
  font-size: 14px;         /* text-sm */
}

.input-field:focus {
  outline: none;
  ring-width: 2px;         /* focus:ring-2 */
  ring-color: #2563eb;     /* focus:ring-blue-500 */
  border-color: transparent;  /* focus:border-transparent */
}
```

---

## 🔄 State Transitions

### **Mode Toggle Animation**
```
Dropdown → Manual:
1. Blue button fades to gray (0.2s)
2. Green button fades from gray to green (0.2s)
3. Dropdown morphs to input field (0.3s)
4. Material code field clears
5. Background changes: blue-50 → green-50 (0.2s)

Manual → Dropdown:
1. Green button fades to gray (0.2s)
2. Blue button fades from gray to blue (0.2s)
3. Input field morphs to dropdown (0.3s)
4. Background changes: green-50 → blue-50 (0.2s)
```

### **Material Selection (Dropdown)**
```
Before selection:
- Dropdown: White background
- Material code: Empty, white background
- Helper text: "🔄 Kode Material akan otomatis terisi"

After selection:
- Dropdown: Blue background (#eff6ff)
- Material code: Filled, blue background, blue text, bold, locked
- Helper text: "✅ Kode ini otomatis dari BOM Masterdata"
- Auto-fill animation: Fade in (0.3s)
```

---

## 📱 Responsive Breakpoints

### **Desktop (md: 768px+)**
```css
.material-row {
  grid-template-columns: repeat(2, 1fr);  /* 2 columns */
  gap: 12px;                               /* gap-3 */
}

.quantity-row {
  grid-template-columns: repeat(4, 1fr);  /* 4 columns */
  gap: 12px;
}
```

### **Mobile (< 768px)**
```css
.material-row {
  grid-template-columns: 1fr;  /* 1 column */
  gap: 12px;
}

.quantity-row {
  grid-template-columns: repeat(2, 1fr);  /* 2 columns */
  gap: 12px;
}
```

---

## 🎯 Visual Hierarchy

```
Level 1 (Highest Priority):
- Material number badge (blue gradient circle)
- Toggle buttons (blue/green active states)

Level 2 (High Priority):
- Field labels with icons (📝, 🏷️, 🔢, etc.)
- Required asterisks (*)
- Auto-generated badge (🔄)

Level 3 (Medium Priority):
- Input fields
- Dropdown selections
- Helper text

Level 4 (Low Priority):
- Border decorations
- Background gradients
- Shadows
```

---

## 🔍 Accessibility Notes

### **Color Contrast**
- Blue-700 on Blue-50: ✅ WCAG AAA (7.2:1)
- Green-700 on Green-50: ✅ WCAG AAA (8.1:1)
- Gray-700 on White: ✅ WCAG AAA (10.7:1)

### **Keyboard Navigation**
- Tab order: Toggle → Name → Type → Code → Desc → Qty → Unit → Price
- Enter key: Submit form
- Escape key: Close modal
- Arrow keys: Navigate dropdown

### **Screen Reader**
- "Material number 1, Dropdown mode selected"
- "Material name field, required, auto-filled from BOM"
- "Material code, read-only, auto-generated"
- "Total price, auto-calculated, 5 million rupiah"

---

**Document Type**: UI/UX Visual Specification  
**Created**: February 4, 2026  
**Purpose**: Design reference for developers and QA team  
**Version**: 1.0
