from natrium import app, cache_pool

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, port=8000)
    finally:
        cache_pool.close_scavenger()
