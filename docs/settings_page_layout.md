# Settings Page - UI Layout Design

## Overall Layout Structure

### Navigation Header (Sticky, Full Width)
- **Height**: 68px (standard with settings context)
- **Background**: Settings-focused glass (rgba(255, 255, 255, 0.95)) with configuration undertones
- **Border**: Clean bottom border (1px solid rgba(59, 130, 246, 0.09))
- **Shadow**: Configuration shadow (0 2px 16px rgba(59, 130, 246, 0.07))

**Components:**
- **Left Section**: 
  - Breadcrumb: "Dashboard > Settings"
  - Settings sync status indicator (saved/syncing/error)
- **Center Section**: 
  - Active tab indicator showing current settings section
  - Quick search within settings
- **Right Section**:
  - Unsaved changes indicator (amber badge when present)
  - "Save All Changes" button (green, when changes exist)
  - "Reset to Defaults" button (outline)
  - Settings help/documentation link

### Sidebar (Sticky, Collapsible)
- **Width**: 300px expanded, 64px collapsed
- **Background**: Settings navigation glass (rgba(248, 250, 252, 0.97))
- **Border**: Configuration border (1px solid rgba(59, 130, 246, 0.08))

**Settings Navigation Tabs:**
1. **Profile & Account** (active state)
2. **Notification Preferences**
3. **System Configuration**
4. **Privacy & Security** 
5. **Appearance & Display**
6. **Integration Settings**
7. **Backup & Data**
8. **Advanced Options**

**Quick Settings Panel:**
- Dark mode toggle
- Language selector
- Time zone display
- Auto-save indicator
- Last backup status

## Main Content Area

### Settings Grid Layout (CSS Grid, 20px gap)

#### Tab Navigation Bar (Full Width)

**Tab Selection Interface**
- **Background**: Tab navigation glass with active state indicators
- **Height**: 60px
- **Content**:
  - **Tab Buttons**: Horizontal scrollable tab bar
    - Profile & Account (active)
    - Notifications 
    - System Config
    - Privacy & Security
    - Appearance
    - Integrations
    - Backup & Data
    - Advanced
  - **Tab Indicators**: Active tab highlighted with blue accent
  - **Tab Badges**: Change indicators and notification counts

---

## Profile & Account Tab (Active)

#### Row 1: Personal Information (Full Width Card)

**User Profile Management Card**
- **Background**: Profile-focused glass with user account accents
- **Height**: 300px
- **Content**:
  - **Left Section (Profile Photo, 30%)**:
    - **Profile Photo**: Large circular photo (120px) with edit overlay
    - **Photo Controls**: 
      - "Change Photo" button
      - "Remove Photo" link
      - File format requirements
    - **Account Status**: "Active" with green badge
    - **Member Since**: "January 15, 2024"
  - **Center Section (Basic Info, 40%)**:
    - **Form Fields**:
      - Full Name: "Dr. Sarah Elizabeth Johnson" (editable)
      - Display Name: "Dr. Johnson" (editable)
      - Email: "s.johnson@healthsphere.ai" (verified badge)
      - Phone: "(555) 123-4567" (editable)
      - Employee ID: "EMP-2847" (read-only)
      - Department: "Cardiology" (dropdown selector)
    - **Field Validation**: Real-time validation with clear error states
  - **Right Section (Professional Info, 30%)**:
    - **Professional Details**:
      - Position: "Senior Cardiologist" (editable)
      - License Number: "MD-12345-CA" (editable)
      - Specializations: Tags with add/remove capability
      - Years of Experience: "12 years" (editable)
    - **Emergency Contact**: 
      - Name: "John Johnson" (editable)
      - Relationship: "Spouse" (dropdown)
      - Phone: "(555) 987-6543" (editable)

#### Row 2: Account Management (2 Cards, 50/50 split)

**Account Security (Left, 50% width)**
- **Background**: Security-focused glass card
- **Height**: 280px
- **Content**:
  - **Header**: "Account Security"
  - **Password Management**:
    - **Current Password Status**: "Last changed 45 days ago"
    - **Change Password Button**: Opens secure password change modal
    - **Password Requirements**: Display of security requirements
  - **Two-Factor Authentication**:
    - **Status**: "Enabled" (green badge)
    - **Method**: "Authenticator App + SMS Backup"
    - **Manage 2FA Button**: Configure authentication methods
    - **Backup Codes**: "Generate new backup codes" link
  - **Login Activity**:
    - **Recent Sessions**: List of last 3 login sessions
    - **Device Management**: "Manage trusted devices" link
    - **Suspicious Activity**: "No suspicious activity detected"
  - **Account Recovery**:
    - **Recovery Email**: Verified secondary email
    - **Security Questions**: "2 questions configured"

**Account Preferences (Right, 50% width)**
- **Background**: Preferences-focused glass card  
- **Height**: 280px
- **Content**:
  - **Header**: "Account Preferences"
  - **Language & Region**:
    - **Language**: "English (US)" (dropdown selector)
    - **Time Zone**: "Pacific Standard Time" (auto-detect toggle)
    - **Date Format**: "MM/DD/YYYY" (format selector)
    - **Time Format**: "12-hour" (12/24 hour toggle)
  - **Communication Preferences**:
    - **Preferred Contact Method**: Email (radio buttons)
    - **Marketing Communications**: Opt-out toggle
    - **Product Updates**: Enabled (toggle)
    - **Research Participation**: Opt-in toggle
  - **Accessibility Options**:
    - **High Contrast Mode**: Disabled (toggle)
    - **Large Text**: Standard (size selector)
    - **Screen Reader Support**: Auto-detect (toggle)
    - **Keyboard Navigation**: Enhanced (toggle)

---

## Notifications Tab (Secondary)

#### Notification Delivery Settings (Full Width Card)

**Comprehensive Notification Management**
- **Background**: Notification settings glass
- **Height**: 450px
- **Content**:
  - **Delivery Method Matrix**:
    - **Column Headers**: In-App, Email, SMS, Push
    - **Row Categories**:
      - Critical Patient Alerts: [✓] [✓] [✓] [✓] (all enabled)
      - AI Insights & Recommendations: [✓] [✓] [✗] [✓] 
      - Appointment Updates: [✓] [✓] [✗] [✗]
      - System Messages: [✓] [✗] [✗] [✗]
      - Patient Messages: [✓] [✓] [✗] [✓]
      - Schedule Changes: [✓] [✓] [✗] [✗]
  - **Notification Timing**:
    - **Quiet Hours**: 10:00 PM - 6:00 AM (time range picker)
    - **Weekend Settings**: "Reduced notifications" (toggle)
    - **Emergency Override**: "Always allow critical alerts" (toggle)
    - **Digest Settings**: "Daily summary at 8:00 AM" (enabled)
  - **Advanced Options**:
    - **Smart Grouping**: Group similar notifications (toggle)
    - **Auto-Archive**: Archive read notifications after 30 days
    - **Sound Alerts**: Custom sounds by priority level
    - **Vibration Patterns**: Different patterns for different alert types

---

## System Configuration Tab (Secondary)

#### System Behavior Settings (2 Cards, 60/40 split)

**Interface Preferences (Left, 60% width)**
- **Background**: Interface settings glass
- **Height**: 350px
- **Content**:
  - **Header**: "Interface & Behavior"
  - **Dashboard Settings**:
    - **Default Dashboard View**: "Hospital Administration" (dropdown)
    - **Card Layouts**: "Compact" vs "Comfortable" (radio buttons)
    - **Auto-refresh Interval**: "5 minutes" (dropdown: 1min, 5min, 15min, Off)
    - **Show Tooltips**: Enabled (toggle)
  - **Data Display**:
    - **Items Per Page**: "25" (dropdown: 10, 25, 50, 100)
    - **Date Range Defaults**: "Last 30 days" (preset selector)
    - **Chart Animations**: Enabled (toggle)
    - **Real-time Updates**: Enabled (toggle)
  - **Workflow Preferences**:
    - **Auto-save Forms**: Enabled every 30 seconds
    - **Confirm Destructive Actions**: Enabled (toggle)
    - **Remember Filter Settings**: Enabled (toggle)
    - **Quick Action Shortcuts**: Show keyboard shortcuts (toggle)

**Performance Settings (Right, 40% width)**
- **Background**: Performance glass card
- **Height**: 350px
- **Content**:
  - **Header**: "Performance & Storage"
  - **Cache Settings**:
    - **Browser Cache**: "Enabled" (clear cache button)
    - **Image Optimization**: "Auto" (Auto/High Quality/Fast Loading)
    - **Offline Mode**: "Limited functionality" (toggle)
  - **Data Sync**:
    - **Background Sync**: Enabled (toggle)
    - **Sync Frequency**: "Every 15 minutes" (dropdown)
    - **Data Usage**: "Optimized" (Full/Optimized/Minimal)
  - **Storage Management**:
    - **Local Storage Used**: "245 MB of 2 GB"
    - **Clear Stored Data**: Button with confirmation
    - **Export User Data**: Generate data export

---

## Privacy & Security Tab (Secondary)

#### Data Privacy Controls (Full Width Card)

**Privacy Management Dashboard**
- **Background**: Privacy-focused glass with security accents
- **Height**: 400px
- **Content**:
  - **Data Access & Sharing**:
    - **Data Sharing Consent**: Granular controls for different data types
      - Clinical data for AI improvements: Opt-in (toggle)
      - Usage analytics: Enabled (toggle) 
      - Research participation: Opt-in (toggle)
    - **Third-party Integrations**: List of connected services with revoke options
  - **Audit & Transparency**:
    - **Data Access Log**: "View who accessed your data" link
    - **Data Usage Report**: "Download your data usage report"
    - **Privacy Policy**: "Last updated February 1, 2026" with view link
  - **Rights Management**:
    - **Data Portability**: "Export my data" button
    - **Data Deletion**: "Request account deletion" (with 30-day retention notice)
    - **Consent Withdrawal**: "Manage consents" detailed controls

---

## Appearance Tab (Secondary)

#### Visual Customization (2 Cards, 50/50 split)

**Theme & Display (Left, 50% width)**
- **Background**: Theme customization glass
- **Height**: 320px
- **Content**:
  - **Header**: "Visual Appearance"
  - **Theme Selection**:
    - **Color Scheme**: Light (selected), Dark, Auto (radio buttons)
    - **Accent Color**: Blue (selected), Green, Purple, Teal (color swatches)
    - **Healthcare Theme**: "Professional" (dropdown: Professional, Warm, Modern)
  - **Typography**:
    - **Font Size**: "Standard" (Small, Standard, Large, Extra Large)
    - **Font Family**: "Inter" (System, Inter, Open Sans)
    - **Line Spacing**: "Comfortable" (Compact, Standard, Comfortable)
  - **Layout Density**:
    - **Sidebar Width**: "Standard" (Narrow, Standard, Wide)
    - **Card Spacing**: "Standard" (Compact, Standard, Spacious)
    - **Table Row Height**: "Comfortable" (Compact, Standard, Comfortable)

**Visual Elements (Right, 50% width)**
- **Background**: Visual elements glass
- **Height**: 320px
- **Content**:
  - **Header**: "Interface Elements"
  - **Animation Preferences**:
    - **Page Transitions**: Enabled (toggle)
    - **Hover Effects**: Enabled (toggle)
    - **Loading Animations**: Enabled (toggle)
    - **Reduced Motion**: Disabled (accessibility toggle)
  - **Visual Indicators**:
    - **Status Badges**: Full color (Full Color, Subtle, Minimal)
    - **Progress Indicators**: Animated (Static, Animated)
    - **Chart Styles**: "Modern" (Classic, Modern, Minimal)
  - **Customization**:
    - **Custom CSS**: "Advanced styling options" (for power users)
    - **Reset to Defaults**: "Restore original appearance"

#### Settings Action Bar (Full Width)

**Settings Management Controls**
- **Background**: Action-focused glass with save state indicators
- **Height**: 80px
- **Content**:
  - **Left Section**: 
    - Change indicator: "3 unsaved changes" (amber badge)
    - Last saved: "2 minutes ago" (gray text)
  - **Center Section**:
    - Settings validation status: "All settings valid" (green checkmark)
    - Conflict resolution: Shows if settings conflict exists
  - **Right Section**:
    - **Primary Actions**:
      - "Save Changes" (green button, prominent when changes exist)
      - "Discard Changes" (outline button)
    - **Secondary Actions**:
      - "Export Settings" (for backup/sharing)
      - "Import Settings" (restore from backup)
      - "Reset All" (red outline, with confirmation)

## Settings Design Specifications

### Tab Navigation Design
- **Active Tab**: Blue accent background with white text
- **Inactive Tabs**: Transparent with blue text, hover brightens background
- **Tab Indicators**: Small badge for unsaved changes, notification counts
- **Responsive Behavior**: Horizontal scroll on smaller screens

### Form Element Standards
- **Input Fields**: Glass styling with subtle borders, focus states with blue accent
- **Toggles**: iOS-style switches with smooth animation
- **Dropdowns**: Native styling with custom arrow, smooth open animation
- **Radio Buttons**: Custom styled with blue accent when selected
- **Checkboxes**: Custom styled with smooth check animation

### Settings Card Layout
- **Card Headers**: Clear section identification with optional icons
- **Form Sections**: Logical grouping with subtle dividers
- **Help Text**: Contextual help below form elements
- **Validation**: Real-time validation with clear success/error states

### Color System for Settings
- **Success**: #10B981 (saved changes, valid settings)
- **Warning**: #F59E0B (unsaved changes, review needed)
- **Error**: #EF4444 (invalid settings, failed saves)
- **Info**: #3B82F6 (informational messages, help text)
- **Neutral**: #6B7280 (labels, secondary text)

### Settings Typography
- **Section Headers**: Inter, 600 weight, 18px (clear organization)
- **Form Labels**: Inter, 500 weight, 14px (readable identification)
- **Input Text**: Inter, 400 weight, 14px (user input)
- **Help Text**: Inter, 400 weight, 12px, muted colors (guidance)
- **Status Messages**: Inter, 500 weight, 13px, colored (feedback)

### Responsive Settings Layout
- **Large Desktop**: Full two-column layout with expanded forms
- **Desktop**: Standard layout as described
- **Tablet**: Single column with collapsed form sections
- **Mobile**: Stacked layout with touch-optimized form elements

### Settings Persistence
- **Auto-save**: Automatic saving for non-critical changes
- **Manual Save**: Explicit save for security and critical settings
- **Change Tracking**: Clear indication of what has changed
- **Conflict Resolution**: Handle concurrent changes gracefully
- **Backup**: Regular backup of settings with restore capabilities

### Accessibility in Settings
- **Keyboard Navigation**: Full form navigation with logical tab order
- **Screen Reader Support**: Complete ARIA labeling for all form elements
- **Focus Management**: Clear focus indicators and focus trapping in modals
- **High Contrast**: Enhanced visibility for all form elements
- **Voice Commands**: Optional voice control for settings changes

## Settings Page Philosophy

The Settings Page serves as the control center for user personalization that:

1. **Empowers User Control**: Comprehensive customization without overwhelming complexity
2. **Maintains Security Standards**: Robust security settings with clear guidance
3. **Supports Accessibility**: Universal design for all healthcare workers
4. **Enables Workflow Optimization**: Settings that adapt to individual work patterns
5. **Ensures Data Privacy**: Transparent control over personal and clinical data
6. **Facilitates System Integration**: Seamless connection with healthcare workflows
7. **Provides Change Management**: Clear tracking and management of setting modifications

The interface creates a comprehensive yet approachable settings environment that enables healthcare professionals to customize their HealthSphere AI experience while maintaining the security, privacy, and workflow efficiency essential for healthcare environments. The design balances extensive customization options with the calm, professional aesthetic that supports confident configuration management.