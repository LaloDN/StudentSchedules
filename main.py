from fastapi import FastAPI
from modules import students, careers, teachers

app = FastAPI(
    title = "Student Schedules",
    description = """
    This API allows you to query information about the available school
    asignatures and their associated teachers, also, if you're logged in you
    can get information about the student's schedules and add new asignatures or
    teachers into the database.
    """,
    version ="Alpha",
    contact={
        "name": "Eduardo Guadalupe Méndez Miranda",
        "email": "lalorayado1@live.com.mx"
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

app.include_router(students.router)
app.include_router(careers.router)
app.include_router(teachers.router)

@app.get("/")
async def root():
    return {"message": "Hello World, application is running! Visit /docs to see the documentation"}
