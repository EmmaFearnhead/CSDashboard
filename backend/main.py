import os

# Railway deployment configuration
PORT = int(os.environ.get("PORT", 8001))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=PORT)