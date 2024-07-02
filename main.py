from fastapi import FastAPI
from web.gem_endpoints import gem_router
from web.user_endpoints import user_router
import uvicorn


app = FastAPI()

app.include_router(gem_router)
app.include_router(user_router)

# def create_db_and_tables():
#       SQLMdel.metadat.create_all(engine)
    

if __name__ == "__main__":
    uvicorn.run('main:app', host="localhost", port=8000, reload=True)
    # create_db_and_tables()


