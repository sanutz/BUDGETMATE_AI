from pydantic import BaseModel, Field
from typing import List, Optional

class TransactionCreate(BaseModel):
    amount: float
    category: str
    description: Optional[str] = ""
    type: str = Field(pattern="^(income|expense)$")
    date: str

class Transaction(BaseModel):
    id: int
    amount: float
    category: str
    description: Optional[str]
    type: str
    date: str
    created_at: str

class SummaryResponse(BaseModel):
    income: float
    expense: float
    balance: float

class NumpyStats(BaseModel):
    mean: float
    median: float
    std_dev: float
    max: float
    min: float
    count: int

class CategoryBreakdown(BaseModel):
    category: str
    total: float
    count: int
    avg: float
    percentage: float

class MonthlyTrend(BaseModel):
    month: str
    income: float
    expense: float
    savings: float

class KeywordCount(BaseModel):
    word: str
    count: int

class AnalysisResponse(BaseModel):
    financial_health: str
    health_score: int
    savings_rate: float
    income_total: float
    expense_total: float
    balance: float
    numpy_stats: NumpyStats
    category_breakdown: List[CategoryBreakdown]
    monthly_trend: List[MonthlyTrend]
    top_keywords: List[KeywordCount]
    recommendations: List[str]
    charts_available: List[str]

class CategoryDetectionResponse(BaseModel):
    category: str
