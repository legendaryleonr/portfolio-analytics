from fastapi import FastAPI

app = FastAPI(title="Portfolio Analytics API")


@app.get("/health")
def health_check():
    return {"status": "ok"}
