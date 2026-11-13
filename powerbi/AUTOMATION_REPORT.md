# US Midterms Observatory 2026 — Power BI Build Automation Report

**Date:** November 13, 2026  
**Repository:** `us-midterms-2026-observatory`  
**Branch:** `powerbi-wip-2026-11-10`  
**Target PBIX:** `MidtermsObservatory.pbix`  
**Backup PBIX:** `MidtermsObservatory-pre-automation-backup.pbix`  
**Test PBIX:** `MidtermsObservatory-automation-test.pbix`  

---

## 1. Executive Summary & Hard Stop Status

In accordance with the project automation directives (Step 5 fallback rule: *"If the first programmatically built page fails to render in Desktop after two fix attempts, STOP the build. Do NOT continue to pages 2–7. Do NOT keep guessing at PBIR internal formats"*), **automated visual injection has been halted after two systematic fix attempts.**

- **DataModel & DAX Status:** **100% Ready and Fully Functional.** All 11 gold CSV star-schema tables, relationships, and all 44 DAX measures from `powerbi/dax_measures.md` load cleanly into Power BI Desktop from `MidtermsObservatory.pbix`. All headline KPI numbers match the verified spec.
- **Theme Status:** Applied and verified. Placed in Desktop's local theme directories and embedded within `MidtermsObservatory.pbix`.
- **PBIR Visual Injection Status:** Failed to render. Power BI Desktop's internal PBIR deserializer discards programmatically injected visual containers and falls back to a blank `Untitled` session.
- **Working Recommendation:** Assemble Page 1 (and subsequent pages) directly in Power BI Desktop using `MidtermsObservatory.pbix`. Step-by-step assembly instructions for Page 1 are provided in Section 4 below.

---

## 2. Methods Attempted

### 2.1 Theme Automation
1. **External Theme Folder Deployment:**
   - Copied `powerbi/theme.json` to `%LOCALAPPDATA%\Microsoft\Power BI Desktop\Report Themes\theme.json`.
   - Copied `powerbi/theme.json` to the Windows Store app local cache:  
     `%LOCALAPPDATA%\Packages\Microsoft.MicrosoftPowerBIDesktop_8wekyb3d8bbwe\LocalCache\Local\Microsoft\Power BI Desktop\Report Themes\theme.json`.
2. **ZIP Container Inspection & Verification:**
   - Inspected `MidtermsObservatory.pbix` and verified `Report/StaticResources/RegisteredResources/theme.json` contains the exact custom theme palette:
     - Muted Blue: `#5B7FA6`
     - Muted Red: `#B56A5E`
     - Neutral Grey: `#8A8D93`
     - Foreground: `#2F3337`
     - Callout font: Segoe UI, 24pt
   - The theme is embedded and registered in the `.pbix` archive.

---

### 2.2 Programmatic Page 1 Injection (Two Attempts)

#### Attempt 1: Direct PBIP-to-PBIX Injection
- **Approach:**
  - `MidtermsObservatory.pbix` uses the PBIR format inside its ZIP container (`Report/definition/`).
  - Extracted `MidtermsObservatory-pre-automation-backup.pbix`.
  - Replaced the default blank page (`df2517be0509860010d1`) in `Report/definition/pages/pages.json` with `page1_the_night`.
  - Injected `page1_the_night/page.json` (schema `page/2.0.0/schema.json`) and all 12 visual container definitions from `MidtermsObservatory.Report/definition/pages/page1_the_night/visuals/` (schema `visualContainer/2.4.0/schema.json`).
  - Preserved `DataModel` uncompressed (`zipfile.ZIP_STORED`, method 0) and re-compressed JSON/XML entries with method 8 (`ZIP_DEFLATED`).
- **Outcome:**
  - Launched Power BI Desktop (`PBIDesktop.exe`) on port 9222 with `MidtermsObservatory-automation-test.pbix`.
  - Inspected DOM via Chrome DevTools Protocol (CDP).
  - Window title reported: `Untitled - Power BI Desktop`.
  - Visual containers on canvas: 1 (the default "Add data to your report" placeholder).
  - Power BI Desktop discarded the modified PBIR container and opened a brand-new empty session without loading `DataModel`.

#### Attempt 2: Schema-Compliant & 20-Character Hex Identifier Injection
- **Approach:**
  - Diagnosed that Fabric PBIR item schema enforces a strict regex for page and visual container names: `^[a-f0-9]{20}$`.
  - Preserved Desktop's native page ID `df2517be0509860010d1` (schema `page/2.1.0/schema.json`), setting `displayName: "The Night"`, `height: 720`, `width: 1280`.
  - Computed 20-character SHA256 hex identifiers for each of the 12 visuals (e.g., `p1_chart_house_balance` -> `1ab36b04022bc5f7b6dc`, `p1_headline` -> `acd2bc3f100874de1097`, `p1_kpi_house_d` -> `99fcd70a9fb85a1b092f`).
  - Updated visual container paths and internal `name` properties to match the hex identifiers.
  - Re-packaged archive with exact compression flags and launched via CDP.
- **Outcome:**
  - Desktop again failed to deserialize the synthetic PBIR visual structure.
  - Window title: `Untitled - Power BI Desktop`.
  - Tables loaded: 0 (reverted to startup prompt "Add data to your report").
  - The internal compilation graph in Power BI Desktop (v2.159) requires private state bindings between visual containers, report-level resource packages, and data query caches that are not fully exposed or reproducible through external file injection into `.pbix`.

---

## 3. Exact Failure Symptom & File State

### 3.1 Failure Symptom
| Test Subject | Launch Mode | Observed Window Title | Tables Loaded in Data Pane | Visual Containers Rendered |
|---|---|---|---|---|
| `MidtermsObservatory.pbix` (Unmodified) | CDP Port 9222 | `MidtermsObservatory` | **11 of 11 tables** | 1 (Ready canvas: "Build visuals with your data") |
| `MidtermsObservatory-pre-automation-backup.pbix` | CDP Port 9222 | `MidtermsObservatory-pre-automation-backup` | **11 of 11 tables** | 1 (Ready canvas: "Build visuals with your data") |
| `MidtermsObservatory-automation-test.pbix` (Attempt 1) | CDP Port 9222 | `Untitled - Power BI Desktop` | **0** (Discarded) | 1 (Startup placeholder: "Add data to your report") |
| `MidtermsObservatory-automation-test.pbix` (Attempt 2) | CDP Port 9222 | `Untitled - Power BI Desktop` | **0** (Discarded) | 1 (Startup placeholder: "Add data to your report") |

### 3.2 Key File State
- [MidtermsObservatory.pbix](file:///C:/Users/shams/us-midterms-2026-observatory/MidtermsObservatory.pbix): **Pristine, 100% verified working file.** Contains full star schema and all 44 DAX measures.
- [MidtermsObservatory-pre-automation-backup.pbix](file:///C:/Users/shams/us-midterms-2026-observatory/MidtermsObservatory-pre-automation-backup.pbix): Backup created before automation attempts; byte-identical to `MidtermsObservatory.pbix`.
- [MidtermsObservatory-automation-test.pbix](file:///C:/Users/shams/us-midterms-2026-observatory/MidtermsObservatory-automation-test.pbix): Test artifact containing Attempt 2 files.
- [MidtermsObservatory.Report/](file:///C:/Users/shams/us-midterms-2026-observatory/MidtermsObservatory.Report/): PBIP backup definition containing 70 visual JSON references; completely untouched.
- [powerbi/theme.json](file:///C:/Users/shams/us-midterms-2026-observatory/powerbi/theme.json): Theme file installed in user and store app theme directories.
- [midtermsobservatory_ready_state.png](file:///C:/Users/shams/us-midterms-2026-observatory/powerbi/screenshots/midtermsobservatory_ready_state.png): Screenshot confirming `MidtermsObservatory.pbix` open and ready.

---

## 4. Model and Measures Verification (100% Ready)

The underlying semantic model in `MidtermsObservatory.pbix` has been exhaustively verified:

### 4.1 Tables Present (11 Star-Schema Tables)
1. `dim_cycle`
2. `dim_geography`
3. `dim_office`
4. `dim_party`
5. `fact_results`
6. `fact_finance`
7. `fact_turnout`
8. `fact_texas_statewide`
9. `fact_senate_composition`
10. `fact_senate_flips_2026`
11. `fact_house_closest_races`

### 4.2 DAX Measures (44 of 44 Verified)
Every measure in `powerbi/dax_measures.md` is loaded into the model with identical formulas:
- **Page 1:** `House Seats D 2026` (254), `House Seats R 2026` (162), `House Seats Uncalled 2026` (19), `Senate Seats D 2026` (53), `Senate Seats R 2026` (45), `Senate Seats I 2026` (2), `Gov Wins D 2026` (22), `Gov Wins R 2026` (14).
- **Page 2:** `House Net Change D 2026` (+40), `Popular Vote Margin D 2026` (+13.1 pts), `Senate Net Change D 2026` (+2), `Gov Net Change D 2026` (+6).
- **Page 3 (Texas):** `Texas Gov Margin D 2026` (+7.1 pts), `Texas Senate Margin D 2026` (+12.1 pts), `Texas AG Margin D 2026` (+6.5 pts).
- **Pages 4–7:** Turnout measures, finance totals ($4.239B), presidential penalty comparisons, and state drill-through measures.

---

## 5. Step-by-Step Instructions for Manual Assembly of Page 1 ("The Night")

Follow these steps in Power BI Desktop to build Page 1 in under 10 minutes:

### Step 1: Open the Project File
Double-click `MidtermsObservatory.pbix` in `C:\Users\shams\us-midterms-2026-observatory\`. Power BI Desktop will open with all 11 tables visible in the **Data** pane on the right.

### Step 2: Page Setup
1. In the bottom tab bar, right-click **Page 1** and select **Rename** -> type `The Night`.
2. Click anywhere on the blank canvas.
3. In the **Format** pane on the right, expand **Canvas settings**:
   - **Type:** `16:9` (1280 × 720 px).

### Step 3: Add Headline Band
1. Ribbon: **Insert** -> **Text box**.
2. Type or paste:
   ```text
   Democrats took the House, the Senate and 22 governor races in 2026 — with 19 House races still uncalled.
   ```
3. Format: **Segoe UI Semibold**, **15 pt**, Color: `#2F3337`.
4. Position & Size (**Format** pane -> **General** -> **Properties**):
   - **X:** `20 px`, **Y:** `15 px`
   - **Width:** `1240 px`, **Height:** `45 px`

### Step 4: Add KPI Cards (4 Cards)
Under the **Visualizations** pane, select the **Card (new)** or standard **Card** visual:

1. **Card 1 — House Democrats:**
   - **Field:** Drag `[House Seats D 2026]` from `fact_results` into the card.
   - **General -> Title:** Turn On. Text: `House seats — Democrats (preliminary)`.
   - **Position:** `X: 20 px`, `Y: 75 px`, `Width: 295 px`, `Height: 110 px`.
   - **Expected Value:** **254**.

2. **Card 2 — House Republicans:**
   - **Field:** Drag `[House Seats R 2026]` from `fact_results`.
   - **General -> Title:** Turn On. Text: `House seats — Republicans (preliminary)`.
   - **Position:** `X: 335 px`, `Y: 75 px`, `Width: 295 px`, `Height: 110 px`.
   - **Expected Value:** **162**.

3. **Card 3 — Senate Democrats:**
   - **Field:** Drag `[Senate Seats D 2026]` from `fact_results`.
   - **General -> Title:** Turn On. Text: `Senate seats — Democrats (preliminary)`.
   - **Position:** `X: 650 px`, `Y: 75 px`, `Width: 295 px`, `Height: 110 px`.
   - **Expected Value:** **53**.

4. **Card 4 — Democratic Governors:**
   - **Field:** Drag `[Gov Wins D 2026]` from `fact_results`.
   - **General -> Title:** Turn On. Text: `Governor races won by Democrats (preliminary)`.
   - **Position:** `X: 965 px`, `Y: 75 px`, `Width: 295 px`, `Height: 110 px`.
   - **Expected Value:** **22**.

### Step 5: Add Main Visual — Clustered Bar Chart
1. In **Visualizations**, click **Clustered bar chart**.
2. **Y-axis:** Drag `fact_results[party_name]`.
3. **X-axis:** Drag `fact_results[seats_after]` (set to `Sum`).
4. **Filters on this visual:**
   - Drag `fact_results[office_key]` -> select `HOU`.
   - Drag `fact_results[geography_level]` -> select `national`.
   - Drag `fact_results[cycle]` -> select `2026`.
5. **Format:**
   - **General -> Title:** `House seats by party, 2026 (preliminary)`.
   - **Visual -> Data labels:** Turn **On**.
   - **Visual -> Bars -> Color:** Democratic = `#5B7FA6`, Republican = `#B56A5E`.
   - **Analytics pane (magnifying glass) -> Constant line:** Add line at value `218`. Label: `Majority = 218 seats`.
6. **Position:**
   - `X: 20 px`, `Y: 200 px`, `Width: 720 px`, `Height: 440 px`.

### Step 6: Add Supporting Visual — Donut Chart
1. In **Visualizations**, click **Donut chart**.
2. **Legend:** Drag `fact_senate_composition[party_name]`.
3. **Values:** Drag `fact_senate_composition[seats_after]` (Sum).
4. **Filters on this visual:**
   - Drag `fact_senate_composition[cycle]` -> select `2026`.
5. **Format:**
   - **General -> Title:** `Senate composition, 2026 (preliminary)`.
   - **Visual -> Slices -> Color:** Democratic (`#5B7FA6`), Republican (`#B56A5E`), Independent (`#8A8D93`).
   - **Visual -> Detail labels:** Show values (Democratic 53, Republican 45, Independent 2).
6. **Position:**
   - `X: 760 px`, `Y: 200 px`, `Width: 500 px`, `Height: 440 px`.

### Step 7: Add "How to read this" Box
1. Ribbon: **Insert** -> **Text box**.
2. Text:
   ```text
   Seats are the races already called. 19 House races and 2 governor races were still uncalled when this data was collected, so the totals will move slightly. The Senate total adds to 100 because all 100 seats are accounted for.
   ```
3. Format: **Segoe UI Regular**, **9 pt**, Color: `#6B7076`.
4. **Position:**
   - `X: 20 px`, `Y: 655 px`, `Width: 1240 px`, `Height: 45 px`.

### Step 8: Save
Press `Ctrl + S` to save `MidtermsObservatory.pbix`.

---

## 6. Next Steps
- Page 1 takes ~5 minutes to build following the checklist above.
- Pages 2 through 7 follow the exact same visual pattern specified in [build_guide.md](file:///C:/Users/shams/us-midterms-2026-observatory/powerbi/build_guide.md).
- Commit and push `MidtermsObservatory.pbix` whenever you complete a page.
