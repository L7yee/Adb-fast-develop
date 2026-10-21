# Design Direction

## Product Mood

- **Tone**: Technical, efficient, no-nonsense
- **Personality**: Like a well-organized workbench - tools laid out clearly, ready to use
- **Audience Connection**: Speaks to engineers who want results, not decoration
- **Feel**: Dark-themed dashboard with high contrast for long debugging sessions

## Visual Principles

1. **Clarity over cleverness**: Every element has a purpose; no decorative flourishes
2. **Information density**: Show enough to be useful, not so much it's overwhelming
3. **Immediate feedback**: Visual state changes clearly indicate what's happening
4. **Touch targets**: Cards sized for easy clicking, not cramped
5. **Monospace reverence**: Terminal output is the hero; give it space and respect

## Typography Direction

- **Primary font**: System UI font (Segoe UI on Windows) for UI elements - familiar and readable
- **Output font**: Monospace font (Consolas or JetBrains Mono) for terminal output area
- **Hierarchy**:
  - Title: Bold, larger
  - Card labels: Medium weight, sentence case
  - Status text: Regular weight, smaller
  - Output: Monospace, regular weight

## Color And Material Direction

- **Base palette**: Dark theme as default
  - Background: Dark gray (#1e1e1e or similar)
  - Surface/Card: Slightly lighter gray (#2d2d2d)
  - Accent: Blue or teal for interactive elements (#0078d4 or similar)
  - Success: Green (#4caf50)
  - Error: Red (#f44336)
  - Warning: Amber (#ff9800)
- **Text colors**:
  - Primary text: White or near-white (#ffffff, #e0e0e0)
  - Secondary text: Muted gray (#9e9e9e)
  - Output text: Green-on-black terminal style or white-on-dark
- **Cards**: Subtle elevation via border or slight shadow, hover state with accent border

## Layout Direction

- **Window**: Single window, resizable, minimum size ~800x600
- **Structure**:
  - Header bar: App title, device status indicator, refresh button
  - Main area split:
    - Left panel: Command cards grid (scrollable if needed)
    - Right panel: Output area with toolbar (save, copy, clear)
- **Card grid**: 2 columns recommended, responsive to window width
- **Output panel**: Takes majority of horizontal space, fixed monospace area with scrollbar

## Interaction Direction

- **Command execution**: Single click on card to execute
- **Streaming control**: Stop button appears when streaming command is active
- **Auto-refresh control**:
  - Toggle switch or button on command cards that support polling
  - Interval dropdown (1s, 5s, 10s, 30s) adjacent to toggle
  - Visual indicator (pulsing dot or rotating arrow) when auto-refresh is active
  - Auto-refresh state resets when switching commands
- **Export actions**: Toolbar buttons with icons + tooltips (no nested menus)
- **Keyboard support**:
  - Ctrl+S: Save output
  - Ctrl+C: Copy output (when output area focused)
  - Escape: Stop streaming command or auto-refresh
- **Feedback patterns**:
  - Card click: Brief visual press state
  - Running: Spinner or pulsing indicator
  - Complete: Checkmark or green flash
  - Error: Red highlight with error message in output
  - Auto-refresh active: Subtle pulse animation on card, timestamp of last refresh

## Component Language

- **Command Card**:
  - Rectangular, rounded corners (4-6px)
  - Icon + label (simple, clear)
  - Hover: accent border, slight lift
  - Active/running: accent glow or border pulse
- **Output Area**:
  - Monospace text field, read-only
  - Dark background (terminal aesthetic)
  - Line numbers optional but not required
  - Scrollbar always visible when content overflows
- **Status Indicator**:
  - Compact pill or dot with label
  - Green = connected, Gray = disconnected, Red = error
- **Auto-refresh Controls**:
  - Toggle switch: Compact, inline with card title or in card footer
  - Interval selector: Small dropdown, default 5 seconds
  - Active indicator: Small animated dot or icon in card corner
- **Toolbar Buttons**:
  - Icon-only with tooltips
  - Disabled state when no output to export

## Accessibility And Responsiveness

- **Minimum window size**: Enforce minimum to prevent layout collapse
- **Tab navigation**: Cards should be tab-navigable for keyboard users
- **Focus indicators**: Clear focus outline on keyboard navigation
- **Color contrast**: Ensure WCAG AA compliance for text contrast
- **No animations**: Keep interactions instant; avoid motion that could distract

## Anti-Patterns To Avoid

1. **Do not** use white/light backgrounds as default - engineers prefer dark themes for extended use
2. **Do not** auto-scroll output to bottom when user has scrolled up - let them read
3. **Do not** show modal dialogs for routine errors - display inline in output area
4. **Do not** use hamburger menus or hidden navigation - all commands visible at all times
5. **Do not** add decorative progress bars or fake loading states
6. **Do not** parse or prettify command output without user request - raw output is the goal
7. **Do not** use tiny touch targets or cramped layouts - generous spacing for quick interaction
8. **Do not** auto-execute commands on selection - require explicit click
9. **Do not** persist output between command runs - clear automatically or with user action
10. **Do not** block the UI during command execution - use async/threaded execution
11. **Do not** auto-refresh by default - require explicit user action to enable polling
12. **Do not** auto-refresh streaming commands like `getevent -l` - they already provide real-time output
