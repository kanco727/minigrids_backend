from sqlalchemy import Column, BigInteger, Text
from ..db import Base

class EquipementType(Base):
    __tablename__ = "equipement_type"
    id = Column(BigInteger, primary_key=True, index=True)
    type = Column(Text, unique=True, nullable=False)
    description = Column(Text, nullable=True)
