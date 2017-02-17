# Sunny CRM
A multi-user web-based CRM for freelancers with an emphasis on flow and momentum. Concentrate on contacting—and staying on contact with—clients and potential clients rather than categorizing and sorting your address book. Maintaining a viable stable of clients is a matter of consistently following up on inquiries and conversations. Sunny CRM makes it easy to add the latest update about a client and quickly schedule a follow-up with a concrete task. Based on years of freelance experience.

Sunny CRM is built with Python 3, Flask, and Bootstrap.

## Setup
1. `cd path/to/sunny-crm`
2. Optional: set up a virtual environment using virtualenv.
3. Install the required packages: `pip install -r requirements.txt`
4. Pick a config file. A `default.cfg` file is included. If you want to enable email for password recovery, etc, you can either edit `default.cfg` or create a new file with the same format. Then do `export FLASK_CONFIG_FILE=path/to/config/file`. If you want to use the default settings, do `export FLASK_CONFIG_FILE=../default.cfg`.
5. Initialize the database: `python manage.py init_db`
6. Start the app: `python manage.py runserver` (debug mode will be enabled). If you want to disable debugging, do `python manage.py runserver --no-debug` instead.
7. Open a browser and navigate to `http://localhost:5000/`