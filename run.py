"""
Script de lancement du serveur web PriceWatch.

Usage :
    python run.py

L'application sera accessible sur :
- Interface utilisateur : http://localhost:8000/
- Documentation Swagger : http://localhost:8000/docs
- Documentation ReDoc   : http://localhost:8000/redoc
"""

import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("Demarrage du serveur PriceWatch (L3 MIAGE Toulouse)...")
    print("Interface Web : http://localhost:8000/")
    print("API Swagger   : http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
