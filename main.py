from fastapi import FastAPI

app = FastAPI(title="Natrium", openapi_prefix="/openapi/")

@app.get("/natrium/hello_world")
async def helloworld():
    return {
        "message": "hello world."
    }