from fastapi import FastAPI, Body, Path, Query, Request, HTTPException, Depends
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.encoders import jsonable_encoder
from starlette.requests import Request
import uvicorn 
from pydantic import BaseModel, Field
from typing import Optional, List
from jwt_config import *
from config.baseDatos import *
from modelos.Ventas import Ventas as VentasModel

app = FastAPI()
app.title = "aplicacion de ventas"
app.version = "1.0"

base.metadata.create_all(bind=motor)

class Usuario(BaseModel):
    email:str
    clave:str

ventas = [
    {"id":1,
     "fecha":"01/01/23",
     "tienda":"Tienda01",
     "importa":2500
     },
     {"id":2,
     "fecha":"01/01/23",
     "tienda":"Tienda02",
     "importa":2500
     }
]

class Ventas(BaseModel):
    id:int = Field(ge=0, le=20)
    #id:Optional[int]=None
    fecha:str
    tienda:str = Field(default="Tienda01", min_length=4, max_length=10)
    #tienda:str
    importe:float
    class Config:
        shema_extra = {
            "example":[{
                "id":0,
                "fecha":"01-02-2023",
                "tienda":"Tienda01",
                "importe":1235.50
            }]
        }


class Portador(HTTPBearer):
    async def __call__(self, request: Request):
        autorizacion = await super().__call__(request)
        dato = validar_token(autorizacion.credentials)
        if dato["email"] != "jose":
            raise HTTPException(status_code=403, detail="no autorizado")
        


@app.get("/", tags=["inicio"])
def mensaje():
    return "Hola, bienvenido"

@app.get("/ventas", tags=["Ventas"], response_model=List[Ventas], status_code=200,dependencies=[Depends(Portador())])
def dame_ventas()->List[Ventas]:
    db = sesion()
    resultado = db.query(VentasModel).all()
    return JSONResponse(content=jsonable_encoder(resultado), status_code=200)

@app.get("/ventas/{id}", tags=["Ventas"], response_model=List[Ventas])
def dame_ventas(id:int = Path(ge=1,le=1000)) ->List[Ventas]:
    db = sesion()
    resultado = db.query(VentasModel).filter(VentasModel.id == id).first()
    print(resultado)
    if not resultado:
        return JSONResponse(content={"mensaje":"no encontrado"}, status_code=404)
    return JSONResponse(content=jsonable_encoder(resultado), status_code=200) 
@app.get("/ventas/", tags=["Ventas"],response_model=List[Ventas])
def dame_ventas_por_tiendas(tienda:str = Query(min_length=4, max_length=20)) -> List[Ventas]:
    db = sesion()
    resultado = db.query(VentasModel).filter(VentasModel.tienda == tienda).first()
    if not resultado:
        return JSONResponse(content={"mensaje":"no encontrado"}, status_code=404)
    return JSONResponse(content=jsonable_encoder(resultado), status_code=200)

@app.post("/ventas", tags=["Ventas"])
def crear_ventas(venta:Ventas):
    db = sesion()
    nueva_venta = VentasModel(**venta.model_dump())
    db.add(nueva_venta)
    db.commit()
    return JSONResponse(content={"response":"creado"},status_code=201)
@app.put("/ventas/{id}", tags=["Ventas"])
def actualizar_ventas(venta:Ventas):
    db = sesion()
    resultado = db.query(VentasModel).filter(VentasModel.id == venta.id).first()
    if not resultado:
        return JSONResponse(content={"mensaje":"no encontrado"}, status_code=404)
    resultado.fecha = venta.fecha
    resultado.tienda = venta.tienda
    resultado.importe = venta.importe
    db.commit()
    return JSONResponse(content={"response":"actualizado"},status_code=202)

@app.delete("/ventas/{id}",tags=["Ventas"])
def borrar_venta(id:int):
    db = sesion()
    resultado = db.query(VentasModel).filter(VentasModel.id == id).first()
    if not resultado:
        return JSONResponse(content={"mensaje":"no encontrado"}, status_code=404)
    db.delete(resultado)
    db.commit()
    return JSONResponse(content={"response":"eliminado"},status_code=204)

@app.post("/loging",tags=["Autenticacion"])
def login(usuario:Usuario):
    if usuario.email == "jose" and usuario.clave == "1235":
        token:str = dame_token(usuario.dict())
        return JSONResponse(content=token)
    return JSONResponse(content="Acceso denegado")
