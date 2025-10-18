## ADDED Requirements

### Requirement: Persistent Notification Bar
The UI SHALL provide a persistent notification bar that remains visible at all times without causing layout reflow.

#### Scenario: Notification bar is always visible
- **GIVEN** the application is running
- **WHEN** no operations are in progress
- **THEN** the notification bar displays default status information
- **AND** the notification bar does not disappear

#### Scenario: Notification bar updates without flicker
- **GIVEN** the notification bar is visible
- **WHEN** a refresh operation completes
- **THEN** the notification content updates smoothly
- **AND** no layout reflow occurs

### Requirement: Smooth Content Transitions
The notification bar SHALL update content with smooth transitions to eliminate visual flickering.

#### Scenario: Content fade transition
- **GIVEN** the notification bar is showing content
- **WHEN** new notification content is available
- **THEN** the old content fades out over 200ms
- **AND** the new content fades in over 200ms
- **AND** the transition appears smooth without flashing

## MODIFIED Requirements

### Requirement: Notification Bar Layout
The notification bar MUST be positioned at the bottom of the main window to avoid covering primary content.

#### Scenario: Bottom positioning
- **GIVEN** the main application window
- **WHEN** the notification bar is created
- **THEN** it occupies the bottom row of the grid layout
- **AND** it does not overlap with file list or control panel
- **AND** its height remains constant regardless of content

#### Scenario: Grid layout stability
- **GIVEN** the application uses grid layout
- **WHEN** notification bar visibility or content changes
- **THEN** the grid structure remains unchanged
- **AND** no widgets are repositioned
- **AND** no resize events are triggered