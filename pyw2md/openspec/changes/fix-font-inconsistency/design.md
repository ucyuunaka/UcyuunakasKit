# Font Consistency Design

## Architectural Decisions

### 1. Emoji Removal Strategy
**Decision**: Complete removal of emoji from UI components
**Rationale**:
- Emoji fonts ("Segoe UI Emoji") use fixed sizes that don't scale with DPI
- Cultural and accessibility concerns with emoji usage
- Professional appearance without emoji icons

**Implementation**:
- Replace emoji icons with text labels or simple symbols
- Remove all "Segoe UI Emoji" font references
- Update placeholder text and user messages

### 2. Chinese Font Stack Enhancement
**Decision**: Improve font stacks with Chinese font priority
**Rationale**:
- Current font stacks prioritize Latin fonts
- Poor Chinese text rendering in existing setup
- Need proper fallback mechanisms

**Font Stack Design**:
```
UI Fonts: "Microsoft YaHei UI, Segoe UI, system-ui, -apple-system, PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif"
Mono Fonts: "Cascadia Code Mono, Consolas, 'Microsoft YaHei Mono', 'Courier New', monospace"
```

### 3. Dynamic Font Standardization
**Decision**: Enforce dynamic font methods across all components
**Rationale**:
- 15 instances of deprecated static font constants
- Static fonts don't respect DPI scaling
- Inconsistent sizing across components

**Migration Pattern**:
```python
# Before (deprecated)
font=MD.FONT_HEADLINE
font=("Segoe UI Emoji", 16)

# After (dynamic)
font=MD.get_font_headline()
font=MD.get_font_ui()
```

## Impact Analysis

### Files Affected
1. `ui/app.py` - 1 static font + 1 emoji
2. `ui/widgets/material_card.py` - 1 static font
3. `ui/components/status_bar.py` - 1 static font
4. `ui/components/file_list_panel.py` - 3 static fonts + multiple emoji
5. `ui/components/control_panel.py` - 4 static fonts + 1 emoji
6. `ui/components/dialogs.py` - 3 static fonts
7. `config/theme.py` - Font stack updates

### Breaking Changes
- None - internal font handling changes only
- User-facing visual improvements only

### Performance Impact
- Minimal - font method calls are lightweight
- Improved consistency reduces layout recalculation

## Testing Strategy
- Visual regression testing across different DPI scales
- Chinese font rendering verification
- Component font size consistency validation