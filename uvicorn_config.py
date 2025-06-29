import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Desactivar reload en producción
        workers=1,     # Número de workers
        log_level="info",
        access_log=True
    ) 