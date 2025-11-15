# Shadowrun Campaign Manager & Map Generator

A full-stack Python application for managing Shadowrun characters and generating dynamic campaign maps for Game Masters and players.

## Project Objectives

This application aims to provide a comprehensive platform for Shadowrun campaigns by combining character management with dynamic map generation capabilities. The system enables players to create and maintain their characters while giving Game Masters powerful tools to build, share, and dynamically generate campaign maps.

## Features

### Player Features
- **User Authentication**: Secure login and registration system
- **Character Registration**: Create and register Shadowrun characters
- **Character Management**: View, edit, and manage character details including:
  - Attributes and skills with 9 skill categories
  - Equipment and gear
  - Cyberware and bioware
  - Spells, adept powers, and complex forms
  - Character contacts with connection and loyalty ratings
  - Character background and notes
- **Dice Rolling System**: Integrated Shadowrun 5e dice mechanics
  - Pool-based D6 rolling with hit calculation
  - Rule of Six (exploding 6s) and glitch detection
  - Dice presets for quick common rolls
  - Roll history tracking
  - Character-specific preset management

### Game Master Features
- **Map Builder**: Interactive visual interface to create and edit custom campaign maps
  - Grid-based map editor with tile painting tools
  - Support for multiple terrain types (urban, wilderness, corporate, underground, mixed)
  - Token/object placement system with 9 object types (NPCs, enemies, items, objectives, traps, entrances, cover, vehicles, markers)
  - X/Y coordinate positioning with custom icons and colors
  - Visibility controls for player vs GM-only objects
  - Visual map display with color-coded tiles
- **Dynamic Map Generation**: Procedurally generate maps using advanced algorithms
  - **5 Generation Algorithms**:
    - Random: Simple terrain distribution for outdoor areas
    - BSP (Binary Space Partitioning): Creates rooms and corridors ideal for buildings
    - Cellular Automata: Organic cave-like structures perfect for natural environments
    - Random Walk: Winding paths and tunnels for underground passages
    - Maze: Complex mazes using recursive backtracking
  - 5 environment types with unique terrain distributions
  - Configurable map dimensions (5-100 tiles)
  - Seed-based generation for reproducible maps
  - Generation presets for quick map creation
- **Map Sharing**: Share maps with specific players or make them public
- **NPC Generator**: Procedurally generate NPCs with complete stats and backgrounds
  - **22 archetype templates** including:
    - **Runner Archetypes**: Street Samurai, Combat Mage, Decker, Face, Adept, Rigger, Street Shaman, Technomancer, Weapon Specialist, Covert Ops
    - **Civilian/Vendor Archetypes**: Gun Vendor, Clothing Vendor, Melee Vendor, Drug Dealer, Pawn Shop Vendor, Food Vendor, Street Performer, Companion, Street Doc (Ripper Doc), Security Guard, Thug, Thief
  - 4 threat levels (Low, Medium, High, Extreme) for scaling difficulty
  - Randomized attributes, skills, and equipment based on archetype
  - Procedural name generation with Shadowrun street aliases
  - Automatic physical descriptions and background stories tailored to archetype
  - Bulk generation support (create up to 20 NPCs at once)
  - Separate NPC management from player characters
- **Campaign Management**: Organize and manage multiple campaigns with comprehensive session tracking

## Technology Stack

- **Backend**: Python
  - Web framework (Django)
  - MySQL Database ORM
  - Authentication system

- **Frontend**: Python-based web framework
  - Template rendering
  - Interactive map interface
  - Responsive design

## Installation

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)
- **Choose one database:**
  - SQLite (included with Python, for development/testing)
  - MySQL (recommended for production or concurrent usage)

### Initial Setup (Common Steps)

Follow these steps regardless of which database you choose:

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/dnd-campaign-map-generator.git
cd dnd-campaign-map-generator
```

2. **Create and activate a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install base dependencies**
```bash
venv/bin/pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings (especially database configuration)
```

**Note:** The `logs/` directory is already included in the repository and will be created automatically when you clone. Log files are automatically generated when the application runs.

Now choose your database path:

---

### Option A: SQLite Setup (Quick Start)

**Best for:** Development, testing, single-user usage

**Pros:** No installation needed, simple setup
**Cons:** May encounter "database is locked" errors under concurrent load

#### Steps:

1. **Ensure `.env` uses SQLite** (default):
```bash
USE_MYSQL=False
# or simply leave USE_MYSQL commented out
```

2. **Run database migrations**
```bash
venv/bin/python manage.py migrate
```

3. **Create a superuser** (for admin access)
```bash
venv/bin/python manage.py createsuperuser
```

4. **Populate sample data** (recommended)
```bash
venv/bin/python manage.py populate_sample_data
```
This adds default Shadowrun qualities, gear, weapons, armor, and cyberware. Without this, the character creation wizard (especially step 4: Qualities) will be empty.

5. **Run the development server**
```bash
venv/bin/python manage.py runserver
```

6. **Access the application**
- Main site: http://localhost:8000
- Admin panel: http://localhost:8000/admin

---

### Option B: MySQL Setup (Recommended for Production)

**Best for:** Production deployments, multi-user environments, avoiding database locks

**Pros:** Better concurrency, no locking issues, production-ready
**Cons:** Requires MySQL installation and configuration

#### Path 1: MySQL Already Installed and Running

If MySQL is already installed:

1. **Install build tools and MySQL development headers**
```bash
sudo apt update
sudo apt install libmysqlclient-dev pkg-config build-essential python3-dev
```

2. **Install MySQL Python client**
```bash
venv/bin/pip install mysqlclient
```

3. **Create the database**
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS shadowrun_campaign CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

4. **Update `.env` file** with your MySQL credentials:
```bash
USE_MYSQL=True
DB_NAME=shadowrun_campaign
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

5. **Run database migrations**
```bash
venv/bin/python manage.py migrate
```

6. **Create a superuser**
```bash
venv/bin/python manage.py createsuperuser
```

7. **Populate sample data**
```bash
venv/bin/python manage.py populate_sample_data
```

8. **Run the development server**
```bash
venv/bin/python manage.py runserver
```

9. **Access the application**
- Main site: http://localhost:8000
- Admin panel: http://localhost:8000/admin

#### Path 2: Install MySQL from Scratch

If MySQL is not installed:

1. **Install MySQL Server and build tools** (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install mysql-server libmysqlclient-dev pkg-config build-essential python3-dev
```

2. **Start and enable MySQL service**
```bash
sudo systemctl start mysql
sudo systemctl enable mysql
```

3. **Verify MySQL is running**
```bash
sudo systemctl status mysql
```
You should see "active (running)" in green.

4. **Set MySQL root password**
```bash
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your-password-here'; FLUSH PRIVILEGES;"
```
Replace `your-password-here` with your desired password.

5. **Install MySQL Python client**
```bash
venv/bin/pip install mysqlclient
```

6. **Create the database**
```bash
mysql -u root -prootpassword -e "CREATE DATABASE IF NOT EXISTS shadowrun_campaign CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```
Note: No space between `-p` and your password.

7. **Update `.env` file** with your MySQL credentials:
```bash
USE_MYSQL=True
DB_NAME=shadowrun_campaign
DB_USER=root
DB_PASSWORD=your-password-here
DB_HOST=localhost
DB_PORT=3306
```

8. **Run database migrations**
```bash
venv/bin/python manage.py migrate
```

9. **Create a superuser**
```bash
venv/bin/python manage.py createsuperuser
```

10. **Populate sample data**
```bash
venv/bin/python manage.py populate_sample_data
```

11. **Run the development server**
```bash
venv/bin/python manage.py runserver
```

12. **Access the application**
- Main site: http://localhost:8000
- Admin panel: http://localhost:8000/admin

---

### Switching Between SQLite and MySQL

To switch databases after initial setup:

1. Update `USE_MYSQL` in `.env` (True for MySQL, False for SQLite)
2. Run migrations: `venv/bin/python manage.py migrate`
3. Restart the server

**Note:** Data is not automatically transferred between databases. You'll need to export/import data or use fixtures if switching with existing data.

## Project Structure

```
dnd-campaign-map-generator/
├── shadowrun_campaign/      # Main Django project settings
│   ├── settings.py          # Project configuration
│   ├── urls.py              # Main URL routing
│   └── wsgi.py              # WSGI configuration
├── accounts/                # User authentication app
│   ├── views.py             # Login, register, profile views
│   └── urls.py              # Account URLs
├── characters/              # Character management app
│   ├── models.py            # Character data models
│   ├── views.py             # Character CRUD views
│   └── urls.py              # Character URLs
├── maps/                    # Map building and generation app
│   ├── models.py            # Map data models
│   ├── views.py             # Map CRUD and generation views
│   └── urls.py              # Map URLs
├── campaigns/               # Campaign management app
│   ├── models.py            # Campaign data models
│   ├── views.py             # Campaign CRUD views
│   └── urls.py              # Campaign URLs
├── dice/                    # Dice rolling system app
│   ├── models.py            # Dice roll and preset models
│   ├── views.py             # Dice roller views
│   ├── utils.py             # Shadowrun 5e dice mechanics
│   └── urls.py              # Dice roller URLs
├── templates/               # HTML templates
│   ├── base.html            # Base template
│   └── home.html            # Homepage template
├── static/                  # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── media/                   # User-uploaded files
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
└── .gitignore               # Git ignore rules
```

## Map System Features

The map builder provides comprehensive tools for creating and managing campaign maps:

### Map Models
- **Map**: Main map entity with dimensions, type, ownership, and sharing settings
- **MapTile**: Individual tiles with terrain types, walkability, transparency, and custom colors
- **MapObject**: Placeable objects (NPCs, enemies, items, markers) with stats and visibility settings
- **MapGenerationPreset**: Reusable presets for procedural map generation

### Map Types
- **Urban**: Streets, sidewalks, and buildings for city environments
- **Wilderness**: Natural terrain with grass, forests, and water
- **Corporate Facility**: Indoor spaces with floors, walls, doors, and elevators
- **Underground/Sewer**: Tunnels, caves, and underground passages
- **Mixed Environment**: Combination of multiple terrain types

### Key Features
- **Visual Grid Editor**: Interactive map display with color-coded tiles
- **Terrain Painting**: Click-to-paint interface for changing tile types
- **Advanced Procedural Generation**: Choose from 5 different algorithms with customizable parameters
  - **BSP**: Room-and-corridor layouts perfect for dungeons and buildings
    - Customizable: min/max room size, corridor width
  - **Cellular Automata**: Organic cave systems with natural-looking structures
    - Customizable: smoothing iterations, wall density
  - **Random Walk**: Winding tunnels and passages
    - Customizable: number of steps, tunnel width probability
  - **Maze**: Complex recursive mazes for puzzle-oriented maps
    - Customizable: path width
  - **Random**: Simple distribution for outdoor environments
- **Map Sharing**: Control visibility with public/private settings and user-specific sharing
- **Object Placement**: Add and manage NPCs, enemies, items, and markers
- **Customizable Dimensions**: Create maps from 5x5 to 100x100 tiles
- **Reproducible Maps**: Use seeds to generate identical maps
- **Admin Interface**: Full CRUD operations for all map-related models

### Generation Algorithms Explained

#### BSP (Binary Space Partitioning)
Creates structured layouts with rooms connected by corridors. The algorithm recursively divides the map into smaller sections and places rooms in each section, then connects them with L-shaped corridors. Perfect for:
- Office buildings and corporate facilities
- Dungeons with distinct rooms
- Structured facility layouts

#### Cellular Automata
Simulates natural cave formation through iterative rules. Starts with random noise and applies smoothing rules over multiple iterations to create organic, cave-like structures. Ideal for:
- Natural cave systems
- Underground ruins
- Organic wilderness areas

#### Random Walk
Creates winding paths by randomly "walking" through the map, carving out tunnels as it goes. Sometimes creates wider passages for variety. Great for:
- Sewer systems
- Underground tunnels
- Winding mountain paths

#### Maze
Uses recursive backtracking to create complex, puzzle-like mazes. Guarantees all areas are connected with exactly one path between any two points. Best for:
- Puzzle-oriented challenge maps
- Complex facility layouts
- Labyrinthine dungeons

#### Random Distribution
Simple algorithm that randomly places different terrain types across the map. Good baseline for:
- Open outdoor areas
- Quick test maps
- Areas with varied terrain

### Algorithm Customization Parameters

Each generation algorithm now supports customizable parameters to fine-tune the map output:

#### BSP Parameters
- **Min Room Size** (3-15): Minimum dimension for generated rooms. Smaller values create tighter, more cramped layouts.
- **Max Room Size** (5-30): Maximum dimension for generated rooms. Larger values create more spacious areas.
- **Corridor Width** (1-3): Width of connecting corridors. Wider corridors make navigation easier.

#### Cellular Automata Parameters
- **Iterations** (1-10): Number of smoothing passes. More iterations create smoother, more refined cave walls.
- **Wall Probability** (0.1-0.9): Initial density of walls. Lower values (0.3-0.4) create open caves, higher values (0.5-0.6) create dense cave systems.

#### Random Walk Parameters
- **Steps**: Number of walking steps. More steps create longer, more complex tunnel systems. Leave empty for automatic calculation.
- **Tunnel Width Probability** (0.0-1.0): Chance to widen tunnels. Higher values create more spacious passages.

#### Maze Parameters
- **Path Width** (1-3): Width of maze corridors. Wider paths make the maze easier to navigate.

### Map Access URLs
- `/maps/` - List all accessible maps
- `/maps/create/` - Create a new blank map
- `/maps/generate/` - Generate a map procedurally (choose algorithm here)
- `/maps/<id>/` - View and edit map in builder interface
- `/maps/<id>/edit/` - Edit map settings
- `/maps/<id>/delete/` - Delete a map

## Campaign Session Management

The campaign system provides comprehensive tools for organizing and running Shadowrun campaigns:

### Campaign Features
- **Campaign Creation**: Create and manage multiple campaigns with customizable settings
- **Player Management**: Add players to campaigns and track their characters
- **Campaign Status Tracking**: Monitor campaign progress (Planning, Active, On Hold, Completed, Archived)
- **Flexible Settings**: Configure starting karma and resources for new characters
- **Public & Private Notes**: Maintain GM-only notes and player-visible campaign information
- **Character & Map Integration**: Link characters and maps to campaigns for easy access
- **Campaign Dashboard**: View all campaign details, sessions, characters, and maps in one place

### Session Features
- **Session Tracking**: Create and manage individual game sessions within campaigns
- **Scheduling**: Track scheduled and actual session dates and times
- **Session Status**: Monitor session state (Planned, In Progress, Completed, Cancelled)
- **Comprehensive Notes**: Maintain GM preparation notes, public session recaps, and player summaries
- **Rewards Management**: Track karma and nuyen awarded to characters
- **Combat Tracking**: Record encounters faced and enemies defeated
- **Event Logging**: Document objectives completed, important NPCs encountered, and loot acquired
- **Resource Linking**: Associate maps and characters with specific sessions
- **Session Objectives**: Create and track individual objectives for each session

### Campaign Statistics
- Automatic tracking of total and completed sessions
- Character participation tracking across sessions
- Map usage statistics
- Campaign timeline and history

### Campaign Access URLs
- `/campaigns/` - List all campaigns (GM and player)
- `/campaigns/create/` - Create a new campaign
- `/campaigns/<id>/` - View campaign dashboard with all sessions
- `/campaigns/<id>/edit/` - Edit campaign settings
- `/campaigns/<id>/delete/` - Delete a campaign
- `/campaigns/<id>/sessions/create/` - Create a new session
- `/campaigns/<id>/sessions/<session_id>/` - View session details
- `/campaigns/<id>/sessions/<session_id>/edit/` - Edit session
- `/campaigns/<id>/sessions/<session_id>/delete/` - Delete session

## Roadmap

### Completed
- [x] Django project structure setup
- [x] User authentication system (login/logout/register)
- [x] Basic app structure (accounts, characters, maps, campaigns)
- [x] URL routing configuration
- [x] Base templates with Bootstrap 5
- [x] Static files configuration
- [x] Database configuration (SQLite & MySQL support)
- [x] Character data models (Shadowrun attributes, skills, etc.)
- [x] Character creation wizard (8-step process)
- [x] Character sheet interface
- [x] Character equipment and gear management
- [x] Qualities (positive/negative traits) system
- [x] Cyberware and bioware tracking
- [x] Map data models (Map, MapTile, MapObject, MapGenerationPreset)
- [x] Basic map builder interface with visual grid editor
- [x] Map CRUD operations (create, read, update, delete)
- [x] Map sharing system (public maps and user-specific sharing)
- [x] Interactive tile painting tools
- [x] Map object placement system
- [x] Admin interface for map management
- [x] Advanced map generation algorithms:
  - [x] BSP (Binary Space Partitioning) for room-and-corridor layouts
  - [x] Cellular Automata for organic cave systems
  - [x] Random Walk for winding tunnels
  - [x] Maze generation using recursive backtracking
  - [x] Random distribution algorithm
- [x] Algorithm customization parameters (room sizes, corridor widths, iteration counts)
- [x] Map generation preview before saving (AJAX-based preview with accept/regenerate options)
- [x] AJAX-based tile editing with paint brush mode (click-and-drag painting, auto-save with visual feedback)
- [x] Campaign Management System:
  - [x] Campaign creation and management
  - [x] Campaign status tracking (Planning, Active, On Hold, Completed, Archived)
  - [x] Player and character assignment to campaigns
  - [x] Campaign settings (starting karma/resources)
  - [x] Public and private campaign notes
  - [x] Campaign dashboard with full overview
- [x] Session Management System:
  - [x] Session creation and tracking within campaigns
  - [x] Session scheduling (planned and actual dates)
  - [x] Session status tracking (Planned, In Progress, Completed, Cancelled)
  - [x] Session notes (GM private, public recap, player summary)
  - [x] Rewards tracking (karma, nuyen)
  - [x] Combat statistics (encounters, enemies defeated)
  - [x] Event logging (objectives, NPCs, loot)
  - [x] Character and map linking to sessions
  - [x] Session objectives system
- [x] Dice Rolling System:
  - [x] Pool-based D6 rolling with Shadowrun 5e mechanics
  - [x] Hit calculation (5s and 6s)
  - [x] Rule of Six (exploding 6s)
  - [x] Glitch and Critical Glitch detection
  - [x] Edge support and optional thresholds
  - [x] Dice preset management for quick rolls
  - [x] Roll history tracking
  - [x] Character-specific dice presets
  - [x] AJAX-based quick roller interface
- [x] Enhanced Character Skills System:
  - [x] 9 skill categories (combat, physical, social, technical, vehicle, magical, resonance, knowledge, language)
  - [x] Skill ratings (0-12) with specializations
  - [x] Linked attribute system for dice pool calculation
  - [x] Automatic dice pool calculation
  - [x] Full CRUD operations for character skills
- [x] Magic and Spell Management:
  - [x] Spell system with 5 categories (combat, detection, health, illusion, manipulation)
  - [x] Physical/Mana spell types
  - [x] Range and duration tracking
  - [x] Drain value calculation
  - [x] Character spell associations
  - [x] Complex forms for technomancers
  - [x] Adept power system with level support
  - [x] Full admin interface for magical abilities
- [x] Token/Character Placement on Maps:
  - [x] MapObject system with X/Y coordinate positioning
  - [x] 9 object types (NPC, Enemy, Item, Objective, Trap, Entrance, Cover, Vehicle, Marker)
  - [x] Icon and color customization
  - [x] Visibility controls for players vs GM
  - [x] Movement and vision blocking properties
  - [x] Custom stats storage (JSON)
- [x] NPC Management with Character Links:
  - [x] Contact system with character relationships
  - [x] Contact archetypes and descriptions
  - [x] Connection rating (1-12) and loyalty rating (1-6)
  - [x] Notes and relationship tracking
  - [x] Full admin interface for contact management
- [x] NPC Generator (Procedural Generation):
  - [x] 22 archetype templates including:
    - [x] 10 Runner archetypes (Street Samurai, Combat Mage, Decker, Face, Adept, Rigger, Street Shaman, Technomancer, Weapon Specialist, Covert Ops)
    - [x] 12 Civilian/Vendor archetypes (Gun Vendor, Clothing Vendor, Melee Vendor, Drug Dealer, Pawn Shop Vendor, Food Vendor, Street Performer, Companion, Street Doc, Security Guard, Thug, Thief)
  - [x] 4 threat levels (Low, Medium, High, Extreme) with scaling attributes and resources
  - [x] Randomized attributes based on archetype priorities
  - [x] Procedural name generation with Shadowrun aliases
  - [x] Random physical descriptions and backgrounds tailored to archetype type
  - [x] Different background generation for runners vs civilians/vendors
  - [x] Automatic skill allocation based on archetype
  - [x] Bulk generation (1-20 NPCs at once)
  - [x] Separate NPC list from player characters
  - [x] Full integration with character management system

- [x] Real-time Combat Tracker:
  - [x] Combat encounter management with round/turn tracking
  - [x] Participant tracking with initiative order
  - [x] HP and damage tracking (physical/stun for Shadowrun)
  - [x] Status effects and condition monitoring
  - [x] Real-time AJAX updates for combat flow
  - [x] Automatic session statistics updates
- [x] Grid Measurement and Distance Tools:
  - [x] Distance measurement tool with Euclidean and Manhattan calculations
  - [x] Visual path highlighting between tiles
  - [x] Line-of-sight calculation using Bresenham's algorithm
  - [x] Mode-based UI (paint, measure, fog of war)
- [x] Fog of War System:
  - [x] Toggle fog of war per map
  - [x] Reveal/hide tiles with configurable radius
  - [x] Persistent revealed tile tracking
  - [x] Visual fog overlay for hidden tiles
  - [x] GM controls for fog management

- [x] Combat Log and History Tracking:
  - [x] Comprehensive event logging for all combat actions
  - [x] Automatic logging of combat start/end, rounds, turns
  - [x] Damage and healing event tracking
  - [x] Effect application and expiration tracking
  - [x] Participant defeat tracking
  - [x] Organized log view grouped by combat round
  - [x] Visual log interface with event type highlighting
  - [x] Combat statistics and duration tracking
  - [x] Full admin interface for log management

### In Progress

### Planned
- [ ] Real-time collaborative map editing
- [ ] Advanced pathfinding with terrain cost calculation
- [ ] Multi-layer map support (ground, objects, lighting layers)
- [ ] Map annotations and drawing tools (freehand, shapes, text)
- [ ] Import/export maps in common formats (JSON, image)
- [ ] Character portrait and token management
- [ ] Advanced search and filtering for characters/campaigns
- [ ] Automated combat AI for NPCs

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

buglish@yahoo.com
