from flask_migrate import MigrateCommand, Migrate
from flask_script import Manager
from info import create_app, db


# Create different configuration app instances by factory mode
app = create_app('develop')
# Integrated flask_script,Initializes a manager object and associated with
# the app
manager = Manager(app)

Migrate(app, db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    # app.run()
    manager.run()
