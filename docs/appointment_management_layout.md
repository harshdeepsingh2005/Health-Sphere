# Appointment Management Page - UI Layout Design

## Overall Layout Structure

### Navigation Header (Sticky, Full Width)
- **Height**: 68px (expanded for appointment context)
- **Background**: Scheduling-focused glass (rgba(255, 255, 255, 0.94)) with time-aware blue undertone
- **Border**: Clean bottom border (1px solid rgba(59, 130, 246, 0.09))
- **Shadow**: Professional scheduling shadow (0 2px 14px rgba(0, 0, 0, 0.05))

**Components:**
- **Left Section**: 
  - Breadcrumb: "Dashboard > Appointments"
  - Current date/time display with live clock
- **Center Section**: 
  - Global patient/appointment search
  - Quick date navigator (Today, Tomorrow, This Week)
- **Right Section**:
  - Appointment conflicts indicator (amber alert if any)
  - "New Appointment" prominent button (green)
  - Calendar sync status
  - View switcher (Calendar/List/Timeline)

### Sidebar (Sticky, Collapsible)
- **Width**: 300px expanded, 64px collapsed
- **Background**: Appointment management glass (rgba(248, 250, 252, 0.97))
- **Border**: Scheduling border (1px solid rgba(59, 130, 246, 0.07))

**Navigation Sections:**
1. **Appointment Views**
   - Today's Schedule (active)
   - Weekly View
   - Monthly Calendar
   - Available Slots
2. **Management Tools**
   - Patient Search
   - Room/Resource Booking
   - Staff Scheduling
   - Appointment Types
3. **Quick Actions Panel**
   - Recent patients list
   - Favorite appointment types
   - Emergency slot creation

## Main Content Area

### Appointment Management Grid Layout (CSS Grid, 18px gap)

#### Header Section: Appointment Controls (Full Width Card)

**Scheduling Control Panel**
- **Background**: Control-focused glass with scheduling accents
- **Height**: 100px
- **Content**:
  - **Left Section**: 
    - View mode toggle: Calendar | List | Timeline (active states)
    - Date range selector with preset options
    - "Today" quick return button
  - **Center Section**:
    - Time slot availability indicator
    - Current timezone display
    - Sync status with external calendars
  - **Right Section**:
    - Filter dropdown (All, By Provider, By Type, By Status)
    - Export appointments button
    - Print schedule button
    - Settings gear for appointment preferences

#### Row 1: Calendar & Schedule Management (Main View)

**Dynamic View Container (Full Width)**
- **Background**: Adaptive glass based on view mode
- **Height**: 600px (expandable)

#### Calendar View Mode (Default)
**Calendar Grid Interface**
- **Header**: Month/Week navigation with arrow controls
- **Time Grid Layout**:
  - **Left Column**: Time slots (8:00 AM - 6:00 PM) with 15-minute increments
  - **Top Row**: Date headers with day names
  - **Grid Cells**: Available/booked time slots
- **Appointment Blocks**:
  - **Color Coding**: 
    - Patient appointments: Blue
    - Administrative time: Gray
    - Blocked/unavailable: Red stripes
    - Tentative/pending: Yellow outline
  - **Appointment Cards** (within time slots):
    - Patient name (truncated if long)
    - Appointment type (Physical, Consultation, Follow-up)
    - Duration indicator
    - Status badge (Confirmed, Pending, Cancelled)
- **Interaction Features**:
  - Drag-and-drop rescheduling
  - Click to view appointment details
  - Double-click to create new appointment
  - Right-click context menu for actions

#### List View Mode (Alternative)
**Appointment List Interface**
- **List Header**: Sortable columns (Time, Patient, Provider, Type, Status)
- **Appointment Rows**:
  - Time slot with duration
  - Patient name with photo thumbnail
  - Appointment type and reason
  - Assigned provider
  - Status with action buttons
  - Quick actions (Reschedule, Cancel, Complete)
- **Grouping Options**: By day, by provider, by appointment type
- **Pagination**: For large appointment lists

#### Timeline View Mode (Alternative)
**Timeline Interface**
- **Provider Rows**: Each row represents a provider's schedule
- **Time Axis**: Horizontal timeline with clear time markers
- **Appointment Blocks**: Positioned along timeline with patient info
- **Overlap Visualization**: Clear indication of scheduling conflicts
- **Resource Allocation**: Room assignments and equipment booking

#### Row 2: Appointment Details & Quick Actions (2 Cards, 60/40 split)

**Appointment Details Panel (Left, 60% width)**
- **Background**: Detail-focused glass card
- **Height**: 380px
- **Content**:
  - **Header**: "Appointment Details" with edit button
  - **Selected Appointment Display**:
    - **Patient Information**:
      - Name: "Sarah Chen"
      - Age/DOB: "34 years • Jan 15, 1992"
      - Phone: "(555) 123-4567" with call button
      - Email: "sarah.chen@email.com" with message button
    - **Appointment Details**:
      - Date/Time: "March 15, 2026 • 2:30 PM - 3:00 PM"
      - Provider: "Dr. Michael Johnson"
      - Type: "Annual Physical"
      - Location: "Exam Room 3"
      - Status: "Confirmed" (green badge)
    - **Visit Information**:
      - Reason: "Routine annual checkup"
      - Special notes: "Patient prefers afternoon appointments"
      - Insurance: "Blue Cross Blue Shield - Verified"
      - Copay: "$25.00"
  - **Action Buttons**:
    - "Reschedule Appointment"
    - "Cancel Appointment"  
    - "Check-in Patient"
    - "View Medical Record"

**Quick Booking Panel (Right, 40% width)**
- **Background**: Booking-focused glass card
- **Height**: 380px
- **Content**:
  - **Header**: "Quick Book Appointment"
  - **Rapid Booking Form**:
    - **Patient Selection**:
      - Search field with auto-complete
      - Recent patients dropdown
      - "New Patient" button
    - **Appointment Type Selection**:
      - Common types: Physical, Consultation, Follow-up
      - Procedure-specific options
      - Custom appointment type
    - **Provider Selection**:
      - Available providers dropdown
      - Auto-suggest based on appointment type
      - "Any Available" option
    - **Date/Time Selection**:
      - Date picker with availability indicators
      - Time slot selector showing available slots
      - Duration selector (15, 30, 45, 60 minutes)
  - **Availability Indicator**: "Next available: Tomorrow 10:30 AM"
  - **Book Button**: Large, prominent green button

#### Row 3: Today's Schedule & Upcoming (2 Cards, 50/50 split)

**Today's Schedule Overview (Left, 50% width)**
- **Background**: Daily focus glass card
- **Height**: 350px
- **Content**:
  - **Header**: "Today's Schedule" with current time indicator
  - **Timeline View** (vertical):
    - **Current Time Line**: Red line indicating current time
    - **Appointment Blocks**:
      - 9:00 AM - Physical Exam - John Smith ✓ (completed)
      - 9:30 AM - Follow-up - Maria Garcia (in progress)
      - 10:00 AM - Consultation - David Lee (confirmed)
      - 10:30 AM - AVAILABLE (open slot)
      - 11:00 AM - Annual Physical - Sarah Chen (confirmed)
  - **Daily Statistics**:
    - Total appointments: "8 scheduled"
    - Completed: "3 of 8"
    - Available slots: "2 remaining"
    - Running status: "On time" (green indicator)
  - **Quick Actions**: 
    - "Add Walk-in"
    - "Block Time"
    - "View Full Day"

**Upcoming Visits Preview (Right, 50% width)**
- **Background**: Preview-focused glass card
- **Height**: 350px
- **Content**:
  - **Header**: "Upcoming This Week"
  - **Upcoming Appointments List**:
    - **Tomorrow (March 16)**:
      - 9:00 AM - Annual Physical - Jennifer Wilson
      - 2:00 PM - Consultation - Robert Martinez
      - 4:00 PM - Follow-up - Lisa Thompson
    - **Wednesday (March 17)**:
      - 10:00 AM - Physical Exam - Michael Davis
      - 1:30 PM - AVAILABLE SLOT
      - 3:00 PM - Consultation - Amy Johnson
  - **Week Statistics**:
    - Total appointments: "24 scheduled"
    - Utilization rate: "87%"
    - Cancellation rate: "5%"
  - **Trend Indicators**: Up/down arrows for appointment volume
  - **Action**: "View Full Week" button

#### Row 4: Patient Wait List & Scheduling Tools (2 Cards, 40/60 split)

**Patient Wait List (Left, 40% width)**
- **Background**: Wait list glass card with priority indicators
- **Height**: 320px
- **Content**:
  - **Header**: "Patient Wait List" with priority badge count
  - **Wait List Entries**:
    - **High Priority** (red indicator):
      - Patient: "Thomas Anderson"
      - Requested: "March 20, 2026"
      - Type: "Urgent consultation"
      - Waiting: "3 days"
      - Action: "Schedule Now" button
    - **Standard Priority** (blue indicator):
      - Patient: "Emma Taylor" 
      - Requested: "March 25, 2026"
      - Type: "Annual physical"
      - Waiting: "1 day"
      - Action: "Find Slot" button
  - **Auto-Scheduling**: "AI suggests: 4 matches for high priority patients"
  - **Bulk Actions**: "Schedule All Available" button

**Advanced Scheduling Tools (Right, 60% width)**
- **Background**: Tools-focused glass card
- **Height**: 320px
- **Content**:
  - **Header**: "Scheduling Tools & Analytics"
  - **Tool Tabs**:
    - **Availability Analysis**: 
      - Provider utilization charts
      - Peak hours identification
      - Optimal scheduling suggestions
    - **Appointment Patterns**:
      - Most requested appointment types
      - Seasonal booking trends
      - Patient preference analysis
    - **Conflict Resolution**:
      - Double-booked slots (if any)
      - Provider scheduling conflicts
      - Room allocation issues
  - **Quick Stats**:
    - "Average appointment length: 28 minutes"
    - "Most popular time slot: 10:00 AM"
    - "Cancellation rate this month: 4.2%"
  - **Optimization Suggestions**: AI-powered scheduling recommendations

## Appointment Interaction Flows

### New Appointment Creation Flow
1. **Entry Points**:
   - "New Appointment" button (header)
   - Double-click empty calendar slot
   - Quick booking panel
   - "Add Walk-in" for immediate needs

2. **Booking Steps**:
   - **Patient Selection**: Search or select from recent
   - **Appointment Type**: Choose from common types or custom
   - **Provider Selection**: Auto-suggest or manual selection
   - **Time Slot**: Visual calendar picker with availability
   - **Confirmation**: Review details and book

3. **Advanced Options**:
   - Recurring appointments
   - Series booking (multiple related appointments)
   - Group appointments (family members)
   - Telehealth vs in-person selection

### Appointment Modification Flow
1. **Selection Methods**:
   - Click appointment in calendar
   - Select from list view
   - Search and select

2. **Available Actions**:
   - **Reschedule**: Drag-drop or time picker
   - **Modify Details**: Change type, provider, notes
   - **Cancel**: With reason and notification options
   - **Check-in**: Mark patient arrival
   - **Complete**: Mark appointment finished

### Conflict Resolution Flow
1. **Conflict Detection**: Automatic identification of scheduling issues
2. **Alert System**: Visual indicators and notifications
3. **Resolution Options**: 
   - Auto-suggest alternative times
   - Provider substitution suggestions
   - Appointment type modifications
4. **Batch Resolution**: Handle multiple conflicts efficiently

## Design Specifications

### Scheduling Color System
- **Available Slots**: Light green background (rgba(34, 197, 94, 0.1))
- **Booked Appointments**: Professional blue (rgba(59, 130, 246, 0.8))
- **Current Time**: Red indicator line for immediate reference
- **Conflicts**: Amber warning (rgba(251, 146, 60, 0.8))
- **Cancelled**: Red striped pattern (rgba(239, 68, 68, 0.3))
- **Pending**: Yellow outline (rgba(251, 191, 36, 0.6))
- **Completed**: Green checkmark with muted colors

### Appointment Typography
- **Patient Names**: Inter, 600 weight, 14px (clear identification)
- **Time Slots**: Inter, 700 weight, 12px (easy scanning)
- **Appointment Types**: Inter, 500 weight, 12px, colored badges
- **Duration**: Inter, 400 weight, 11px, muted color
- **Status Labels**: Inter, 600 weight, 10px, uppercase, colored

### Calendar Interaction Design
- **Time Slots**: 
  - Height: 60px for 30-minute slots
  - Clear grid lines with subtle borders
  - Hover effects for available slots
- **Appointment Cards**:
  - Rounded corners: 8px
  - Padding: 8px
  - Shadow on hover: 0 2px 8px rgba(0, 0, 0, 0.15)
  - Drag handle indicator on hover

### Responsive Scheduling Layout
- **Large Desktop (1400px+)**: Full calendar with detailed appointment cards
- **Desktop (1024px-1399px)**: Standard layout as described
- **Tablet (768px-1023px)**: List view default, calendar on demand
- **Mobile (<768px)**: Day view only, swipe navigation between dates

### Accessibility & Efficiency
- **Keyboard Navigation**: Full calendar navigation with keyboard
- **Screen Reader Support**: Comprehensive ARIA labeling for appointments
- **High Contrast**: Clear visual distinction between appointment states
- **Quick Actions**: Keyboard shortcuts for common scheduling tasks
- **Voice Commands**: Optional voice scheduling for hands-free operation

### Performance Optimization
- **Lazy Loading**: Load appointments on-demand for large date ranges
- **Caching**: Cache frequently accessed appointment data
- **Real-time Sync**: Live updates for multi-user scheduling environments
- **Conflict Prevention**: Real-time availability checking during booking

## Scheduling Command Center Philosophy

The Appointment Management Page serves as a comprehensive scheduling command center that:

1. **Optimizes Provider Time**: Efficient scheduling tools minimize administrative overhead
2. **Enhances Patient Experience**: Easy booking with minimal wait times
3. **Prevents Scheduling Conflicts**: Real-time conflict detection and resolution
4. **Supports Clinical Workflow**: Seamless integration with patient care processes
5. **Provides Operational Insights**: Analytics for schedule optimization
6. **Maintains Professional Standards**: Clean, medical-grade scheduling interface

The interface balances comprehensive scheduling functionality with the calm, professional healthcare aesthetic while supporting efficient appointment management workflows for both individual providers and healthcare organizations.