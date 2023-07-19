from config.baseDatos import base
from sqlalchemy import Column, Integer, String, Float

class Ventas(base):
    __tablename__ ="ventas"
    id = Column(Integer,primary_key=True)
    fecha = Column(String)
    tienda = Column(String)
    importe = Column(Float)