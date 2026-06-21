# SDE Prep Roadmap 90 Days

A comprehensive, gamified 90-day learning and tracking platform built to help students prepare for Software Development Engineer (SDE) interviews. 

## Features

- **90-Day Progress Tracker**: Daily modules with topic names, video resources, notes, and question lists. Track your completion with an interactive grid.
- **Streak & Freeze System**: Gamified streak counting. Keep your streak alive by completing days consecutively. Use earned "Freezes" to protect your streak on days off.
- **Dynamic Leaderboard**: See where you rank among all registered students based on XP points earned through daily completions. Features a visually stunning Top 3 podium!
- **Interactive Calendar/Timeline**: An intelligent timeline to keep track of meetings, holidays, and deadlines, featuring color-coded smart event chips.
- **Community Chat Board**: A real-time discussion feed allowing students to chat, upload images, and interact. Also features quick access to an external WhatsApp Community.
- **Customizable Profiles**: Personalize your account by uploading a custom Profile Photo and Cover Banner. 
- **Founder Dashboard**: A dedicated admin panel for the founder to track overall student progress, freeze usage, and manage the curriculum calendar.

## Tech Stack
- **Backend**: Python, Django
- **Frontend**: HTML5, Vanilla JS, Tailwind CSS (via CDN for immediate responsive styling)
- **Database**: SQLite (Development)

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/atul-techx/SDE-Prep-Roadmap-90-Days.git
   cd SDE-Prep-Roadmap-90-Days
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install django Pillow
   ```

4. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Start the Development Server**
   ```bash
   python manage.py runserver
   ```
   Navigate to `http://127.0.0.1:8000/` in your browser.

## Built By atul-techx
Designed to help software engineers level up!
