# Notifications Center - UI Layout Design

## Overall Layout Structure

### Navigation Header (Sticky, Full Width)
- **Height**: 68px (standard with notification context)
- **Background**: Notification-focused glass (rgba(255, 255, 255, 0.95)) with alert-aware undertones
- **Border**: Alert-responsive bottom border (1px solid rgba(59, 130, 246, 0.09))
- **Shadow**: Notification shadow (0 2px 16px rgba(59, 130, 246, 0.07))

**Components:**
- **Left Section**: 
  - Breadcrumb: "Dashboard > Notifications"
  - Unread count indicator: "23 Unread" with pulsing badge
- **Center Section**: 
  - Notification search bar with type-ahead filtering
  - Quick filter buttons: All, Unread, Critical, Today
- **Right Section**:
  - Mark all read button
  - Notification settings dropdown
  - Export notifications (for audit)
  - Real-time sync indicator (green/amber/red)

### Sidebar (Sticky, Collapsible)
- **Width**: 320px expanded, 64px collapsed
- **Background**: Notification management glass (rgba(248, 250, 252, 0.97))
- **Border**: Alert-aware border (1px solid rgba(59, 130, 246, 0.08))

**Notification Categories:**
1. **All Notifications** (active with count badge)
2. **Critical Alerts** (red badge with count)
3. **AI Insights** (purple badge)
4. **Appointment Updates** (blue badge)
5. **System Messages** (gray badge)
6. **Patient Reminders** (green badge)
7. **Archived** (muted)

**Priority Summary Panel:**
- **Critical**: "5 requiring immediate attention"
- **High**: "12 need review today"
- **Medium**: "34 general notifications"
- **Low**: "67 informational updates"

**Quick Actions:**
- Clear all read notifications
- Notification preferences
- Digest settings
- Do not disturb mode toggle

## Main Content Area

### Notifications Grid Layout (CSS Grid, 16px gap)

#### Row 1: Notification Management Controls (Full Width Card)

**Notification Control Panel**
- **Background**: Control-focused glass with notification accents
- **Height**: 80px
- **Content**:
  - **Left Section**: 
    - View options: All | Unread | Critical | Today (toggle buttons)
    - Sort dropdown: Newest, Oldest, Priority, Category
  - **Center Section**:
    - Bulk selection controls (when notifications selected)
    - Bulk actions: Mark Read, Archive, Delete, Export
  - **Right Section**:
    - Items per page: 25, 50, 100
    - Auto-refresh toggle (30s, 1min, 5min, Off)
    - Notification sound toggle

#### Row 2: Critical Alerts Banner (Full Width, Conditional)

**Critical Alerts Banner** (Only shows when critical alerts exist)
- **Background**: Critical gradient glass (rgba(239, 68, 68, 0.1) to rgba(239, 68, 68, 0.05))
- **Border**: 2px solid rgba(239, 68, 68, 0.3)
- **Height**: 100px
- **Content**:
  - **Alert Header**: "5 Critical Alerts Require Immediate Attention" with pulsing red icon
  - **Critical Alert Preview**:
    - "Patient Johnson - Cardiac emergency in Room 205" (2 min ago)
    - "AI Alert: High readmission risk - Mrs. Chen" (5 min ago)
    - "System Alert: ICU capacity at 98%" (8 min ago)
  - **Action Button**: "Review All Critical Alerts" (prominent red button)
  - **Dismiss Options**: Snooze, Mark as Handled, False Positive

#### Row 3: Notification Feed (Full Width)

**Notification List Container**
- **Background**: Feed-focused glass with scrollable content
- **Height**: Dynamic (minimum 600px, expands based on content)

#### Individual Notification Cards (Within Feed)

**Critical Alert Notification Card**
- **Background**: Critical glass with red accent border (rgba(239, 68, 68, 0.1))
- **Border**: Left border 4px solid #EF4444
- **Height**: 120px
- **Content**:
  - **Header Section**:
    - **Priority Badge**: "CRITICAL" (red badge with alert icon)
    - **Category**: "Patient Alert" (small gray text)
    - **Timestamp**: "2 minutes ago" (red text, urgent)
    - **Status**: Unread indicator (red dot)
  - **Message Section**:
    - **Title**: "Cardiac Emergency - Room 205" (18px, bold)
    - **Content**: "Patient Johnson showing irregular heartbeat patterns. Immediate cardiac consultation required."
    - **Source**: "AI Monitoring System + Dr. Williams" (source attribution)
  - **Action Section**:
    - **Primary Actions**: "Respond Now" (red button), "Assign to Cardiologist" (blue button)
    - **Secondary Actions**: Mark Read, Snooze, Details dropdown
  - **Visual Elements**:
    - Patient photo thumbnail (if available)
    - Location indicator: "Room 205, Cardiac Wing"
    - Urgency timer: "Response needed within 5 minutes"

**AI Insight Notification Card**
- **Background**: AI-focused glass with purple accent (rgba(139, 92, 246, 0.08))
- **Border**: Left border 3px solid #8B5CF6
- **Height**: 100px
- **Content**:
  - **Header Section**:
    - **Priority Badge**: "HIGH" (amber badge with AI sparkle icon)
    - **Category**: "AI Insight" 
    - **Timestamp**: "15 minutes ago"
    - **Status**: Unread indicator (purple dot)
  - **Message Section**:
    - **Title**: "High Readmission Risk Detected" (16px, semibold)
    - **Content**: "Patient Sarah Chen shows 87% probability of readmission within 30 days based on recent vitals and history."
    - **AI Confidence**: "94% prediction accuracy"
  - **Action Section**:
    - **Primary Actions**: "Review Risk Factors" (purple button), "Schedule Follow-up" (blue button)
    - **Secondary Actions**: Mark Read, Share with Team, Learn More

**Appointment Update Card**
- **Background**: Appointment glass with blue accent (rgba(59, 130, 246, 0.08))
- **Border**: Left border 3px solid #3B82F6
- **Height**: 90px
- **Content**:
  - **Header Section**:
    - **Priority Badge**: "MEDIUM" (blue badge with calendar icon)
    - **Category**: "Appointment"
    - **Timestamp**: "1 hour ago"
    - **Status**: Read indicator (gray dot)
  - **Message Section**:
    - **Title**: "Appointment Rescheduled" (16px, semibold)
    - **Content**: "Patient Maria Rodriguez moved appointment from March 15 to March 18 at 2:30 PM."
    - **Details**: "Reason: Schedule conflict"
  - **Action Section**:
    - **Primary Actions**: "Confirm Change" (blue button), "View Schedule" (outline button)
    - **Secondary Actions**: Contact Patient, Add Note

**System Message Card**
- **Background**: System glass with gray accent (rgba(107, 114, 128, 0.08))
- **Border**: Left border 2px solid #6B7280
- **Height**: 80px
- **Content**:
  - **Header Section**:
    - **Priority Badge**: "INFO" (gray badge with info icon)
    - **Category**: "System Update"
    - **Timestamp**: "3 hours ago"
    - **Status**: Read indicator
  - **Message Section**:
    - **Title**: "System Maintenance Complete" (14px, regular)
    - **Content**: "Scheduled maintenance on patient portal completed successfully. All services restored."
  - **Action Section**:
    - **Primary Actions**: "View Details" (gray button)
    - **Secondary Actions**: Archive, Dismiss

**Patient Reminder Card**
- **Background**: Reminder glass with green accent (rgba(34, 197, 94, 0.08))
- **Border**: Left border 3px solid #22C55E
- **Height**: 95px
- **Content**:
  - **Header Section**:
    - **Priority Badge**: "REMINDER" (green badge with bell icon)
    - **Category**: "Patient Care"
    - **Timestamp**: "4 hours ago"
    - **Status**: Unread indicator (green dot)
  - **Message Section**:
    - **Title**: "Medication Review Due" (16px, semibold)
    - **Content**: "Patient David Lee scheduled for medication review today at 3:00 PM. Requires blood pressure medication adjustment."
    - **Patient Info**: "Age 58, Hypertension, Last review 6 months ago"
  - **Action Section**:
    - **Primary Actions**: "Start Review" (green button), "View History" (outline button)
    - **Secondary Actions**: Reschedule, Add Note, Mark Complete

#### Row 4: Notification Statistics & Settings (2 Cards, 60/40 split)

**Notification Analytics (Left, 60% width)**
- **Background**: Analytics glass with notification metrics
- **Height**: 300px
- **Content**:
  - **Header**: "Notification Insights & Trends"
  - **Response Metrics**:
    - **Average Response Time**:
      - Critical alerts: "3.2 minutes" (green, within target)
      - High priority: "47 minutes" (amber, could improve)
      - Medium priority: "4.3 hours" (good)
    - **Resolution Rate**:
      - Critical: "100% resolved" (excellent)
      - High: "89% resolved same day" (good)
      - Medium: "76% resolved within 24h" (acceptable)
  - **Notification Volume Charts**:
    - Daily notification count over 2 weeks (line chart)
    - Notification type distribution (donut chart)
    - Peak notification times (heat map)
  - **Team Performance**:
    - Fastest responder: "Dr. Johnson - avg 2.1 min"
    - Most notifications handled: "Nurse Martinez - 67 today"
    - Department response rates comparison

**Notification Preferences (Right, 40% width)**
- **Background**: Settings-focused glass card
- **Height**: 300px
- **Content**:
  - **Header**: "Notification Settings"
  - **Delivery Preferences**:
    - **In-App Notifications**: Enabled (toggle)
    - **Email Notifications**: Enabled for critical only (dropdown)
    - **SMS Alerts**: Enabled for emergencies (toggle)
    - **Push Notifications**: Enabled (toggle)
  - **Priority Thresholds**:
    - **Critical**: Patient emergencies, system failures
    - **High**: AI insights, urgent appointments
    - **Medium**: Schedule changes, reminders
    - **Low**: System updates, informational
  - **Quiet Hours Settings**:
    - **Do Not Disturb**: 10 PM - 6 AM (time picker)
    - **Emergency Override**: Always allow critical (checkbox)
    - **Weekend Settings**: Reduced notifications (toggle)
  - **Digest Settings**:
    - **Daily Summary**: Enabled, 8:00 AM (time picker)
    - **Weekly Report**: Enabled, Monday 9:00 AM
  - **Custom Rules**: "Set up advanced notification rules" link

## Notification Design Specifications

### Priority Badge System
- **CRITICAL**: Red badge (#EF4444) with white text and alert triangle icon
- **HIGH**: Amber badge (#F59E0B) with white text and exclamation icon  
- **MEDIUM**: Blue badge (#3B82F6) with white text and info icon
- **LOW/INFO**: Gray badge (#6B7280) with white text and bell icon
- **REMINDER**: Green badge (#22C55E) with white text and clock icon

### Notification Status Indicators
- **Unread**: Colored dot matching priority (red, amber, blue, gray, green)
- **Read**: Gray dot with reduced opacity
- **Archived**: No dot, muted text colors
- **Snoozed**: Clock icon with snooze duration
- **In Progress**: Spinner icon with progress indicator

### Card Interaction States
- **Default**: Clean glass card with priority border
- **Hover**: Gentle lift (translateY(-1px)) with increased shadow
- **Selected**: Blue outline with selection checkmark
- **Read**: Reduced opacity (85%) with muted colors
- **Expired**: Strike-through effect with faded appearance

### Typography Hierarchy
- **Critical Titles**: Inter, 700 weight, 18px (urgent emphasis)
- **Standard Titles**: Inter, 600 weight, 16px (clear identification)
- **Content Text**: Inter, 400 weight, 14px (readable information)
- **Metadata**: Inter, 400 weight, 12px, muted colors (timestamps, sources)
- **Priority Badges**: Inter, 600 weight, 10px, uppercase (clear status)

### Responsive Notification Layout
- **Large Desktop**: Full card layout with expanded actions
- **Desktop**: Standard layout as described
- **Tablet**: Condensed cards with primary actions only
- **Mobile**: Stacked list with swipe actions for management

### Real-Time Features
- **Live Updates**: New notifications slide in from top
- **Sound Alerts**: Configurable audio alerts by priority
- **Visual Alerts**: Browser tab notifications and favicon badges
- **Auto-Refresh**: Configurable refresh intervals with manual override
- **Offline Queue**: Store notifications when offline, sync when connected

### Accessibility Features
- **Screen Reader Support**: Complete ARIA labeling for all notifications
- **Keyboard Navigation**: Full interface navigation without mouse
- **High Contrast Mode**: Enhanced visibility for priority indicators
- **Focus Management**: Clear focus indicators and logical tab order
- **Voice Announcements**: Optional audio reading of critical notifications

### Performance Optimization
- **Virtual Scrolling**: Efficient rendering of large notification lists
- **Lazy Loading**: Load notification details on demand
- **Smart Caching**: Cache frequently accessed notification data
- **Background Sync**: Non-blocking notification fetching
- **Compression**: Optimize notification payload sizes

## Notification Center Philosophy

The Notifications Center serves as the central nervous system for HealthSphere AI that:

1. **Prioritizes Patient Safety**: Critical alerts always receive immediate attention
2. **Reduces Information Overload**: Smart filtering and prioritization systems
3. **Enables Rapid Response**: Quick actions directly from notification cards
4. **Supports Clinical Workflow**: Seamless integration with patient care processes
5. **Maintains Situational Awareness**: Comprehensive view of all healthcare activities
6. **Prevents Alert Fatigue**: Intelligent notification management and customization
7. **Ensures Compliance**: Audit trails and response tracking for regulatory requirements

The interface creates an intelligent notification ecosystem that keeps healthcare teams informed without overwhelming them, maintaining the calm, professional aesthetic while ensuring critical information is never missed. The design balances comprehensive alert management with the clear, trustworthy communication essential for healthcare environments.