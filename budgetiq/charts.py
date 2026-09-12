import matplotlib
matplotlib.use('Agg') # Non-interactive backend, important for threads/servers
import matplotlib.pyplot as plt
import pandas as pd
import os
import tempfile

CHARTS_DIR = os.path.join(
    tempfile.gettempdir() if os.environ.get('VERCEL') else os.path.dirname(os.path.abspath(__file__)),
    'budgetiq-charts' if os.environ.get('VERCEL') else os.path.join('static', 'charts')
)

# Use a vibrant, dark-theme compatible color palette
COLORS = ['#00d4aa', '#ff4d4d', '#ffb84d', '#4d94ff', '#bf4dff', '#4dffc3']
BG_COLOR = '#0f172a' # Tailwind slate-900
TEXT_COLOR = '#f8fafc'

def ensure_dir():
    if not os.path.exists(CHARTS_DIR):
        os.makedirs(CHARTS_DIR)

def setup_plot_style():
    plt.rcParams.update({
        'axes.facecolor': BG_COLOR,
        'figure.facecolor': BG_COLOR,
        'text.color': TEXT_COLOR,
        'axes.labelcolor': TEXT_COLOR,
        'xtick.color': TEXT_COLOR,
        'ytick.color': TEXT_COLOR,
        'axes.edgecolor': '#334155', # slate-700
        'grid.color': '#334155'
    })

def generate_charts(transactions):
    ensure_dir()
    if not transactions:
        return []
        
    setup_plot_style()
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    expense_df = df[df['type'] == 'expense']
    
    generated_files = []

    # 1. Category Pie Chart (Expenses)
    if not expense_df.empty:
        cat_sums = expense_df.groupby('category')['amount'].sum()
        
        plt.figure(figsize=(6, 6))
        plt.pie(cat_sums, labels=cat_sums.index, autopct='%1.1f%%', startangle=140, 
                colors=COLORS, textprops={'color': TEXT_COLOR}, wedgeprops={'edgecolor': BG_COLOR})
        plt.title('Expenses by Category', color=TEXT_COLOR)
        
        filepath = os.path.join(CHARTS_DIR, 'category_pie.png')
        plt.savefig(filepath, bbox_inches='tight', dpi=150)
        plt.close()
        generated_files.append('category_pie.png')

    # 2. Monthly Bar Chart (Income vs Expense)
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    monthly = df.groupby(['year_month', 'type'])['amount'].sum().unstack(fill_value=0)
    
    if not monthly.empty:
        if 'income' not in monthly.columns: monthly['income'] = 0
        if 'expense' not in monthly.columns: monthly['expense'] = 0
            
        fig, ax = plt.subplots(figsize=(8, 5))
        monthly[['income', 'expense']].plot(kind='bar', ax=ax, color=['#00d4aa', '#ff4d4d'])
        plt.title('Monthly Income vs Expense')
        plt.xlabel('Month')
        plt.ylabel('Amount')
        plt.xticks(rotation=45)
        plt.legend(facecolor=BG_COLOR, edgecolor='#334155', labelcolor=TEXT_COLOR)
        plt.grid(axis='y', alpha=0.3)
        
        filepath = os.path.join(CHARTS_DIR, 'monthly_bar.png')
        plt.savefig(filepath, bbox_inches='tight', dpi=150)
        plt.close()
        generated_files.append('monthly_bar.png')

    # 3. Transaction Scatter Plot (Amount over Time)
    plt.figure(figsize=(8, 4))
    if not df.empty:
        # separate colors
        inc_data = df[df['type'] == 'income']
        exp_data = df[df['type'] == 'expense']
        
        plt.scatter(inc_data['date'], inc_data['amount'], color='#00d4aa', alpha=0.7, label='Income')
        plt.scatter(exp_data['date'], exp_data['amount'], color='#ff4d4d', alpha=0.7, label='Expense')
        plt.title('Transactions Over Time')
        plt.xlabel('Date')
        plt.ylabel('Amount')
        plt.xticks(rotation=45)
        plt.legend(facecolor=BG_COLOR, edgecolor='#334155', labelcolor=TEXT_COLOR)
        plt.grid(alpha=0.3)
        
        filepath = os.path.join(CHARTS_DIR, 'scatter_plot.png')
        plt.savefig(filepath, bbox_inches='tight', dpi=150)
        plt.close()
        generated_files.append('scatter_plot.png')

    # 4. Expense Histogram (Frequency of expense amounts)
    if not expense_df.empty:
        plt.figure(figsize=(8, 4))
        plt.hist(expense_df['amount'], bins=15, color='#ffb84d', edgecolor=BG_COLOR, alpha=0.8)
        plt.title('Distribution of Expense Amounts')
        plt.xlabel('Amount')
        plt.ylabel('Frequency')
        plt.grid(axis='y', alpha=0.3)
        
        filepath = os.path.join(CHARTS_DIR, 'expense_histogram.png')
        plt.savefig(filepath, bbox_inches='tight', dpi=150)
        plt.close()
        generated_files.append('expense_histogram.png')

    return generated_files
