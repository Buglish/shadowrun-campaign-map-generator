# Shadowrun Campaign Manager & Map Generator

A full-stack Python application for managing Shadowrun characters and generating dynamic campaign maps for Game Masters and players.

## Project Objectives

This application aims to provide a comprehensive platform for Shadowrun campaigns by combining character management with dynamic map generation capabilities. The system enables players to create and maintain their characters while giving Game Masters powerful tools to build, share, and dynamically generate campaign maps.

## Features

### Player Features
- **User Authentication**: Secure login and registration system
- **Character Registration**: Create and register Shadowrun characters
- **Character Management**: View, edit, and manage character details including:
  - Attributes and skills
  - Equipment and gear
  - Cyberware and bioware
  - Character background and notes

### Game Master Features
- **Map Builder**: Interactive visual interface to create and edit custom campaign maps
  - Grid-based map editor with tile painting tools
  - Support for multiple terrain types (urban, wilderness, corporate, underground, mixed)
  - Place and manage map objects (NPCs, enemies, items, markers, etc.)
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
- **Campaign Management**: Organize and manage multiple campaigns (coming soon)

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
- MySQL (optional, for production)

### Setup Instructions

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

3. **Install dependencies**
```bash
venv/bin/pip install -r requirements.txt
```

4. **Configure environment variables** (optional)
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run database migrations**
```bash
venv/bin/python manage.py migrate
```

6. **Create a superuser** (for admin access)
```bash
venv/bin/python manage.py createsuperuser
```

7. **Run the development server**
```bash
venv/bin/python manage.py runserver
```

8. **Access the application**
- Main site: http://localhost:8000
- Admin panel: http://localhost:8000/admin

### MySQL Configuration (Optional)

By default, the project uses SQLite for development. To use MySQL:

1. Install MySQL client library:
```bash
apt install libmysqlclient-dev pkg-config
venv/bin/pip install mysqlclient==2.2.1
```

2. Update your `.env` file:
```
USE_MYSQL=True
DB_NAME=shadowrun_campaign
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

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
- **Advanced Procedural Generation**: Choose from 5 different algorithms
  - **BSP**: Room-and-corridor layouts perfect for dungeons and buildings
  - **Cellular Automata**: Organic cave systems with natural-looking structures
  - **Random Walk**: Winding tunnels and passages
  - **Maze**: Complex recursive mazes for puzzle-oriented maps
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

### Access URLs
- `/maps/` - List all accessible maps
- `/maps/create/` - Create a new blank map
- `/maps/generate/` - Generate a map procedurally (choose algorithm here)
- `/maps/<id>/` - View and edit map in builder interface
- `/maps/<id>/edit/` - Edit map settings
- `/maps/<id>/delete/` - Delete a map

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

### Planned
- [ ] Algorithm customization parameters (room sizes, corridor widths, iteration counts)
- [ ] Map generation preview before saving
- [ ] Real-time collaborative map editing
- [ ] AJAX-based tile editing (currently client-side only)
- [ ] Campaign session management
- [ ] Dice rolling integration
- [ ] Combat tracker
- [ ] NPC management with character links
- [ ] Enhanced character skills system
- [ ] Magic and spell management
- [ ] Map layers and fog of war
- [ ] Token/character placement on maps
- [ ] Grid measurement and distance tools

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

buglish@yahoo.com
