# Applied Database Project: Creating the Interface of the Data Management System

### Author

**Aldas Zarnauskas**

---

## Table of Contents

* [Project Overview](#project-overview)
* [The Main Folders and Files](#the-main-folders-and-files)
* [Data Source](#data-source)
* [Figures](#figures)
* [Requirements](#requirements)
* [License](#license)

---

## Project Overview

This project implements a command-line data management system for a **Conference Management** application. It provides an interactive interface that allows users to manage conference attendees, sessions, rooms, speakers, and attendee connections.

The system integrates two databases:
- **MySQL** (`appdbproj`) — stores relational data including attendees, sessions, rooms, companies, and registrations.
- **Neo4j** (`appdbprojneo4j`) — stores graph data representing connections between attendees.

The interface supports the following operations:
1. View Speakers & Sessions — search attendees by name and view their sessions and rooms.
2. View Attendees by Company — list all attendees belonging to a specific company.
3. Add New Attendee — insert a new attendee record into the MySQL database.
4. View Connected Attendees — retrieve attendees connected to a given attendee via Neo4j.
5. Add Attendee Connection — create a new connection between two attendees in Neo4j.
6. View Rooms — display all available conference rooms with their capacities.

---

## The Main Folders and Files

* **`main.py`** — Contains the Python script for the data management system.

---

## Data Source

* **`appdbproj.sql`** — MySQL relational database containing tables for attendees, sessions, rooms, companies, and registrations.
* **`appdbprojNeo4j.json`** — Neo4j graph database containing attendee nodes and `CONNECTED_TO` relationships between them.

---

## Figures

Conference Management
--------------------------
MENU
====
1 - View Speakers & Sessions
2 - View Attendees by Company
3 - Add New Attendee
4 - View Connected Attendees
5 - Add Attendee Connection
6 - View Rooms
x - Exit application

---

## Requirements

Before running the project locally, install the necessary dependencies:

```
pip install -r requirements.txt
```


Make sure to create a `.env` file in the project root with the following variables:

```
MYSQL_HOST=your_mysql_host
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=your_mysql_db
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=your_neo4j_user
NEO4J_PASSWORD=your_neo4j_password
```

---

## License

No license.
