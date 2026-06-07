from fastapi import FastAPI, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, text
import hashlib
import json
import gzip

app = FastAPI(
    title="API IBGE - Dataset Municipal",
    description="API REST otimizada para consulta de 4 milhões de registros",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "postgresql://postgres:123456@localhost:5432/ibge"
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)

@app.get("/app")
def frontend():
    return FileResponse("index.html")

@app.get("/")
def root():
    return {"status": "ok", "message": "API IBGE rodando!"}

@app.get("/municipios")
def listar_municipios(
    request: Request,
    limit: int = Query(default=100, le=1000, description="Itens por página"),
    cursor: int = Query(default=0, description="ID do último item recebido"),
    estado: str = Query(default=None, description="Filtrar por estado ex: SP"),
    regiao: str = Query(default=None, description="Filtrar por região ex: Sudeste"),
    fields: str = Query(default=None, description="Campos a retornar ex: nome,estado,populacao")
):
    filters = "WHERE id > :cursor"
    params = {"cursor": cursor, "limit": limit}

    if estado:
        filters += " AND estado = :estado"
        params["estado"] = estado.upper()

    if regiao:
        filters += " AND regiao = :regiao"
        params["regiao"] = regiao

    query = f"SELECT * FROM municipios {filters} ORDER BY id LIMIT :limit"

    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        rows = [dict(r._mapping) for r in result]

    if not rows:
        return {"data": [], "next_cursor": None, "count": 0}

    # Filtra campos se o parâmetro ?fields= foi enviado
    CAMPOS_VALIDOS = {"id", "nome", "estado", "populacao", "area_km2", "pib_per_capita", "regiao", "codigo_ibge"}
    if fields:
        campos = {c.strip() for c in fields.split(",") if c.strip() in CAMPOS_VALIDOS}
        if campos:
            rows = [{k: v for k, v in row.items() if k in campos} for row in rows]

    payload = {"data": rows, "next_cursor": rows[-1]["id"] if "id" in rows[-1] else None, "count": len(rows)}
    content = json.dumps(payload, default=str).encode("utf-8")

    # Gera ETag
    etag = f'"{hashlib.md5(content).hexdigest()}"'

    # Verifica 304
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304)

    # Comprime manualmente com Gzip
    accepts_gzip = "gzip" in request.headers.get("accept-encoding", "")
    if accepts_gzip:
        compressed = gzip.compress(content)
        return Response(
            content=compressed,
            media_type="application/json",
            headers={
                "ETag": etag,
                "Cache-Control": "public, max-age=60",
                "Content-Encoding": "gzip",
            }
        )

    return Response(
        content=content,
        media_type="application/json",
        headers={
            "ETag": etag,
            "Cache-Control": "public, max-age=60",
        }
    )

@app.get("/municipios/{id}")
def buscar_municipio(id: int, request: Request):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM municipios WHERE id = :id"),
            {"id": id}
        )
        row = result.fetchone()

    if not row:
        return Response(status_code=404)

    data = dict(row._mapping)
    content = json.dumps(data, default=str).encode("utf-8")
    etag = f'"{hashlib.md5(content).hexdigest()}"'

    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304)

    accepts_gzip = "gzip" in request.headers.get("accept-encoding", "")
    if accepts_gzip:
        compressed = gzip.compress(content)
        return Response(
            content=compressed,
            media_type="application/json",
            headers={
                "ETag": etag,
                "Cache-Control": "public, max-age=300",
                "Content-Encoding": "gzip",
            }
        )

    return Response(
        content=content,
        media_type="application/json",
        headers={
            "ETag": etag,
            "Cache-Control": "public, max-age=300",
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)