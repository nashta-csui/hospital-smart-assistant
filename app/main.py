from fastapi import FastAPI

app = FastAPI()
@app.get("/")
async def root():
    msg = "Hello World"
    return {"message": "Hello World"}
