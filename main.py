from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from typing import List, Optional
import csv
import io
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Models and custom modules
from models import (TransactionCreate, Transaction, SummaryResponse, 
                    AnalysisResponse, CategoryDetectionResponse)
import database
import nlp
import analysis
import charts

app = FastAPI(title="BudgetIQ API")

STATIC_DIR = os.path.join(BASE_DIR, 'static')
try:
    os.makedirs(os.path.join(STATIC_DIR, 'charts'), exist_ok=True)
except OSError:
    pass

@app.get("/static/charts/{file_name}")
def get_chart(file_name: str):
    chart_path = os.path.join(charts.CHARTS_DIR, file_name)
    if os.path.exists(chart_path):
        return FileResponse(chart_path)
    fallback_path = os.path.join(STATIC_DIR, 'charts', file_name)
    if os.path.exists(fallback_path):
        return FileResponse(fallback_path)
    raise HTTPException(status_code=404, detail="Chart not found")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.on_event("startup")
def startup_event():
    database.init_db()

# Serve frontend
@app.get("/")
def read_root():
    # If using SPA, return index.html
    return FileResponse(os.path.join(STATIC_DIR, 'index.html'))

# Transaction APIs
@app.post("/api/transactions", response_model=Transaction)
def add_transaction(transaction: TransactionCreate):
    new_txn = database.add_transaction(
        transaction.amount, 
        transaction.category, 
        transaction.description, 
        transaction.type, 
        transaction.date
    )
    return new_txn

@app.get("/api/transactions", response_model=List[Transaction])
def list_transactions(type: Optional[str] = None, category: Optional[str] = None):
    return database.get_transactions(type_filter=type, category_filter=category)

@app.delete("/api/transactions/{transaction_id}")
def delete_transaction(transaction_id: int):
    success = database.delete_transaction(transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"}

# Summary
@app.get("/api/summary", response_model=SummaryResponse)
def get_summary():
    txns = database.get_transactions()
    income = sum(t['amount'] for t in txns if t['type'] == 'income')
    expense = sum(t['amount'] for t in txns if t['type'] == 'expense')
    return {"income": income, "expense": expense, "balance": income - expense}

# AI Analysis
@app.get("/api/analysis", response_model=AnalysisResponse)
def get_analysis():
    txns = database.get_transactions()
    return analysis.run_analysis(txns)

# Charts Generation
@app.get("/api/charts/generate")
def generate_charts_api():
    txns = database.get_transactions()
    files = charts.generate_charts(txns)
    return {"message": "Charts generated successfully", "files": files}

# Category Detection
@app.get("/api/categories/detect", response_model=CategoryDetectionResponse)
def detect_category(description: str = Query("")):
    cat = nlp.detect_category(description)
    return {"category": cat}

# Export CSV
@app.get("/api/export/csv")
def export_csv():
    txns = database.get_transactions()
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "date", "type", "category", "amount", "description", "created_at"])
    writer.writeheader()
    for row in txns:
        writer.writerow(row)
        
    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=budgetiq_export.csv"
    return response

# Seeder
@app.post("/api/seed")
def seed_database():
    database.seed_data()
    return {"message": "Database seeded with 15 sample transactions over the last 3 months."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
