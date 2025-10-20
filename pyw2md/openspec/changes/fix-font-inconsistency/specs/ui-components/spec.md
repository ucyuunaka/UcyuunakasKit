# UI Components Font Standardization

## MODIFIED Requirements
### Requirement: Dynamic Font Methods Only
All UI components SHALL use dynamic font methods instead of static font constants.

#### Scenario: Font Panel Headline Update
**Given** the FileListPanel uses a headline font
**When** the panel initializes
**Then** it SHALL call `MD.get_font_headline()` instead of using `MD.FONT_HEADLINE`

#### Scenario: Button Font Consistency
**Given** the Btn widget needs font configuration
**When** the button is created
**Then** it SHALL use `MD.get_font_ui()` instead of `MD.FONT_UI`

#### Scenario: Status Bar Text
**Given** the StatusBar displays text
**When** the status bar initializes
**Then** it SHALL use `MD.get_font_body()` instead of `MD.FONT_BODY`

### Requirement: Emoji-Free UI
UI components SHALL not use emoji icons or emoji fonts.

#### Scenario: File Management Icons
**Given** the file list panel shows section headers
**When** the header is rendered
**Then** it SHALL use text labels instead of emoji icons like "📂"

#### Scenario: Status Messages
**Given** the application shows status messages
**When** messages are displayed
**Then** they SHALL use text descriptions instead of emoji indicators

#### Scenario: Dialog Titles
**Given** dialogs display titles and icons
**When** dialog content is rendered
**Then** it SHALL not include emoji fonts or characters

### Requirement: Text Label Replacements
Emoji icons SHALL be replaced with descriptive text labels.

#### Scenario: File Management Section
**Given** the file management section uses "📂" icon
**When** the section header is displayed
**Then** it SHALL show "文件管理" text label instead

#### Scenario: Settings Section
**Given** the settings section uses "⚙️" icon
**When** the section header is displayed
**Then** it SHALL show "转换设置" text label instead

#### Scenario: Action Feedback Messages
**Given** operations use emoji for success/failure feedback
**When** feedback messages are displayed
**Then** they SHALL use clear text descriptions instead