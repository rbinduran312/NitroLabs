# NitroLabsAPI

Server Side API data for RPI sensors and data


## Installation

- Install PostgreSQL
    ```bash
    sudo apt update
    sudo apt install -y python-pip python3-dev libpq-dev postgresql postgresql-contrib
    sudo su - postgres
    psql

    ```
- Now, create a new database and user.

    ```postgresql
    CREATE DATABASE nitro_labs;
    CREATE USER <USER> WITH PASSWORD '<PASSWORD>';
    GRANT ALL PRIVILEGES ON DATABASE nitro_labs TO <USER>;
    ```
- Install python packages

    ```bash
    sudo apt install -y virtualenv
    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
- Migrate and create a superuser
    
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
    ```

## Working video
https://drive.google.com/file/d/1cgwRSEbA8kvf0d2SEfFDAscAzVV32occ/view?usp=sharing
