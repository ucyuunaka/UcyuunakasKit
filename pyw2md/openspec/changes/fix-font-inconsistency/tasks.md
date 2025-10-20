# Font Consistency Implementation Tasks

## Phase 1: Theme Configuration Updates
- [ ] Update UI font stack with Chinese font priority
- [ ] Update monospace font stack with Chinese fallback
- [ ] Adjust base font sizes for better DPI scaling
- [ ] Mark static font constants as deprecated
- [ ] Test theme configuration loading

## Phase 2: UI Component Static Font Replacement
- [ ] Replace `MD.FONT_UI` with `MD.get_font_ui()` (4 instances)
  - [ ] ui/widgets/material_card.py
  - [ ] ui/components/control_panel.py (2 instances)
  - [ ] ui/components/control_panel.py (additional instance)
- [ ] Replace `MD.FONT_BODY` with `MD.get_font_body()` (3 instances)
  - [ ] ui/components/status_bar.py
  - [ ] ui/components/file_list_panel.py
  - [ ] ui/components/dialogs.py
- [ ] Replace `MD.FONT_HEADLINE` with `MD.get_font_headline()` (3 instances)
  - [ ] ui/components/file_list_panel.py
  - [ ] ui/components/control_panel.py
  - [ ] ui/components/dialogs.py
- [ ] Replace `MD.FONT_TITLE` with `MD.get_font_title()` (1 instance)
  - [ ] ui/components/control_panel.py
- [ ] Replace `MD.FONT_LABEL` with `MD.get_font_label()` (1 instance)
  - [ ] ui/app.py
- [ ] Replace `MD.FONT_MONO` with `MD.get_font_mono()` (3 instances)
  - [ ] ui/components/dialogs.py

## Phase 3: Emoji Removal
- [ ] Remove emoji from app.py drag-drop hint
- [ ] Replace "📂" with "文件管理" in file_list_panel.py
- [ ] Replace "⚙️" with "转换设置" in control_panel.py
- [ ] Remove "Segoe UI Emoji" font references
- [ ] Update search placeholder text
- [ ] Replace emoji status messages with text descriptions

## Phase 4: Validation and Testing
- [ ] Test font rendering at different DPI scales (100%, 125%, 150%, 200%)
- [ ] Verify Chinese text display quality
- [ ] Check component font size consistency
- [ ] Validate UI layout remains intact
- [ ] Perform visual regression testing

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