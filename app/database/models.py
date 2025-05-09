from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database.session import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    report_id = Column(String(255), unique=True, nullable=False)
    org_name = Column(String(255))
    email = Column(String(255))
    date_begin = Column(TIMESTAMP, nullable=False)
    date_end = Column(TIMESTAMP, nullable=False)
    domain = Column(String(255), nullable=False)
    adkim = Column(String(1))
    aspf = Column(String(1))
    policy = Column(String(50))
    subdomain_policy = Column(String(50))
    pct = Column(Integer)

    records = relationship("Record", back_populates="report", cascade="all, delete-orphan")

class Record(Base):
    __tablename__ = "records"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    report_id = Column(BigInteger, ForeignKey('reports.id', ondelete="CASCADE"), nullable=False)
    source_ip = Column(String(45), nullable=False)
    count = Column(Integer, nullable=False)
    disposition = Column(String(50))
    dkim_result = Column(String(50))
    spf_result = Column(String(50))
    header_from = Column(String(255))

    report = relationship("Report", back_populates="records")
    auth_results = relationship("AuthResult", back_populates="record", cascade="all, delete-orphan")

class AuthResult(Base):
    __tablename__ = "auth_results"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    record_id = Column(BigInteger, ForeignKey('records.id', ondelete="CASCADE"), nullable=False)
    auth_type = Column(String(10), nullable=False) # 'dkim' or 'spf'
    domain = Column(String(255), nullable=False)
    result = Column(String(50))

    record = relationship("Record", back_populates="auth_results")
