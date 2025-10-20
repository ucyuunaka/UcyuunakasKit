# Font Consistency Implementation Tasks

## Phase 1: Theme Configuration Updates
- [x] Update UI font stack with Chinese font priority
- [x] Update monospace font stack with Chinese fallback
- [x] Adjust base font sizes for better DPI scaling
- [x] Mark static font constants as deprecated
- [x] Test theme configuration loading

## Phase 2: UI Component Static Font Replacement
- [x] Replace `MD.FONT_UI` with `MD.get_font_ui()` (4 instances)
  - [x] ui/widgets/material_card.py
  - [x] ui/components/control_panel.py (2 instances)
  - [x] ui/components/control_panel.py (additional instance)
- [x] Replace `MD.FONT_BODY` with `MD.get_font_body()` (3 instances)
  - [x] ui/components/status_bar.py
  - [x] ui/components/file_list_panel.py
  - [x] ui/components/dialogs.py
- [x] Replace `MD.FONT_HEADLINE` with `MD.get_font_headline()` (3 instances)
  - [x] ui/components/file_list_panel.py
  - [x] ui/components/control_panel.py
  - [x] ui/components/dialogs.py
- [x] Replace `MD.FONT_TITLE` with `MD.get_font_title()` (1 instance)
  - [x] ui/components/control_panel.py
- [x] Replace `MD.FONT_LABEL` with `MD.get_font_label()` (1 instance)
  - [x] ui/app.py
- [x] Replace `MD.FONT_MONO` with `MD.get_font_mono()` (3 instances)
  - [x] ui/components/dialogs.py

## Phase 3: Emoji Removal
- [x] Remove emoji from app.py drag-drop hint
- [x] Replace "📂" with "文件管理" in file_list_panel.py
- [x] Replace "⚙️" with "转换设置" in control_panel.py
- [x] Remove "Segoe UI Emoji" font references
- [x] Update search placeholder text
- [x] Replace emoji status messages with text descriptions

## Phase 4: Validation and Testing
- [x] Test font rendering at different DPI scales (100%, 125%, 150%, 200%)
- [x] Verify Chinese text display quality
- [x] Check component font size consistency
- [x] Validate UI layout remains intact
- [x] Perform visual regression testing

## Dependencies
- Requires font-scaling spec compliance
- Depends on DPI detection system
- Theme configuration must be updated first

## Validation Criteria
- All 15 static font constants replaced
- Zero emoji characters in UI code
- Chinese fonts render properly
- Consistent font sizes across DPI scales
- No visual layout breaks