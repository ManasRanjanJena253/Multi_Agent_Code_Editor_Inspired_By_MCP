import uvicorn
from fastapi.staticfiles import StaticFiles
from api import app

# Mount the static directory to serve the HTML, CSS, and JS
app.mount("/Frontend", StaticFiles(directory="/Frontend"), name="Frontend")

# Add a route to serve the index.html file
from fastapi.responses import FileResponse

@app.get("/")
async def read_index():
    return FileResponse("Frontend/index.html")

if __name__ == "__main__":
    uvicorn.run("run:app", host="127.0.0.1", port=8000, reload=True)