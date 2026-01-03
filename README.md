# Notes App – Flask & MariaDB on AWS EC2
## Project Overview
This project is a web-based Notes Management Application developed using Python (Flask) and MariaDB, and deployed on an AWS EC2 instance. The application allows users to register, log in, create notes, view their own notes, and log out securely. Each user can only access their own notes. The database is backed up automatically to an attached volume.

## Features
- User registration and authentication
- Secure password hashing
- User-specific notes (data isolation)
- MariaDB backend
- Automated daily database backup
- Deployed on AWS EC2
- Persistent storage using mounted volume
## Technology Stack
### Component	Technology
- Backend	Python 3, Flask
- Database	MariaDB
- OS	Red Hat Linux (EC2)
- Cloud Provider	AWS
- Backup	mysqldump + cron
- Version Control	Git & GitHub
## Application Architecture

User → Browser → Flask App → MariaDB → Backup Volume (/backup)

## Directory Structure
Notes_App/

- app.py

- requirements.txt

- .gitignore

## Database Schema
### users table
CREATE TABLE users (

id INT AUTO_INCREMENT PRIMARY KEY,

username VARCHAR(100) UNIQUE NOT NULL,

password_hash VARCHAR(255) NOT NULL
);

### notes table
CREATE TABLE notes (

  id INT AUTO_INCREMENT PRIMARY KEY,  
  
  user_id INT NOT NULL,        
  
  content TEXT NOT NULL,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (user_id) REFERENCES users(id)
);

## Setup Instructions
1. Launch EC2 Instance
   
  OS: Red Hat Linux

  Open ports:

    -- 22 (SSH)

    -- 80 (HTTP)

2. Add additional disk for Backup
   
3. Connect to EC2 Instance

4. Create Directory under Home


   mkdir -p /home/Application/Notes_App


6. change directory to Notes_App


     cd /home/Application/Notes_App


7. Install Dependencies
   
    sudo dnf install -y python3 python3-pip mariadb mariadb-server git

    pip3 install -r requirements.txt

7. Configure MariaDB

   sudo systemctl start mariadb

   sudo mysql_secure_installation

#### Create database and user:

    CREATE DATABASE notesdb;

    CREATE USER 'notesuser'@'localhost' IDENTIFIED BY 'StrongPassword123';

    GRANT ALL PRIVILEGES ON notesdb.* TO 'notesuser'@'localhost';

    FLUSH PRIVILEGES;

8. Navigate to Notes_App directory and Create app.py file
   
    touch app.py 

9. Paste the python Code in app.py file and save it

10. Run the Application
  
     python3 app.py

11.Access the app via browser:

  http://<EC2_PUBLIC_IP>/

12.Create and Mount Backup EBS Volume

  lsblk

  sudo mkfs.xfs /dev/nvme1n1

  sudo mkdir /backup

  sudo mount /dev/nvme1n1 /backup

#### Persist mount:

  sudo blkid /dev/xvdf

#### Edit fstab:

  sudo vim /etc/fstab

 #### Add:

  UUID= /backup xfs defaults 0 0

13. Backup MariaDB to /backup
    
### Create Backup Script

  sudo mkdir /backup/mariadb

  sudo vim /usr/local/bin/db_backup.sh

  #!/bin/bash

  DATE=$(date +%F_%H-%M)

  mysqldump -u root -p'RootPassword' notesdb > /backup/db-backups/notesdb_$DATE.sql

  sudo chmod +x /usr/local/bin/db_backup.sh

14. Automate Backup (Cron Job)
    
  sudo crontab -e
  
  Daily backup at 2 AM:
  
  0 2 * * * /usr/local/bin/db_backup.sh
