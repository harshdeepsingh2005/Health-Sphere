# User Management Page - UI Layout Design

## Overall Layout Structure

### Navigation Header (Sticky, Full Width)
- **Height**: 70px (expanded for user management controls)
- **Background**: Administrative glass (rgba(255, 255, 255, 0.95)) with management-focused blue undertone
- **Border**: Clean bottom border (1px solid rgba(59, 130, 246, 0.09))
- **Shadow**: Administrative shadow (0 2px 16px rgba(59, 130, 246, 0.07))

**Components:**
- **Left Section**: 
  - Breadcrumb: "Dashboard > User Management"
  - Active user count indicator: "847 Active Users"
- **Center Section**: 
  - Global user search bar with advanced search toggle
  - Quick role filter buttons (All, Doctors, Nurses, Staff, Patients, Admins)
- **Right Section**:
  - Bulk actions dropdown (when users selected)
  - "Invite New User" button (green)
  - Export user list button
  - User management settings

### Sidebar (Sticky, Collapsible)
- **Width**: 320px expanded, 64px collapsed
- **Background**: User management glass overlay (rgba(248, 250, 252, 0.97))
- **Border**: Management border (1px solid rgba(59, 130, 246, 0.08))

**User Management Navigation:**
1. **All Users** (active state)
2. **Medical Staff**
3. **Administrative Staff**
4. **Patients**
5. **Inactive Users**
6. **Pending Invitations**
7. **Access Controls**
8. **Audit Logs**

**Quick Filters Panel:**
- **Status Filters**: Active, Inactive, Suspended, Pending
- **Role Categories**: Clinical, Administrative, Support, Patient
- **Department Filters**: Emergency, Cardiology, Surgery, etc.
- **Access Level**: Admin, Manager, Staff, Read-only
- **Registration Date**: Today, This Week, This Month, Custom

**User Statistics:**
- Total users: "847"
- Active today: "234"
- New this month: "23"
- Pending approval: "5"

## Main Content Area

### User Management Grid Layout (CSS Grid, 18px gap)

#### Row 1: User Management Controls (Full Width Card)

**User Management Control Panel**
- **Background**: Control-focused glass with management accents
- **Height**: 100px
- **Content**:
  - **Left Section**: 
    - View toggle: Table View | Card View (active states)
    - Items per page selector (25, 50, 100, All)
    - Show/hide columns dropdown
  - **Center Section**:
    - Advanced search builder with field-specific filters
    - Sort options: Name, Role, Department, Last Active, Registration Date
    - Filter indicator badges showing active filters
  - **Right Section**:
    - Bulk selection controls (Select All, Clear Selection)
    - Bulk actions: Activate, Deactivate, Change Role, Export Selected
    - User import/export tools

#### Row 2: User Statistics Overview (4 Cards)
**Grid**: 4 equal columns, responsive stacking

**Medical Staff (Card 1)**
- **Background**: Medical staff glass with clinical accent (rgba(34, 197, 94, 0.06))
- **Height**: 120px
- **Content**:
  - **Count**: "156" (36px, semibold)
  - **Subtitle**: "Medical Staff"
  - **Breakdown**:
    - Doctors: "47 active"
    - Nurses: "89 active" 
    - Specialists: "20 active"
  - **Status**: "98% active rate"
  - **Icon**: Stethoscope with user silhouette

**Administrative Staff (Card 2)**
- **Background**: Admin staff glass with blue accent (rgba(59, 130, 246, 0.06))
- **Height**: 120px
- **Content**:
  - **Count**: "73" (36px, semibold)
  - **Subtitle**: "Administrative Staff"
  - **Breakdown**:
    - Managers: "12 active"
    - Coordinators: "28 active"
    - Support: "33 active"
  - **Status**: "95% active rate"
  - **Icon**: Clipboard with user badge

**Patient Accounts (Card 3)**
- **Background**: Patient glass with caring accent (rgba(139, 92, 246, 0.06))
- **Height**: 120px
- **Content**:
  - **Count**: "618" (36px, semibold)
  - **Subtitle**: "Patient Accounts"
  - **Breakdown**:
    - Active patients: "567"
    - Family accounts: "51"
  - **Growth**: "+47 this month"
  - **Icon**: Heart with user profile

**System Access (Card 4)**
- **Background**: Access control glass with security accent (rgba(251, 146, 60, 0.06))
- **Height**: 120px
- **Content**:
  - **Count**: "5" (36px, semibold)
  - **Subtitle**: "Pending Access"
  - **Breakdown**:
    - New staff: "3 pending"
    - Role changes: "2 pending"
  - **Action Required**: "Review Requests"
  - **Icon**: Key with shield

#### Row 3: User Data Table (Full Width Card)

**Comprehensive User Management Table**
- **Background**: Table-focused glass with data organization accents
- **Height**: Dynamic (minimum 500px, expandable)
- **Content**:
  - **Table Header Controls**:
    - Column sorting indicators (clickable headers)
    - Filter icons on filterable columns
    - Resize handles between columns
    - Pin/unpin column options
  
  - **Table Columns**:
    - **Selection**: Checkbox for bulk operations
    - **User Photo**: Professional avatar with status indicator
    - **Name**: Full name with preferred name display
    - **Role**: Color-coded role badge with hierarchy indicator
    - **Department**: Department name with icon
    - **Email**: Contact email with verification status
    - **Phone**: Contact number with SMS capability indicator
    - **Status**: Active/Inactive with visual indicator
    - **Last Login**: Timestamp with relative time display
    - **Actions**: Quick action buttons (View, Edit, Deactivate, More)

  - **Sample User Rows**:
    - **Dr. Sarah Johnson**:
      - Photo: Professional headshot with green active indicator
      - Role: "Cardiologist" (blue medical badge)
      - Department: "Cardiology" with heart icon
      - Email: "s.johnson@healthsphere.ai" (verified checkmark)
      - Phone: "(555) 123-4567" (SMS enabled)
      - Status: "Active" (green badge)
      - Last Login: "2 hours ago"
      - Actions: View profile, Edit details, Message, More options

    - **Maria Rodriguez, RN**:
      - Photo: Professional headshot with green active indicator
      - Role: "Nurse Manager" (green nursing badge)
      - Department: "Emergency" with plus icon
      - Email: "m.rodriguez@healthsphere.ai" (verified)
      - Phone: "(555) 234-5678"
      - Status: "Active" (green badge)
      - Last Login: "15 minutes ago"

    - **Robert Chen**:
      - Photo: Patient avatar with blue indicator
      - Role: "Patient" (purple patient badge)
      - Department: "N/A" 
      - Email: "robert.chen@email.com" (verified)
      - Phone: "(555) 345-6789"
      - Status: "Active" (green badge)
      - Last Login: "Yesterday"

    - **Jennifer Adams**:
      - Photo: Staff photo with amber indicator
      - Role: "Admin Coordinator" (orange admin badge)
      - Department: "Administration" with gear icon
      - Email: "j.adams@healthsphere.ai" (pending verification)
      - Phone: "(555) 456-7890"
      - Status: "Pending Setup" (amber badge)
      - Last Login: "Never"

  - **Table Features**:
    - **Row Interactions**: Click to view profile, hover for quick actions
    - **Bulk Selection**: Multi-select with shift-click support
    - **Inline Editing**: Click-to-edit for certain fields
    - **Contextual Menus**: Right-click for additional options
    - **Pagination**: Smart pagination with jump-to-page options
    - **Row Density**: Compact, Standard, Comfortable view options

#### Row 4: User Details & Quick Actions (2 Cards, 60/40 split)

**Selected User Details Panel (Left, 60% width)**
- **Background**: User detail glass card
- **Height**: 400px
- **Content**:
  - **Header**: "User Profile: Dr. Sarah Johnson" with edit button
  - **User Information Display**:
    - **Personal Details**:
      - Full Name: "Dr. Sarah Elizabeth Johnson"
      - Employee ID: "EMP-2847"
      - Department: "Cardiology"
      - Position: "Senior Cardiologist"
      - Direct Manager: "Dr. Michael Davis, Chief of Cardiology"
    - **Contact Information**:
      - Email: "s.johnson@healthsphere.ai" (verified badge)
      - Phone: "(555) 123-4567" (mobile icon)
      - Emergency Contact: "John Johnson (Spouse) - (555) 987-6543"
    - **System Access**:
      - Role: "Medical Staff - Cardiologist"
      - Access Level: "Clinical Full Access"
      - Permissions: "Patient Records, Scheduling, Prescriptions"
      - Last Password Change: "45 days ago"
      - Two-Factor Auth: "Enabled" (security badge)
    - **Activity Summary**:
      - Account Created: "January 15, 2024"
      - Last Login: "February 17, 2026 at 2:34 PM"
      - Total Logins: "1,247"
      - Average Session: "4.2 hours"
  - **Action Buttons**:
    - "Edit Profile" (blue button)
    - "Reset Password" (amber button)
    - "Change Role" (purple button)
    - "Deactivate Account" (red outline button)

**Quick User Management Actions (Right, 40% width)**
- **Background**: Quick actions glass card
- **Height**: 400px
- **Content**:
  - **Header**: "Quick Management Actions"
  - **User Creation Section**:
    - **Create New User**:
      - "Add Medical Staff" (green button)
      - "Add Administrative User" (blue button)
      - "Create Patient Account" (purple button)
      - "Bulk Import Users" (amber button)
  - **Access Management Section**:
    - **Pending Approvals**:
      - "Review 5 Access Requests" (notification badge)
      - "Approve Role Changes" (2 pending)
      - "Verify New Registrations" (3 pending)
  - **System Administration**:
    - **User Analytics**:
      - "Generate User Activity Report"
      - "Export User Directory"
      - "Review Login Analytics"
    - **Security Actions**:
      - "Force Password Resets" (batch action)
      - "Review Failed Login Attempts"
      - "Update Access Permissions"
  - **Recent Activity Log**:
    - "Dr. Martinez logged in - 5 min ago"
    - "New patient registered - 12 min ago" 
    - "Role changed: J. Adams to Admin - 1 hour ago"
    - "Password reset: Nurse Williams - 2 hours ago"

#### Row 5: User Insights & Reports (3 Cards)

**User Activity Analytics (Card 1, 40% width)**
- **Background**: Analytics glass with activity tracking accents
- **Height**: 280px
- **Content**:
  - **Header**: "User Activity Insights"
  - **Activity Metrics**:
    - Daily active users: "234 (28% of total)"
    - Peak usage time: "10:00 AM - 2:00 PM"
    - Average session length: "3.7 hours"
    - Mobile vs desktop: "67% desktop, 33% mobile"
  - **Activity Charts**:
    - Login frequency over 30 days (line chart)
    - Department usage distribution (bar chart)
    - Role-based activity levels (donut chart)
  - **Usage Patterns**: "Highest activity on Tuesdays and Wednesdays"

**Access Control Summary (Card 2, 30% width)**
- **Background**: Security-focused glass card
- **Height**: 280px
- **Content**:
  - **Header**: "Access Control Overview"
  - **Permission Levels**:
    - Full Access: "52 users (Doctors, Senior Staff)"
    - Standard Access: "134 users (Nurses, Coordinators)"
    - Limited Access: "87 users (Support Staff)"
    - Patient Access: "574 users (Patients, Families)"
  - **Security Metrics**:
    - Two-factor enabled: "89% of clinical staff"
    - Password compliance: "96% meeting requirements"
    - Failed login attempts: "12 in last 24 hours"
  - **Action Items**: "3 users need password updates"

**User Management Reports (Card 3, 30% width)**
- **Background**: Reporting glass card
- **Height**: 280px
- **Content**:
  - **Header**: "User Management Reports"
  - **Available Reports**:
    - "Monthly User Activity Summary"
    - "Department Staffing Report"
    - "Security Compliance Audit"
    - "New User Onboarding Status"
  - **Recent Reports**:
    - "January 2026 Activity Report" - Generated yesterday
    - "Q4 2025 Security Audit" - Downloaded 3 days ago
  - **Automated Reports**:
    - Weekly activity summary: "Enabled"
    - Monthly compliance report: "Auto-generated"
    - Security alerts: "Real-time notifications"
  - **Custom Reports**: "Build Custom User Report" button

## User Management Interaction Flows

### User Search & Filtering
- **Global Search**: Search across name, email, employee ID, department
- **Advanced Filters**: Multi-criteria filtering with saved filter sets
- **Quick Filters**: One-click role and status filters
- **Real-time Results**: Instant filtering as user types

### User Profile Management
- **Profile Viewing**: Comprehensive user information display
- **Inline Editing**: Quick edits for common fields
- **Bulk Operations**: Multi-user updates and management
- **Role Management**: Hierarchical role assignment and permissions

### Access Control Workflows
- **Permission Assignment**: Granular permission management
- **Role-Based Access**: Pre-configured role templates
- **Approval Workflows**: Multi-step approval for access changes
- **Security Monitoring**: Real-time access monitoring and alerts

## Design Specifications

### User Management Color System
- **Medical Staff**: #059669 (green, healthcare professionals)
- **Administrative**: #2563EB (blue, management and coordination)
- **Patients**: #8B5CF6 (purple, care recipients)
- **System Admin**: #EA580C (orange, system management)
- **Active Status**: #10B981 (green, currently active)
- **Inactive Status**: #6B7280 (gray, not currently active)
- **Pending Status**: #F59E0B (amber, awaiting action)
- **Critical Alert**: #DC2626 (red, immediate attention needed)

### Table Design Elements
- **Row Height**: 60px (comfortable data density)
- **Alternating Rows**: Subtle zebra striping (rgba(248, 250, 252, 0.5))
- **Hover Effects**: Gentle row highlighting on hover
- **Selection State**: Blue highlight for selected rows
- **Sort Indicators**: Clear ascending/descending arrows
- **Action Buttons**: Consistent icon-based actions with tooltips

### User Badge System
- **Role Badges**: Color-coded with icon indicators
  - Medical: Green with stethoscope icon
  - Nursing: Teal with care cross icon
  - Admin: Blue with gear icon
  - Patient: Purple with heart icon
- **Status Indicators**: Dot indicators with tooltips
  - Active: Green dot
  - Away: Amber dot
  - Offline: Gray dot
- **Verification Badges**: Checkmarks for verified information

### Responsive User Management
- **Large Desktop**: Full table with all columns visible
- **Desktop**: Standard layout with column prioritization
- **Tablet**: Card view with essential information
- **Mobile**: List view with expandable user cards

### Accessibility Features
- **Screen Reader Support**: Complete ARIA labeling for tables
- **Keyboard Navigation**: Full table navigation with keyboard
- **High Contrast**: Clear visual distinction for all user states
- **Focus Management**: Clear focus indicators throughout interface
- **Alternative Formats**: Audio descriptions for user status information

### Performance Optimization
- **Virtual Scrolling**: Efficient rendering of large user lists
- **Lazy Loading**: Load user details on demand
- **Search Optimization**: Indexed searching with debounced input
- **Caching**: Smart caching of frequently accessed user data
- **Background Operations**: Non-blocking bulk operations with progress indicators

## User Management Philosophy

The User Management Page serves as a comprehensive administrative control center that:

1. **Simplifies User Administration**: Intuitive interface for managing diverse user types
2. **Ensures Security Compliance**: Robust access control and permission management
3. **Supports Healthcare Workflows**: Role-based access aligned with clinical needs
4. **Provides Operational Visibility**: Clear insights into user activity and system usage
5. **Enables Scalable Management**: Efficient tools for growing healthcare organizations
6. **Maintains Data Integrity**: Accurate user information with verification systems
7. **Facilitates Compliance**: Audit trails and reporting for regulatory requirements

The interface creates a powerful yet approachable user management environment that enables healthcare administrators to efficiently manage users while maintaining the security and compliance standards essential for healthcare organizations. The design balances comprehensive functionality with the calm, professional aesthetic that supports confident administrative decision-making.