import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin, ModelView

from db import db
from db.models import Product, User, Routine
from web.provider import UsernameAndPasswordProvider

app = Starlette()

admin = Admin(db._engine,
              title="Example: SQLAlchemy",
              base_url='/',  # Adjust the base URL if needed
              auth_provider=UsernameAndPasswordProvider(),
              middlewares=[Middleware(SessionMiddleware, secret_key="qewrerthytju4")])


class ProductModelView(ModelView):
    exclude_fields_from_create = ["created_at", 'updated_at']
    exclude_fields_from_list = ["id"]


class UserModelView(ModelView):
    exclude_fields_from_create = ["created_at", "updated_at"]
    exclude_fields_from_list = ["id"]


class RoutineModelView(ModelView):
    exclude_fields_from_create = ["created_at", 'updated_at']
    exclude_fields_from_list = ["id"]


admin.add_view(RoutineModelView(Routine))
admin.add_view(UserModelView(User))
admin.add_view(ProductModelView(Product))

admin.mount_to(app)

if __name__ == "__main__":
    db.init()  # Ensure database is initialized
    uvicorn.run(app, host="localhost", port=8080)
