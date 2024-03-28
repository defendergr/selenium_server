import uvicorn

if __name__ == "__main__":
    uvicorn.run('Api.main:app', host="0.0.0.0", port=8030, reload=False)
