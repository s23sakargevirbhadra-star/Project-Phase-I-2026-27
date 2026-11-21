# 📊 Maharashtra Places - System Diagrams Guide

## ✅ All 5 JPG Images Created

Your system diagrams are now ready in the `diagrams/` folder as high-quality JPG images.

| # | Filename | Size | What It Shows |
|---|----------|------|---------------|
| 1 | `1_system_architecture.jpg` | 28.2 KB | All system layers, components, and external services |
| 2 | `2_data_flow_1_search.jpg` | 19.5 KB | User searches → API → MongoDB → Distance calculation → Results on map |
| 3 | `3_data_flow_2_auth.jpg` | 83.4 KB | Signup → Password hashing → OTP → Verification → Login → Session |
| 4 | `4_use_case_diagram.jpg` | 18.6 KB | All 11 features: search, filter, map, trails, language |
| 5 | `5_system_working_flow.jpg` | 63.2 KB | Complete user journey from landing page to logout |

**Total Size:** 213.3 KB for all 5 diagrams

---

## 🖼️ How to Use These Images

### View Images
- **Windows:** Right-click → Open with → Photos or any image viewer
- **Mac:** Double-click to open in Preview
- **Linux:** Open in your default image viewer
- **Browser:** Drag and drop into any web browser

### Print Images
- **Windows:** Right-click → Print → "Microsoft Print to PDF" or your printer
- **Mac:** Open in Preview → File → Print
- **Browser:** File → Print (or Ctrl+P)

### Share Images
- Email: Attach the `.jpg` files directly
- Presentations: Insert into PowerPoint, Google Slides, Keynote
- Documents: Embed in Word, Google Docs
- GitHub: Upload to your repository
- Web: Include in project documentation

### Edit Diagrams
If you need to modify a diagram:
1. Open the corresponding `.md` file (e.g., `1_system_architecture.md`)
2. Copy the Mermaid code block
3. Go to https://mermaid.live
4. Paste the code and edit
5. Download as PNG or JPG
6. Replace the old image file

---

## 📐 Image Specifications

- **Format:** JPG (Joint Photographic Experts Group)
- **Quality:** 90% (high quality with smaller file size)
- **Color:** Black and white (print-friendly, accessible)
- **Resolution:** ~800-1920 px wide × 600-1200 px tall
- **Background:** White with black text and lines
- **Style:** Clean, professional, publication-ready

---

## 📝 Diagram Descriptions

### 1. System Architecture
**Filename:** `1_system_architecture.jpg`

Shows the complete system divided into 4 layers:
- **Client Layer:** Web browser (HTML + CSS + JavaScript)
- **Application Layer:** Flask web server, authentication module, recommendation engine
- **Data Layer:** MongoDB database, CSV backup file
- **External Services:** OpenStreetMap (for maps), Gmail SMTP (for emails)

**Connections shown:**
- Browser sends HTTP requests to Flask
- Flask routes requests to Auth or Recommender modules
- Modules query MongoDB for data
- Auth module sends emails via Gmail
- Browser displays map tiles from OpenStreetMap

---

### 2. Data Flow Diagram 1 - Location Search Flow
**Filename:** `2_data_flow_1_search.jpg`

Shows what happens when user searches for places by city and radius:

1. User selects city and radius
2. Browser JavaScript calls `/api/recommend?lat=...&lon=...&radius=50`
3. Flask app receives request
4. Recommender module loads all 53 places from MongoDB
5. **Haversine formula** calculates distance from user to each place
6. Filter: keep only places within radius & matching category
7. Sort: by rating (highest first), then by distance
8. Return top 10 as JSON
9. Display as result cards (left) and map pins (right)

**Key concept:** Haversine formula = mathematical way to calculate distance between two GPS points on Earth

---

### 3. Data Flow Diagram 2 - Authentication Flow
**Filename:** `3_data_flow_2_auth.jpg`

Shows complete signup and login process:

**Signup Path:**
1. User fills form: name, email, password, confirm password
2. System validates input (email format, password length, no duplicates)
3. Password is hashed using werkzeug (never stored as plain text)
4. User document saved to MongoDB with `is_verified=false`
5. Generate 6-digit OTP code
6. Send OTP to user's email via Gmail SMTP
7. User navigates to `/verify` page

**OTP Verification:**
1. User enters 6-digit code from email
2. System checks: code matches AND not expired (10 minute window)
3. If correct: mark `is_verified=true` in MongoDB, clear OTP
4. Redirect to login page

**Login Path:**
1. User enters email and password
2. System validates: email exists, password matches hash, account is verified
3. If all checks pass: create Flask session cookie
4. Session contains user name, email, login time
5. Redirect to main application

---

### 4. Use Case Diagram
**Filename:** `4_use_case_diagram.jpg`

Shows all system features and who can use them:

**Visitor (Not Logged In):**
- Sign Up (create account)
- Login (enter credentials)
- Change Language (English ↔ Marathi)

**Logged-in User (All of above PLUS):**
- Search by city & radius
- Use GPS location
- Filter by category (Beach, Fort, Temple, etc.)
- Filter by season (Winter, Monsoon, Summer)
- Search by place name
- View interactive map with pins
- View place details (fees, timings, tips)
- View pre-designed trails
- Change language

**Feature Relationships:**
- Search by city and GPS are alternative ways to start
- Filters work with location search
- Map displays results visually
- Clicking place shows full details

---

### 5. System Working Flow
**Filename:** `5_system_working_flow.jpg`

Complete user journey from first visit to logout:

**Landing & Authentication Phase:**
1. User visits site
2. System checks: logged in?
3. If NO: show landing page with value proposition
4. User chooses: Sign Up, Login, or Forgot Password

**Signup Path:**
1. Fill form, validate input
2. Hash password, save to MongoDB
3. Send OTP email
4. User verifies OTP
5. Account marked as verified

**Login Path:**
1. Enter email and password
2. Validate credentials
3. Create Flask session
4. Redirect to main application

**Main App Phase:**
1. Show map and search interface
2. User chooses search method:
   - City & radius dropdown
   - GPS location button
   - Name search box
   - Category/season filters
3. System loads places from MongoDB
4. Calculate distances (Haversine formula)
5. Filter and sort results
6. Display as cards and map pins
7. User clicks place to see full details

**Exit:**
1. User clicks Logout
2. Session cleared
3. Redirect to landing page

---

## 🔧 Generate New Images

If you modify any Mermaid diagram and want to regenerate the JPG image:

### Method 1: Using Mermaid.live (Online)
1. Go to https://mermaid.live
2. Open the `.md` file (e.g., `1_system_architecture.md`)
3. Copy the Mermaid code (between `` ```mermaid `` and `` ``` ``)
4. Paste into mermaid.live editor
5. Make your edits
6. Click Download → JPG
7. Save over the old file in `diagrams/` folder

### Method 2: Using VS Code with Mermaid Extension
1. Install "Mermaid" extension in VS Code
2. Open the `.md` file
3. Click preview icon (top right)
4. Edit the Mermaid code
5. Right-click preview → Export as PNG
6. Convert PNG to JPG (or download directly as JPG if available)

### Method 3: Using Command Line (Puppeteer)
```bash
# Install Puppeteer (one-time)
npm install puppeteer

# Create HTML from Mermaid
# (See generate_diagrams_html.py for template)

# Convert HTML to JPG
node convert_html_to_jpg.js
```

---

## 📚 Additional Resources

### Mermaid Diagram Types
- **Graph/Flowchart:** Boxes with arrows showing flow (used in most diagrams)
- **Sequence:** Timeline of interactions between actors
- **Gantt:** Project timeline
- **Class:** Object-oriented relationships
- **State:** State transitions

### Related Files
- `diagrams/README.md` — Detailed diagram guide
- `diagrams/*.md` — Mermaid source code for all diagrams
- `README.md` — Main project documentation
- `CHANGELOG.md` — All changes to the project

---

## ✨ What's Included

In the `diagrams/` folder you now have:

```
diagrams/
├── README.md                         ← Overview & instructions
│
├── 1_system_architecture.jpg         ← IMAGE - System architecture
├── 1_system_architecture.md          ← Source - Mermaid code
│
├── 2_data_flow_1_search.jpg          ← IMAGE - Location search flow
├── 2_data_flow_1_search.md           ← Source - Mermaid code
│
├── 3_data_flow_2_auth.jpg            ← IMAGE - Authentication flow
├── 3_data_flow_2_auth.md             ← Source - Mermaid code
│
├── 4_use_case_diagram.jpg            ← IMAGE - Use cases & features
├── 4_use_case_diagram.md             ← Source - Mermaid code
│
├── 5_system_working_flow.jpg         ← IMAGE - Complete user journey
└── 5_system_working_flow.md          ← Source - Mermaid code
```

---

## 🎯 Next Steps

1. **View:** Open any `.jpg` file to see the diagram
2. **Print:** Right-click → Print for physical copies
3. **Share:** Email or upload to GitHub
4. **Embed:** Insert into presentations or documents
5. **Edit:** Open `.md` file and modify at mermaid.live if needed

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't open JPG file | Try a different image viewer (Photos, Preview, Firefox) |
| Image too small on screen | Zoom in (Ctrl/Cmd + scroll) or open in web browser |
| Need to edit diagram | Open corresponding `.md` file and edit at mermaid.live |
| Want PNG instead | Convert JPG to PNG using online converter or ImageMagick |
| Quality issues | Original diagrams are 90% quality JPG for balance |

---

**Generated:** November 20, 2026
**System:** Maharashtra Places - Location Based Recommendation System
**All diagrams created as black and white JPG images, ready for viewing, printing, and sharing.**
