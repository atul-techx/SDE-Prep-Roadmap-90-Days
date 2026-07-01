import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dsa_platform.settings")
django.setup()

def sync_missing_tables():
    with connection.cursor() as cursor:
        tables = connection.introspection.table_names(cursor)
        
    from django.apps import apps
    
    with connection.schema_editor() as schema_editor:
        for model in apps.get_app_config('roadmap').get_models():
            if model._meta.db_table not in tables:
                print(f"Creating missing table for {model.__name__}...")
                schema_editor.create_model(model)
                
if __name__ == '__main__':
    sync_missing_tables()
    print("Database sync complete.")
