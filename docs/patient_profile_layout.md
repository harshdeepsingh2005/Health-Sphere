# Patient Profile Page - UI Layout Design

## Overall Layout Structure

### Navigation Header (Sticky, Full Width)
- **Height**: 68px (slightly taller for breadcrumb)
- **Background**: Clinical glass (rgba(255, 255, 255, 0.93)) with professional blue undertone
- **Border**: Subtle bottom border (1px solid rgba(59, 130, 246, 0.08))
- **Shadow**: Professional shadow (0 2px 16px rgba(0, 0, 0, 0.06))

**Components:**
- **Left Section**: 
  - Breadcrumb navigation: "Dashboard > Patients > Sarah Chen"
  - Patient status indicator (Active/Inactive/Critical)
- **Center Section**: 
  - Patient name and primary identifier
  - Quick patient search with suggestions
- **Right Section**:
  - Critical alerts badge
  - Print patient summary button
  - Share/Export options dropdown
  - Emergency protocol access

### Sidebar (Sticky, Collapsible)
- **Width**: 320px expanded, 64px collapsed
- **Background**: Clinical information glass (rgba(248, 250, 252, 0.96))
- **Border**: Professional right border (1px solid rgba(59, 130, 246, 0.08))

**Patient Quick Navigation:**
1. **Overview** (active state)
2. **Medical History**
3. **Vital Signs**
4. **Medications**
5. **Lab Results**
6. **Imaging Studies**
7. **Treatment Plans**
8. **Notes & Reports**
9. **Insurance & Billing**

**Quick Info Panel:**
- Patient photo and basic demographics
- Emergency contacts
- Primary physician
- Insurance status
- Last visit date

## Main Content Area

### Patient Profile Grid Layout (CSS Grid, 20px gap)

#### Header Section: Patient Overview Card (Full Width)

**Patient Identity & Status Card**
- **Background**: Patient-focused gradient glass (soft blue to white)
- **Height**: 180px
- **Content**:
  - **Left Section (Patient Photo & Demographics)**:
    - Professional patient photo (120px circle with medical border)
    - Full name: "Sarah Elizabeth Chen" (24px, semibold)
    - Patient ID: "HS-2847-9831"
    - Age, DOB, Gender: "34 years • Jan 15, 1992 • Female"
    - Contact info with privacy controls
  - **Center Section (Key Medical Info)**:
    - Primary physician: "Dr. Michael Johnson, MD"
    - Blood type: "A+" with medical cross icon
    - Known allergies: "Penicillin, Shellfish" (red alert badges)
    - Emergency contact: "John Chen (Spouse)" with phone
  - **Right Section (Current Status)**:
    - Health status: "Stable" (green indicator)
    - Last visit: "Feb 10, 2026"
    - Next appointment: "Mar 15, 2026 - Annual Physical"
    - Active treatment plans: "2 ongoing"

#### Row 1: AI Assessment & Risk Analysis (2 Cards, 60/40 split)

**AI Risk Assessment Dashboard (Left, 60% width)**
- **Background**: AI-focused glass with intelligent purple accents
- **Height**: 320px
- **Content**:
  - **Header**: "AI Clinical Risk Assessment" with confidence indicator
  - **Risk Score Display**:
    - Overall risk: "Low Risk" (large green indicator)
    - Risk percentage: "12%" with trend arrow
    - Last assessment: "Feb 16, 2026"
  - **Risk Breakdown**:
    - Cardiovascular: "Low (8%)" - green
    - Diabetes: "Moderate (24%)" - yellow  
    - Cancer screening: "Up to date" - green
    - Mental health: "Monitor (18%)" - yellow
  - **AI Recommendations**:
    - "Consider lipid panel in 6 months"
    - "Maintain current exercise routine"
    - "Schedule mammography this year"
  - **Prediction Confidence**: "94% accuracy based on 15,000+ similar cases"

**Current Medications (Right, 40% width)**
- **Background**: Medication-focused glass with pharmacy accents
- **Height**: 320px
- **Content**:
  - **Header**: "Current Medications" with medication count
  - **Active Medications List**:
    - **Medication Card 1**:
      - Name: "Lisinopril 10mg"
      - Purpose: "Blood pressure control"
      - Schedule: "Once daily, morning"
      - Prescribing doctor: "Dr. Johnson"
      - Start date: "Jan 2024"
      - Refills remaining: "2"
    - **Medication Card 2**:
      - Name: "Vitamin D3 2000 IU"
      - Purpose: "Bone health supplement"
      - Schedule: "Once daily with meal"
      - Start date: "Dec 2025"
  - **Interaction Warnings**: "No known interactions detected"
  - **Actions**: "Request Refill", "Print Med List"

#### Row 2: Medical History Timeline (Full Width Card)

**Medical History & Timeline Visualization**
- **Background**: Historical data glass with timeline accents
- **Height**: 400px
- **Content**:
  - **Header**: "Medical History Timeline" with time range selector
  - **Interactive Timeline** (horizontal scroll with zoom):
    - **Time Scale**: Years/Months with clear markers
    - **Event Categories** (color-coded tracks):
      - **Conditions**: Chronic conditions and diagnoses
      - **Procedures**: Surgeries, treatments, major procedures  
      - **Medications**: Start/stop dates for medications
      - **Preventive Care**: Screenings, vaccinations, checkups
    - **Timeline Events**:
      - **2026 Feb**: Annual physical - excellent health
      - **2025 Dec**: Started Vitamin D supplementation
      - **2024 Jan**: Hypertension diagnosed, started Lisinopril
      - **2023 Aug**: Appendectomy - successful recovery
      - **2022 Oct**: COVID vaccination series completed
  - **Detailed Event Cards**: Click/hover for full information
  - **Filter Options**: By category, date range, severity

#### Row 3: Vital Signs & Laboratory Data (2 Cards, 50/50 split)

**Vital Signs Dashboard (Left, 50% width)**
- **Background**: Vitals-focused glass with monitoring accents
- **Height**: 450px
- **Content**:
  - **Header**: "Vital Signs Trends" with date range selector
  - **Current Vitals** (top section):
    - Blood Pressure: "118/76 mmHg" (green, excellent)
    - Heart Rate: "72 bpm" (green, normal)
    - Temperature: "98.6°F" (green, normal)
    - Weight: "145 lbs" (stable trend)
    - BMI: "22.1" (green, healthy range)
  - **Trend Charts** (interactive):
    - Blood pressure over 6 months (line chart)
    - Weight trend over 1 year (line chart)
    - Heart rate variability (when available)
  - **Alert Thresholds**: Clearly marked normal ranges
  - **Data Source**: Last recorded visit + home monitoring

**Laboratory Results (Right, 50% width)**
- **Background**: Lab-focused glass with analytical accents
- **Height**: 450px
- **Content**:
  - **Header**: "Recent Laboratory Results"
  - **Latest Lab Panel** (Feb 10, 2026):
    - **Complete Blood Count**:
      - WBC: "6.8 K/μL" (normal range)
      - RBC: "4.2 M/μL" (normal range)
      - Hemoglobin: "13.8 g/dL" (normal range)
      - Hematocrit: "41%" (normal range)
    - **Comprehensive Metabolic Panel**:
      - Glucose: "95 mg/dL" (normal, fasting)
      - Cholesterol: "185 mg/dL" (good)
      - HDL: "65 mg/dL" (excellent)
      - LDL: "110 mg/dL" (acceptable)
      - Triglycerides: "98 mg/dL" (normal)
  - **Trending Values**: Comparison to previous results
  - **Action Items**: "No abnormal findings" or specific follow-ups

#### Row 4: Clinical Notes & Reports (2 Cards, 70/30 split)

**Doctor Notes & Observations (Left, 70% width)**
- **Background**: Clinical notes glass with documentation accents
- **Height**: 380px
- **Content**:
  - **Header**: "Clinical Notes & Provider Observations"
  - **Recent Notes** (chronological, scrollable):
    - **Note Entry 1** (Feb 10, 2026 - Dr. Johnson):
      - Visit type: "Annual Physical Examination"
      - Chief complaint: "Routine health maintenance"
      - Assessment: "34yo female in excellent health. BP well controlled..."
      - Plan: "Continue current medications, routine screening up to date..."
      - Follow-up: "RTC 1 year, sooner if concerns"
    - **Note Entry 2** (Aug 15, 2025 - Dr. Smith):
      - Visit type: "Follow-up hypertension"
      - Assessment: "BP responding well to Lisinopril..."
      - Plan: "Continue current dose, lifestyle modifications..."
  - **Note Categories**: Progress notes, consultation notes, procedure notes
  - **Search & Filter**: Full-text search within notes

**Recent Reports Summary (Right, 30% width)**
- **Background**: Reports summary glass
- **Height**: 380px
- **Content**:
  - **Header**: "Recent Reports & Studies"
  - **Report List**:
    - **Imaging Reports**:
      - Chest X-ray (Normal) - Jan 2026
      - Mammogram (Normal) - Oct 2025
    - **Specialty Consults**:
      - Cardiology consult (Normal) - Dec 2025
    - **Procedure Reports**:
      - Colonoscopy (Normal) - Sep 2024
  - **Pending Studies**: Upcoming scheduled tests
  - **Action Items**: Follow-up requirements from reports

#### Row 5: Family History & Additional Information (3 Cards)

**Family Medical History (Card 1, 40% width)**
- **Background**: Genetic/family history glass
- **Height**: 280px
- **Content**:
  - **Header**: "Family Medical History"
  - **Paternal Side**:
    - Father: "Diabetes (age 65), Hypertension"
    - Paternal grandmother: "Stroke (age 78)"
  - **Maternal Side**:
    - Mother: "Breast cancer survivor (age 52)"
    - Maternal grandfather: "Heart disease (age 70)"
  - **Risk Implications**: AI-generated genetic risk factors
  - **Screening Recommendations**: Based on family history

**Social History & Lifestyle (Card 2, 30% width)**
- **Background**: Lifestyle-focused glass
- **Height**: 280px
- **Content**:
  - **Header**: "Social & Lifestyle History"
  - **Lifestyle Factors**:
    - Smoking: "Never"
    - Alcohol: "Occasional social drinking"
    - Exercise: "Regular - 4x/week cardio + weights"
    - Diet: "Mediterranean-style, well-balanced"
  - **Occupational**: "Software engineer - desk work"
  - **Stress levels**: "Moderate, managed well"
  - **Sleep patterns**: "7-8 hours nightly, good quality"

**Care Team & Contacts (Card 3, 30% width)**
- **Background**: Care coordination glass
- **Height**: 280px
- **Content**:
  - **Header**: "Care Team & Emergency Contacts"
  - **Primary Care Team**:
    - Primary Care: "Dr. Michael Johnson, MD"
    - Pharmacy: "HealthPlus Pharmacy"
    - Insurance: "Blue Cross Blue Shield"
  - **Specialist Consultants**:
    - Cardiology: "Dr. Sarah Williams, MD"
    - OB/GYN: "Dr. Lisa Martinez, MD"
  - **Emergency Contacts**:
    - Primary: "John Chen (Spouse) - (555) 123-4567"
    - Secondary: "Maria Chen (Mother) - (555) 987-6543"

## Clinical Review Interface Elements

### Action Bar (Floating, Bottom Right)
- **Background**: Clinical action glass with medical accent
- **Components**:
  - "Print Summary" button
  - "Send to Specialist" button  
  - "Schedule Follow-up" button
  - "Update Information" button
  - "Emergency Protocol" (red button)

### Clinical Decision Support
- **AI Recommendations Panel** (expandable):
  - Evidence-based treatment suggestions
  - Drug interaction warnings
  - Preventive care reminders
  - Risk stratification guidance
  - Clinical guideline compliance

## Design Specifications

### Clinical Color System
- **Primary Medical Blue**: #1E40AF (professional, trustworthy)
- **Critical Alert Red**: #DC2626 (immediate attention)
- **Caution Amber**: #D97706 (review needed)
- **Healthy Green**: #059669 (normal, positive)
- **AI Intelligence Purple**: #7C3AED (insights, analysis)
- **Information Gray**: #6B7280 (supporting data)

### Medical Typography
- **Patient Name**: Inter, 700 weight, 24px (clear identification)
- **Medical Values**: Inter, 600 weight, 16px (critical readability)
- **Clinical Notes**: Inter, 400 weight, 14px, 1.6 line height
- **Timestamps**: Inter, 400 weight, 12px, muted color
- **Medical Terms**: Consistent terminology with hover definitions

### Clinical Card Design
- **Border Radius**: 12px (professional, clean)
- **Padding**: 20px (efficient medical information density)
- **Shadow**: 0 3px 18px rgba(0, 0, 0, 0.08)
- **Border**: 1px solid rgba(59, 130, 246, 0.1) for medical context
- **Background**: rgba(255, 255, 255, 0.9) with subtle medical tint

### Clinical Data Visualization
- **Charts**: Clean, medical-grade with clear axis labels
- **Trend Lines**: Smooth curves with normal range indicators
- **Data Points**: Clear markers with hover details
- **Time Series**: Consistent time scales with medical relevance
- **Alert Zones**: Clear visual indicators for abnormal ranges

### Medical Information Hierarchy
1. **Critical/Emergency**: Allergies, current medications, critical values
2. **Primary Clinical**: Current conditions, recent vitals, active treatments
3. **Historical**: Past medical history, family history, previous results
4. **Supporting**: Social history, care team information, notes
5. **Administrative**: Insurance, billing, contact information

### Clinical Workflow Integration
- **EMR Compatibility**: Design supports integration with electronic medical records
- **Clinical Documentation**: Structured for medical billing and documentation
- **Care Coordination**: Information organized for multi-provider access
- **Patient Safety**: Critical information prominently displayed
- **Audit Trail**: Clear documentation of information access and updates

### Responsive Clinical Layout
- **Large Medical Display**: Full layout optimized for clinical workstations
- **Standard Desktop**: Maintains clinical information hierarchy
- **Tablet**: Condensed view with swipe navigation between sections
- **Mobile**: Essential information only, emergency-focused

### Clinical Safety Features
- **Allergy Alerts**: Prominently displayed with high contrast
- **Drug Interactions**: Real-time checking with clear warnings
- **Critical Values**: Immediate highlighting of abnormal results
- **Emergency Information**: Always accessible emergency contacts and protocols
- **Version Control**: Clear indication of information currency and updates

## Clinical Command Center Philosophy

The Patient Profile Page serves as a comprehensive clinical command center that:

1. **Supports Clinical Decision Making**: All relevant information accessible
2. **Ensures Patient Safety**: Critical information prominently featured
3. **Facilitates Care Coordination**: Structured for multi-provider access
4. **Maintains Medical Standards**: Professional clinical documentation
5. **Integrates AI Insights**: Intelligent analysis without overwhelming clinicians
6. **Preserves Patient Privacy**: Clear access controls and audit capabilities

The interface provides comprehensive patient information in a calm, organized manner that supports thorough clinical review while maintaining the warm, professional healthcare aesthetic essential for both provider efficiency and patient trust.