# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django-based Shadowrun Campaign Manager and Map Generator. The application provides character management for players and campaign/map building tools for Game Masters.

**Tech Stack**: Django 5.0.1, Django Channels 4.0+, Bootstrap 5, crispy-forms, SQLite (dev) / MySQL (prod optional), Redis (optional for WebSocket scaling)

## Development Commands

### Initial Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
venv/bin/pip install -r requirements.txt

# Configure environment (optional)
cp .env.example .env
# Edit .env as needed

# Run migrations
venv/bin/python manage.py migrate

# Create superuser for admin access
venv/bin/python manage.py createsuperuser
```

### Daily Development
```bash
# Run development server
venv/bin/python manage.py runserver

# Create new migrations after model changes
venv/bin/python manage.py makemigrations

# Apply migrations
venv/bin/python manage.py migrate

# Run tests
venv/bin/python manage.py test

# Run tests for specific app
venv/bin/python manage.py test accounts
venv/bin/python manage.py test characters

# Collect static files (for production)
venv/bin/python manage.py collectstatic
```

### Database Management
```bash
# Open Django shell for database queries
venv/bin/python manage.py shell

# Create database dump (SQLite)
sqlite3 db.sqlite3 .dump > backup.sql

# Reset database (caution: deletes all data)
rm db.sqlite3
venv/bin/python manage.py migrate
```

## Architecture

### Django Apps Structure

The project follows a modular Django app architecture with four main apps:

1. **accounts**: User authentication and profile management
   - Uses Django's built-in auth system
   - Custom registration view with UserCreationForm
   - URL namespace: `accounts:`
   - Login redirects to home, logout redirects to home (configured in settings)

2. **characters**: Shadowrun character management
   - Comprehensive character models including attributes, skills, equipment, contacts, languages, and magic systems
   - URL namespace: `characters:`
   - All views require login (`@login_required`)
   - 8-step character creation wizard
   - Full CRUD operations for characters

3. **maps**: Map builder and generation system
   - Models not yet implemented (planned: map data, tiles, dynamic generation params)
   - URL namespace: `maps:`

4. **campaigns**: Campaign organization and session management
   - Models not yet implemented (planned: campaign, sessions, GM tools)
   - URL namespace: `campaigns:`

### Configuration

- **Main settings**: `shadowrun_campaign/settings.py`
- **URL routing**: Main routing in `shadowrun_campaign/urls.py`, each app has its own `urls.py` with namespaced patterns
- **Environment variables**: Managed via python-dotenv, loaded from `.env` file
- **Database**: SQLite by default; MySQL support via `USE_MYSQL=True` env var
- **Static files**: Located in `static/` directory, served via `STATICFILES_DIRS` in development
- **Templates**: Project-level templates in `templates/`, app-level templates should use `app_name/template.html` pattern
- **Media files**: User uploads go to `media/` directory

### Template System

- **Base template**: `templates/base.html` - includes Bootstrap 5, navbar with auth state, flash messages, footer
- **Template blocks**: `title`, `content`, `extra_css`, `extra_js`
- **Crispy Forms**: Configured for Bootstrap 5 (`CRISPY_TEMPLATE_PACK = "bootstrap5"`)
- **Static files**: Use `{% load static %}` and `{% static 'path' %}`

### Authentication Flow

- Login URL: `/accounts/login/` (name: `accounts:login`)
- Register URL: `/accounts/register/` (name: `accounts:register`)
- Profile URL: `/accounts/profile/` (name: `accounts:profile`)
- `LOGIN_URL = 'accounts:login'` - redirects unauthenticated users here
- `LOGIN_REDIRECT_URL = 'home'` - redirects after successful login
- `LOGOUT_REDIRECT_URL = 'home'` - redirects after logout

## Development Guidelines

### Adding New Models

When creating data models for characters, maps, or campaigns:

1. Define models in the app's `models.py`
2. Run `venv/bin/python manage.py makemigrations`
3. Review the generated migration file
4. Apply with `venv/bin/python manage.py migrate`
5. Register in `admin.py` for admin interface access

### URL Patterns

All apps use namespaced URLs. When adding new views:
- Add URL pattern to app's `urls.py`
- Use `app_name = 'appname'` in urls.py
- Reference in templates as `{% url 'namespace:view_name' %}`
- Reference in views as `reverse('namespace:view_name')`

### MySQL Setup (Optional)

To switch from SQLite to MySQL:
1. Install system dependencies: `apt install libmysqlclient-dev pkg-config`
2. Install Python package: `venv/bin/pip install mysqlclient==2.2.1`
3. Update `.env`: Set `USE_MYSQL=True` and configure DB credentials
4. The settings.py automatically switches database backend based on `USE_MYSQL` env var

## Character Creation System

The character app implements a complete Shadowrun character creation wizard with 8 steps:

1. **Basic Information**: Name, race (Human, Dwarf, Elf, Ork, Troll), archetype
2. **Role & History**: Role selection, background story, locations, attitudes
3. **Priorities**: Assign A-E priorities to metatype, attributes, magic, skills, resources
4. **Qualities**: Select positive (cost karma) and negative (grant karma) traits
5. **Attributes**: Allocate points to Body, Agility, Reaction, Strength, Charisma, Intuition, Logic, Willpower, Edge, Magic, Resonance
6. **Karma**: Set total karma, spent karma, and available karma
7. **Gear**: Select equipment, weapons, armor, cyberware from catalog
8. **Finishing Touches**: Set resources (nuyen) and essence

### Character Data Models

**Core Character Models:**
- **Character**: Main model with attributes, priorities, history, physical description, lifestyle, reputation, condition monitors
  - Includes derived attributes as properties: initiative, physical/stun monitors, limits, armor rating
  - Physical description fields: age, sex, height, weight, eyes, hair, skin, distinguishing features
  - Lifestyle and reputation: lifestyle type, street cred, notoriety, public awareness
  - Condition monitors: physical and stun damage tracking

**Equipment & Qualities:**
- **Quality**: Catalog of positive/negative traits with karma costs
- **CharacterQuality**: Junction table linking characters to their selected qualities
- **Gear**: Enhanced catalog with weapon stats (damage, AP, firing mode, RC, ammo, range) and armor stats
- **CharacterGear**: Junction table linking characters to their equipment with quantity tracking

**Skills System:**
- **Skill**: Skills catalog with categories (combat, physical, social, technical, vehicle, magical, resonance, knowledge, language)
- **CharacterSkill**: Character skills with ratings, specializations, and calculated dice pools

**Social & Knowledge:**
- **Contact**: NPCs with connection and loyalty ratings, archetype, and descriptions
- **Language**: Known languages with proficiency levels (native, fluent, conversational, basic)

**Magic Systems:**
- **Spell**: Spells catalog (for mages/shamans) with category, type, range, duration, and drain
- **CharacterSpell**: Spells known by character
- **AdeptPower**: Adept powers catalog with power point costs
- **CharacterAdeptPower**: Adept powers for character with levels
- **ComplexForm**: Complex forms catalog (for technomancers) with target, duration, and fading
- **CharacterComplexForm**: Complex forms known by character

### Sample Data Management

Run `venv/bin/python manage.py populate_sample_data` to populate:
- 6 positive qualities (Ambidextrous, Catlike, High Pain Tolerance, Lucky, Natural Athlete, Toughness)
- 6 negative qualities (Allergy, Bad Luck, Code of Honor, Combat Paralysis, Distinctive Style, Phobia)
- 5 weapons (Ares Predator V, Fichetti Security 600, AK-97, Remington 990, Knife)
- 3 armor items (Armor Jacket, Lined Coat, Full Body Armor)
- 3 cyberware items (Cybereyes, Wired Reflexes, Dermal Plating)
- Electronics and miscellaneous gear
- **81 skills** across 9 categories (combat, physical, social, technical, vehicle, magical, resonance)
- **60+ spells** across 5 categories (combat, detection, health, illusion, manipulation)
- **25 adept powers** with descriptions and power point costs
- **15 complex forms** for technomancers

### Character Wizard Session Management

Character creation uses Django sessions to track progress:
- `character_id` in session stores the character being created
- `creation_step` field tracks current step (1-8)
- `is_complete` flag marks finished characters
- Users can navigate back through steps to modify choices
- Incomplete characters are marked with warning badges in the list view

## Map System

The map system provides comprehensive tools for creating, managing, and generating Shadowrun campaign maps.

### Map Data Models

**Core Map Models:**
- **Map**: Main map entity with dimensions (width/height), map_type (urban, wilderness, corporate, underground, mixed), owner, is_public, shared_with users
- **MapTile**: Individual tiles with terrain_type, x/y coordinates, is_walkable, is_transparent, custom_color
- **MapObject**: Placeable objects with object_type (npc, enemy, item, objective, trap, entrance, cover, vehicle, marker), x/y coordinates, name, icon, color, stats (JSON), is_visible_to_players, blocks_movement, blocks_vision
- **MapGenerationPreset**: Saved generation configurations with width, height, map_type, algorithm, seed, parameters (JSON), owner, is_public

### Map Builder Interface

- Visual grid editor at `/maps/<id>/` displays color-coded tiles
- Paint mode: Click-and-drag to paint terrain types
- Measure mode: Click two tiles to calculate distance and show path
- Fog of War mode: Reveal/hide tiles for players
- AJAX-based tile editing with auto-save and visual feedback
- Object placement interface for adding NPCs, enemies, items, markers, etc.

### Map Generation

URL: `/maps/generate/`

**5 Generation Algorithms:**
1. **BSP (Binary Space Partitioning)**: Creates structured room-and-corridor layouts
   - Parameters: min_room_size (3-15), max_room_size (5-30), corridor_width (1-3)
   - Best for: Buildings, corporate facilities, dungeons

2. **Cellular Automata**: Creates organic cave-like structures
   - Parameters: iterations (1-10), wall_probability (0.1-0.9)
   - Best for: Natural caves, underground ruins, wilderness

3. **Random Walk**: Creates winding tunnels and passages
   - Parameters: steps (optional), tunnel_width_probability (0.0-1.0)
   - Best for: Sewers, underground passages, mountain paths

4. **Maze**: Creates complex mazes using recursive backtracking
   - Parameters: path_width (1-3)
   - Best for: Puzzle maps, labyrinthine facilities

5. **Random**: Simple random terrain distribution
   - No parameters
   - Best for: Outdoor areas, quick test maps

**Generation Features:**
- Map dimensions: 5x5 to 100x100 tiles
- Seed-based generation for reproducibility
- Preview system: Generate → Preview → Accept/Regenerate
- Procedural cover placement: Configurable density (0.0-0.5), context-aware objects based on map type
- Cover levels: Light (+2 defense), Medium (+4 defense), Heavy (+6 defense, blocks movement/vision)

### Map Sharing

Maps can be shared in two ways:
- `is_public=True`: Map visible to all users
- `shared_with`: Many-to-many field for sharing with specific users
- Map owner always has full access
- Shared users can view and edit (depending on permissions)

## Campaign Management System

The campaign system organizes game sessions, tracks progress, and manages player characters and NPCs.

### Campaign Data Models

**Core Campaign Models:**
- **Campaign**: Main campaign entity with name, description, game_master (User), status (planning, active, on_hold, completed, archived), starting_karma, starting_resources, players (many-to-many with User), characters (many-to-many with Character), maps (many-to-many with Map), public_notes, gm_notes
- **Session**: Individual game sessions with campaign (FK), session_number, title, scheduled_date, actual_date, status (planned, in_progress, completed, cancelled), gm_notes, public_recap, player_summary, karma_awarded, nuyen_awarded, encounters_faced, enemies_defeated, objectives_completed_text, npcs_encountered_text, loot_acquired_text, characters_present, npcs_involved, maps_used
- **SessionObjective**: Objectives for sessions with session (FK), description, is_completed, order

### Campaign Features

**Campaign Dashboard** (`/campaigns/<id>/`):
- Campaign details and settings
- List of all sessions with status indicators
- Character roster with participation tracking
- Linked maps
- Statistics: Total sessions, completed sessions, timeline

**Session Management**:
- Create sessions at `/campaigns/<id>/sessions/create/`
- Track session scheduling (planned vs actual dates)
- Session status workflow: Planned → In Progress → Completed
- Separate notes: GM private notes, public recap, player summary
- Rewards: Track karma and nuyen awarded
- Combat statistics: Encounters faced, enemies defeated
- Event logging: Objectives, NPCs, loot (text fields)
- Character and NPC assignment
- Map linking for sessions

**Session Objectives**:
- Add objectives to sessions
- Real-time AJAX completion tracking
- Visual progress bars
- Drag-to-reorder objectives
- GM-only editing, player viewing

### Campaign URLs

- `/campaigns/` - List all campaigns (GM and player)
- `/campaigns/create/` - Create new campaign
- `/campaigns/<id>/` - Campaign dashboard
- `/campaigns/<id>/edit/` - Edit campaign settings
- `/campaigns/<id>/delete/` - Delete campaign
- `/campaigns/<id>/sessions/create/` - Create session
- `/campaigns/<id>/sessions/<session_id>/` - View session details
- `/campaigns/<id>/sessions/<session_id>/edit/` - Edit session
- `/campaigns/<id>/sessions/<session_id>/delete/` - Delete session

## NPC Generator

The NPC generator creates fully-functional Shadowrun NPCs with randomized attributes, skills, equipment, and backgrounds.

### NPC Generation

URL: `/characters/generate/`

**22 Archetype Templates:**
- **Runner Archetypes (10)**: Street Samurai, Combat Mage, Decker, Face, Adept, Rigger, Street Shaman, Technomancer, Weapon Specialist, Covert Ops
- **Civilian/Vendor Archetypes (12)**: Gun Vendor, Clothing Vendor, Melee Vendor, Drug Dealer, Pawn Shop Vendor, Food Vendor, Street Performer, Companion, Street Doc (Ripper Doc), Security Guard, Thug, Thief

**Threat Levels:**
- **Low**: Basic NPCs (e.g., security guards, civilians)
- **Medium**: Competent NPCs (e.g., gang members, low-level runners)
- **High**: Professional NPCs (e.g., corporate security, experienced runners)
- **Extreme**: Elite NPCs (e.g., prime runners, corporate specialists)

**Generation Features:**
- Randomized attributes scaled to threat level
- Automatic skill allocation based on archetype (e.g., Street Samurai gets combat skills, Decker gets hacking skills)
- Procedural name generation with Shadowrun street aliases
- Random physical descriptions (age, sex, height, weight, distinguishing features)
- Background stories tailored to archetype (runners get shadowrunner backstories, vendors get business backstories)
- Bulk generation: Create 1-20 NPCs at once
- NPCs marked with `is_npc=True` flag in Character model
- Separate NPC list at `/characters/npcs/`

**NPC URLs:**
- `/characters/generate/` - NPC generator form
- `/characters/npcs/` - List all NPCs
- `/characters/<id>/` - View NPC (same as character detail)

## Dice Rolling System

The dice rolling system implements Shadowrun 5e mechanics with pool-based D6 rolling.

### Dice Data Models

- **DiceRoll**: Stores roll results with character (optional FK), pool_size, roll_results (JSON list), hits, ones, is_glitch, is_critical_glitch, edge_used, threshold, is_success, description, timestamp
- **DicePreset**: Saved dice pools with character (optional FK), name, pool_size, description, is_quick_access

### Dice Mechanics

**Shadowrun 5e Rules:**
- Roll a pool of D6s
- 5s and 6s count as hits
- **Rule of Six**: Each 6 explodes (roll again and add to pool)
- **Glitch**: If more than half the dice show 1s
- **Critical Glitch**: Glitch with 0 hits
- **Edge**: Optional, can be used to add extra dice or ignore glitches
- **Threshold**: Optional target number of hits for success

**Dice Roller Interface:**
- URL: `/dice/` - Main dice roller page
- Quick roller: AJAX-based interface for fast rolls
- Roll history: View past rolls with full details
- Dice presets: Save common rolls (e.g., "Pistols Attack", "Perception Check")
- Character-specific presets: Link presets to characters for easy access

**Dice URLs:**
- `/dice/` - Main dice roller
- `/dice/roll/` - AJAX endpoint for rolling
- `/dice/presets/` - Manage presets
- `/dice/presets/create/` - Create preset
- `/dice/presets/<id>/edit/` - Edit preset
- `/dice/presets/<id>/delete/` - Delete preset

## Combat System

The combat system provides real-time tracking of combat encounters with initiative, damage, effects, and logging.

### Combat Data Models

**Core Combat Models:**
- **CombatEncounter**: Main combat entity with session (optional FK), name, description, current_round, current_turn, status (active, paused, completed), started_at, ended_at
- **CombatParticipant**: Characters/NPCs in combat with encounter (FK), character (optional FK), name, initiative, physical_hp, physical_max_hp, stun_hp, stun_max_hp, is_defeated, is_player_character, turn_order
- **CombatEffect**: Status effects on participants with participant (FK), name, effect_type (buff, debuff, dot, hot, condition), description, duration_rounds, color
- **CombatLog**: Event log with encounter (FK), round_number, event_type, description, timestamp

### Combat Features

**Combat Tracker Interface:**
- Real-time AJAX updates for combat flow
- Initiative order display with current turn highlighting
- Round/turn tracking with next turn buttons
- HP tracking for physical and stun damage
- Quick damage/heal buttons with confirmation
- Effect management: Add, view, remove effects
- Participant defeat tracking

**Combat Effects System:**
- 5 effect types: Buff (green), Debuff (red), DoT (orange), HoT (blue), Condition (purple)
- Duration tracking: Effects countdown each round
- Automatic expiration: Effects removed when duration reaches 0
- Visual badges: Effects displayed as colored badges on participant cards
- Modal interface for adding effects with name, type, description, duration

**Combat Log:**
- Comprehensive event logging for all combat actions
- Automatic logging: Combat start/end, rounds, turns, damage, healing, effects, defeats
- Organized by round: Log entries grouped for easy reading
- Event type highlighting: Different colors for different event types
- Full log view accessible from combat tracker

**Combat URLs:**
- `/combat/` - List all encounters
- `/combat/create/` - Create new encounter
- `/combat/<id>/` - Combat tracker interface
- `/combat/<id>/delete/` - Delete encounter

## Fog of War System

The fog of war system allows GMs to hide/reveal portions of maps to players.

### Fog of War Features

- Toggle fog of war per map (`has_fog_of_war` boolean on Map)
- Revealed tiles tracked in `MapTile.is_revealed` field
- GM controls: Reveal/hide tiles with configurable radius
- Visual fog overlay: Hidden tiles displayed with semi-transparent dark overlay
- Persistent tracking: Revealed state saved to database
- Map builder integration: Fog of War mode in map interface

**Usage:**
1. Enable fog of war for a map in map settings
2. In map builder, switch to Fog of War mode
3. Click tiles to reveal/hide with radius
4. Players only see revealed tiles

## Advanced Character Sheet

The advanced character sheet displays comprehensive calculated statistics for easy reference during gameplay.

### Advanced Sheet Features

URL: `/characters/<id>/advanced/`

**Calculated Properties:**
- **Movement**: Walk, Run, Sprint rates based on Agility
- **Carrying**: Lifting capacity and carrying capacity based on Strength and Body
- **Overflow**: Overflow damage threshold (Physical Condition Monitor + Body)
- **Social Pools**: Composure (Charisma + Willpower), Judge Intentions (Intuition + Charisma), Memory (Logic + Willpower)
- **Defense Pools**: Ranged Defense (Reaction + Intuition), Melee Defense (Reaction + Intuition)
- **Soak Pool**: Body + Armor Rating
- **Combat Stats**: Initiative, Physical/Mental Limits, Damage Monitors
- **Equipment Totals**: Total value of all gear
- **Qualities Impact**: Total karma cost of all qualities
- **Essence**: Total essence loss from cyberware

**Sheet Layout:**
- Visual damage track displays (checkboxes for each damage box)
- Organized stat boxes with color-coded sections
- Quick reference panels for combat and common actions
- Complete equipment listing with stats and totals
- Full skills table with dice pools
- Magic systems display (spells, adept powers, complex forms)
- Print-friendly layout for at-table reference

## Current State

The project is a comprehensive Shadowrun campaign management platform with:

### Character Management
- User authentication (login/register/logout)
- Complete 8-step character creation wizard
- Character listing, detail viewing, editing, and deletion
- Full character sheet display with all Shadowrun components:
  - Core attributes and derived attributes (initiative, limits, condition monitors)
  - Physical description and lifestyle management
  - Reputation tracking (street cred, notoriety, public awareness)
  - Skills system with 9 categories, ratings, specializations, and automatic dice pool calculations
  - Qualities (positive/negative traits)
  - Equipment with weapon stats (damage, AP, firing modes) and armor ratings
  - Contacts (NPCs with connection/loyalty) - Full CRUD operations
  - Languages with proficiency levels - Full CRUD operations
  - Magic systems with full CRUD operations:
    - Spells (for mages/shamans) - 5 categories with drain, range, duration
    - Adept Powers (for adepts) - with level tracking and power point costs
    - Complex Forms (for technomancers) - with fading and target types
- Advanced character sheet with comprehensive calculated stats:
  - Movement rates, carrying capacity, overflow damage
  - Defense pools (ranged, melee), soak pool
  - Visual damage track displays
  - Complete combat reference
  - Total equipment value and qualities karma impact
  - Print-friendly layout

### NPC Management
- Procedural NPC Generator with 22 archetype templates:
  - 10 Runner archetypes (Street Samurai, Combat Mage, Decker, Face, Adept, Rigger, Shaman, Technomancer, Weapon Specialist, Covert Ops)
  - 12 Civilian/Vendor archetypes (Gun Vendor, Clothing Vendor, Drug Dealer, Street Doc, Security Guard, Thug, etc.)
- 4 threat levels (Low, Medium, High, Extreme) with scaling attributes
- Randomized attributes, skills, equipment based on archetype
- Procedural name generation with Shadowrun street aliases
- Automatic physical descriptions and backgrounds
- Bulk generation (1-20 NPCs at once)
- Separate NPC list from player characters

### Map System
- Complete map builder with visual grid editor
- Map models: Map, MapTile, MapObject, MapGenerationPreset
- Interactive tile painting tools with click-and-drag functionality
- AJAX-based tile editing with auto-save
- 5 terrain types: Urban, Wilderness, Corporate, Underground, Mixed
- Token/object placement with 9 object types (NPCs, enemies, items, objectives, traps, entrances, cover, vehicles, markers)
- X/Y coordinate positioning with custom icons and colors
- Visibility controls for player vs GM-only objects
- Map sharing system (public maps and user-specific sharing)
- Distance measurement tool with Euclidean and Manhattan calculations
- Line-of-sight calculation using Bresenham's algorithm
- Fog of War system with reveal/hide tiles and persistent tracking

#### Map Generation
- 5 procedural generation algorithms:
  - **BSP (Binary Space Partitioning)**: Room-and-corridor layouts for buildings
  - **Cellular Automata**: Organic cave systems
  - **Random Walk**: Winding tunnels
  - **Maze**: Complex mazes using recursive backtracking
  - **Random Distribution**: Simple terrain distribution for outdoor areas
- Algorithm customization parameters (room sizes, corridor widths, iteration counts, etc.)
- Configurable map dimensions (5x5 to 100x100 tiles)
- Seed-based generation for reproducible maps
- Map generation preview with accept/regenerate options
- Procedural cover system with context-aware placement:
  - 3 cover levels (Light +2, Medium +4, Heavy +6 defense)
  - Automatic placement based on map type
  - Configurable cover density (0.0-0.5)
- Map generation presets system:
  - Save and load favorite configurations
  - Public/private preset sharing
  - Full CRUD operations

### Campaign Management
- Campaign creation and management
- Campaign status tracking (Planning, Active, On Hold, Completed, Archived)
- Player and character assignment to campaigns
- Campaign settings (starting karma/resources)
- Public and private campaign notes
- Campaign dashboard with full overview
- Session Management System:
  - Session creation and tracking within campaigns
  - Session scheduling (planned and actual dates)
  - Session status tracking (Planned, In Progress, Completed, Cancelled)
  - Session notes (GM private, public recap, player summary)
  - Rewards tracking (karma, nuyen)
  - Combat statistics (encounters, enemies defeated)
  - Event logging (objectives, NPCs, loot)
  - Character and map linking to sessions
  - Session objectives system with CRUD operations and completion tracking
  - Real-time AJAX updates for objective status
  - Visual progress bars

### Combat System
- Real-time combat tracker with round/turn tracking
- Participant tracking with initiative order
- HP and damage tracking (physical/stun for Shadowrun)
- Status effects and condition monitoring
- Combat effects system:
  - 5 effect types with visual color coding (buffs, debuffs, DoT, HoT, conditions)
  - Duration tracking with automatic countdown per round
  - One-click effect removal
  - Automatic effect expiration and logging
- Combat log and history tracking:
  - Comprehensive event logging for all combat actions
  - Automatic logging of combat start/end, rounds, turns
  - Damage and healing event tracking
  - Effect application and expiration tracking
  - Organized log view grouped by combat round
- Real-time AJAX updates for combat flow
- Automatic session statistics updates

### Dice Rolling System
- Pool-based D6 rolling with Shadowrun 5e mechanics
- Hit calculation (5s and 6s count as hits)
- Rule of Six (exploding 6s)
- Glitch and Critical Glitch detection
- Edge support and optional thresholds
- Dice preset management for quick rolls
- Roll history tracking
- Character-specific dice presets
- AJAX-based quick roller interface

### Sample Data
- Complete sample data command (`populate_sample_data`) includes:
  - 6 positive qualities and 6 negative qualities
  - 5 weapons, 3 armor items, 3 cyberware items
  - Electronics and miscellaneous gear
  - **All 81 Shadowrun skills** across 9 categories (combat, physical, social, technical, vehicle, magical, resonance, knowledge, language)
  - **60+ spells** across 5 categories (combat, detection, health, illusion, manipulation)
  - **25 adept powers** with power point costs
  - **15 complex forms** for technomancers

### Infrastructure
- Django 5.0.1 with Bootstrap 5 UI
- Admin interface for all models
- URL routing configured with namespaced patterns
- Static files serving
- Database support (SQLite for dev, MySQL for production)
- Comprehensive logging system

### Real-time Collaborative Map Editing
- WebSocket-based synchronization using Django Channels
- `maps/consumers.py`: MapConsumer handles tile/object/fog updates
- `maps/presence.py`: PresenceManager tracks connected users
- `maps/routing.py`: WebSocket URL routing (`ws/maps/<id>/`)
- `static/js/map_collaboration.js`: Frontend WebSocket client
- Features:
  - Multiple users can edit maps simultaneously
  - Live tile updates broadcast to all connected users
  - User presence tracking (see who's online)
  - Remote cursor display (see other users' positions)
  - Connection status indicator
  - Graceful fallback to AJAX when WebSocket unavailable
  - Shared users can now edit maps (owner + shared_with users)
- Run with Daphne for WebSocket support: `daphne shadowrun_campaign.asgi:application`
- Uses InMemoryChannelLayer for dev, Redis for production (`USE_REDIS=True`)

**Not yet implemented** (Planned Future Enhancements):
- Advanced pathfinding with terrain cost calculation
- Multi-layer map support (ground, objects, lighting layers)
- Map annotations and drawing tools (freehand, shapes, text)
- Import/export maps in common formats (JSON, image)
- Character portrait and token management
- Advanced search and filtering for characters/campaigns
- Automated combat AI for NPCs
