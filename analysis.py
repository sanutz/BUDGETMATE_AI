import pandas as pd
import numpy as np
from nlp import clean_and_tokenize, NLTK_READY
from collections import Counter
import os

def run_analysis(transactions):
    if not transactions:
        return {
            "financial_health": "Critical",
            "health_score": 0,
            "savings_rate": 0.0,
            "income_total": 0.0,
            "expense_total": 0.0,
            "balance": 0.0,
            "numpy_stats": {"mean": 0, "median": 0, "std_dev": 0, "max": 0, "min": 0, "count": 0},
            "category_breakdown": [],
            "monthly_trend": [],
            "top_keywords": [],
            "recommendations": ["No data available. Add transactions to see your analysis."],
            "charts_available": []
        }

    # Load data
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    df['year_month'] = df['date'].dt.to_period('M').astype(str)

    # Basic totals
    income_df = df[df['type'] == 'income']
    expense_df = df[df['type'] == 'expense']
    
    income_total = float(income_df['amount'].sum())
    expense_total = float(expense_df['amount'].sum())
    balance = income_total - expense_total
    
    # Savings Rate
    savings_rate = 0.0
    if income_total > 0:
        savings_rate = (balance / income_total) * 100
        savings_rate = round(float(savings_rate), 2)
        
    # Financial Health
    health_score = 0
    if income_total > 0:
        health_score = int(min(max((savings_rate / 30.0) * 100, 0), 100)) # 30% savings = 100 score
    elif expense_total == 0:
        health_score = 100
    
    if health_score >= 80:
        financial_health = "Excellent"
    elif health_score >= 50:
        financial_health = "Good"
    elif health_score >= 20:
        financial_health = "Fair"
    else:
        financial_health = "Critical"

    # NumPy stats on expenses
    if not expense_df.empty:
        exp_amounts = expense_df['amount'].to_numpy()
        numpy_stats = {
            "mean": round(float(np.mean(exp_amounts)), 2),
            "median": round(float(np.median(exp_amounts)), 2),
            "std_dev": round(float(np.std(exp_amounts)), 2),
            "max": round(float(np.max(exp_amounts)), 2),
            "min": round(float(np.min(exp_amounts)), 2),
            "count": int(len(exp_amounts))
        }
    else:
        numpy_stats = {"mean": 0.0, "median": 0.0, "std_dev": 0.0, "max": 0.0, "min": 0.0, "count": 0}

    # Category Breakdown for Expenses
    category_breakdown = []
    if not expense_df.empty:
        cat_group = expense_df.groupby('category').agg({'amount': ['sum', 'count', 'mean']})
        cat_group.columns = ['total', 'count', 'avg']
        cat_group = cat_group.reset_index().sort_values(by='total', ascending=False)
        
        for _, row in cat_group.iterrows():
            percentage = (row['total'] / expense_total) * 100
            category_breakdown.append({
                "category": row['category'],
                "total": round(float(row['total']), 2),
                "count": int(row['count']),
                "avg": round(float(row['avg']), 2),
                "percentage": round(float(percentage), 2)
            })

    # Monthly Trend
    monthly_trend = []
    month_group = df.groupby(['year_month', 'type'])['amount'].sum().unstack(fill_value=0).reset_index()
    if 'income' not in month_group.columns:
        month_group['income'] = 0.0
    if 'expense' not in month_group.columns:
        month_group['expense'] = 0.0
        
    for _, row in month_group.iterrows():
        m_inc = float(row['income'])
        m_exp = float(row['expense'])
        monthly_trend.append({
            "month": row['year_month'],
            "income": m_inc,
            "expense": m_exp,
            "savings": m_inc - m_exp
        })

    # Keywords (NLP)
    all_descriptions = " ".join([d for d in df['description'].dropna().tolist() if d])
    tokens = clean_and_tokenize(all_descriptions)
    
    # Simple stopword removal if NLTK is ready
    if NLTK_READY:
        from nltk.corpus import stopwords
        stop_words = set(stopwords.words('english'))
        tokens = [t for t in tokens if t not in stop_words and len(t) > 2]
    else:
        fallback_stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'for', 'at', 'in', 'on', 'to', 'with'}
        tokens = [t for t in tokens if t not in fallback_stopwords and len(t) > 2]

    word_counts = Counter(tokens)
    top_keywords = [{"word": word, "count": count} for word, count in word_counts.most_common(10)]

    # Recommendations
    recommendations = []
    if savings_rate >= 20:
        recommendations.append("Great job! Your savings rate is above 20%. Consider increasing your investment portfolio.")
    elif savings_rate > 0:
        recommendations.append("You are saving, but try to cut discretionary spending to reach a 20% savings target.")
    else:
        recommendations.append("ALERT: You are spending more than you earn. Review your highest expense categories immediately.")
        
    if category_breakdown and category_breakdown[0]['percentage'] > 40:
        top_cat = category_breakdown[0]['category']
        recommendations.append(f"Your top expense is '{top_cat}', making up {category_breakdown[0]['percentage']}% of your spending. Try setting a strict budget here.")

    # Charts available check
    import glob
    chart_files = [os.path.basename(p) for p in glob.glob("static/charts/*.png")]

    return {
        "financial_health": financial_health,
        "health_score": health_score,
        "savings_rate": savings_rate,
        "income_total": income_total,
        "expense_total": expense_total,
        "balance": balance,
        "numpy_stats": numpy_stats,
        "category_breakdown": category_breakdown,
        "monthly_trend": monthly_trend,
        "top_keywords": top_keywords,
        "recommendations": recommendations,
        "charts_available": chart_files
    }
