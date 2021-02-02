import random


class AuthRouter(object):
    """
    A router to control all database operations on models in the
    auth and contenttypes applications.
    """
    route_app_labels = {'communication'}

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label == 'communication':
            return 'keys_communcation'
        if model._meta.app_label == 'temp_oracle':
            return 'oracle'
        if model._meta.app_label == 'inspection':
            return 'inspection'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label == 'communication':
            return 'keys_communcation'
        if model._meta.app_label == 'temp_oracle':
            return 'oracle'
        if model._meta.app_label == 'inspection':
            return 'inspection'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth or contenttypes apps is
        involved.
        """
        if (
                obj1._meta.app_label == 'communication' or
                obj2._meta.app_label == 'communication'
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth and contenttypes apps only appear in the
        'auth_db' database.
        """
        if app_label == 'communication':
            return True
        return None


class PrimaryReplicaRouter:
    def db_for_read(self, model, **hints):
        """
        Reads go to a randomly-chosen replica.
        """
        return random.choice(['default', 'replica'])

    def db_for_write(self, model, **hints):
        """
        Writes always go to primary.
        """
        if model._meta.app_label == 'communication':
            return 'keys_communcation'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed if both objects are
        in the primary/replica pool.
        """
        db_list = ('default', 'replica')
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        All non-auth models end up in this pool.
        """
        return True
