from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class Jurisdiction(str, enum.Enum):
    UK = "uk"
    UAE = "uae"


class TaxDocument(Base):
    __tablename__ = "tax_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_type = Column(String, nullable=False)
    jurisdiction = Column(String, default="uk")
    file_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    extracted_text = Column(Text, nullable=True)
    ai_analysis = Column(JSON, nullable=True)
    processed = Column(Boolean, default=False)
    processing_error = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", backref="tax_documents")


class TaxCalculation(Base):
    __tablename__ = "tax_calculations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tax_year = Column(String, nullable=False)
    jurisdiction = Column(String, default="uk")
    employment_income = Column(Float, default=0.0)
    self_employment_income = Column(Float, default=0.0)
    dividend_income = Column(Float, default=0.0)
    savings_interest = Column(Float, default=0.0)
    property_income = Column(Float, default=0.0)
    total_income = Column(Float, default=0.0)
    tax_allowance = Column(Float, default=12570.0)
    taxable_income = Column(Float, default=0.0)
    tax_basic = Column(Float, default=0.0)
    tax_higher = Column(Float, default=0.0)
    tax_additional = Column(Float, default=0.0)
    income_tax = Column(Float, default=0.0)
    national_insurance = Column(Float, default=0.0)
    total_tax = Column(Float, default=0.0)
    effective_tax_rate = Column(Float, default=0.0)
    pension_contributions = Column(Float, default=0.0)
    tax_already_paid = Column(Float, default=0.0)
    calculation_method = Column(String, default="manual")
    confidence_score = Column(Float, nullable=True)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="tax_calculations")


class CAAdvice(Base):
    __tablename__ = "ca_advice"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tax_calculation_id = Column(Integer, ForeignKey("tax_calculations.id"), nullable=True)
    jurisdiction = Column(String, default="uk")
    total_current_tax = Column(Float, nullable=False)
    total_optimized_tax = Column(Float, nullable=True)
    potential_savings = Column(Float, nullable=True)
    reliefs = Column(JSON, default=list)
    full_analysis = Column(Text, nullable=True)
    action_items = Column(JSON, default=list)
    confidence = Column(Float, nullable=True)
    metadata = Column(JSON, default=dict)
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="ca_advices")
    calculation = relationship("TaxCalculation", backref="ca_advice")
