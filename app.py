import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import requests
import dash
import json
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
SITE_URL = os.getenv('SITE_URL', 'http://localhost:8053')
SITE_NAME = os.getenv('SITE_NAME', 'NYT Bestsellers Analytics')

def get_book_summary(title, author):
    try:
        print(f"Requesting summary for {title} by {author}")
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": SITE_URL,
                "X-Title": SITE_NAME,
            },
            data=json.dumps({
                "model": "deepseek/deepseek-r1-distill-llama-70b:free",
                "messages": [
                    {
                        "role": "user",
                        "content": f"Please provide a brief summary of the book '{title}' by {author}. Keep it concise and informative."
                    }
                ],
            })
        )
        result = response.json()
        print(f"API Response: {result}")  
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error in get_book_summary: {str(e)}")
        return f"Error getting summary: {str(e)}"

app = Dash(__name__, 
           external_stylesheets=[
               dbc.themes.FLATLY,
               "https://use.fontawesome.com/releases/v6.4.2/css/all.css"
           ],
           meta_tags=[{'name': 'viewport',
                      'content': 'width=device-width, initial-scale=1.0'}])

df = pd.read_csv('data.csv')

unique_dates = sorted(df['published_date'].unique(), reverse=True)

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("NYT Bestsellers Analytics", 
                   className="dashboard-title"),
            html.P("Analysis of bestselling books and publishers", 
                   className="dashboard-subtitle")
        ], width=12, className="text-center mb-4")
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-building stats-icon")
                    ], className="stats-icon-container"),
                    html.Div([
                        html.H3("Publishers", className="stats-title"),
                        html.H2(len(df['publisher'].unique()), className="stats-value"),
                        html.P("Total Active Publishers", className="stats-subtitle")
                    ])
                ], className="stats-content")
            ], className="stats-card")
        ], width=12, lg=4),
        dbc.Col([
            dbc.Card([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-book stats-icon")
                    ], className="stats-icon-container"),
                    html.Div([
                        html.H3("Books", className="stats-title"),
                        html.H2(len(df['title'].unique()), className="stats-value"),
                        html.P("Total Books Listed", className="stats-subtitle")
                    ])
                ], className="stats-content")
            ], className="stats-card")
        ], width=12, lg=4),
        dbc.Col([
            dbc.Card([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-pen-fancy stats-icon")
                    ], className="stats-icon-container"),
                    html.Div([
                        html.H3("Authors", className="stats-title"),
                        html.H2(len(df['author'].unique()), className="stats-value"),
                        html.P("Featured Authors", className="stats-subtitle")
                    ])
                ], className="stats-content")
            ], className="stats-card")
        ], width=12, lg=4),
    ], className="mb-4"),

    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="fas fa-trophy me-2"),
                        "Top Publishers"
                    ], className="section-title")
                ]),
                dbc.CardBody(
                    html.Div(id='top-publishers-container')
                )
            ], className="content-card h-100")
        ], width=12, lg=4),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.Div([
                        html.H4([
                            html.I(className="fas fa-calendar me-2"),
                            "Bestsellers by Date"
                        ], className="section-title"),
                        dcc.Dropdown(
                            id='date-dropdown',
                            options=[{'label': date, 'value': date} for date in unique_dates],
                            placeholder="Select date...",
                            className="date-dropdown"
                        )
                    ], className="d-flex justify-content-between align-items-center")
                ]),
                dbc.CardBody(
                    dash_table.DataTable(
                        id='books-table',
                        style_table={'overflowX': 'auto'},
                        style_cell={
                            'textAlign': 'left',
                            'padding': '16px',
                            'fontSize': '14px',
                            'fontFamily': '"Inter", sans-serif'
                        },
                        style_header={
                            'backgroundColor': '#f8f9fa',
                            'fontWeight': 'bold',
                            'border': 'none',
                            'fontSize': '14px'
                        },
                        style_data={
                            'border': 'none',
                            'borderBottom': '1px solid #f0f0f0'
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': '#f8f9fa'
                            },
                            {
                                'if': {'column_id': 'get_summary'},
                                'cursor': 'pointer',
                                'color': '#007bff',
                                'textDecoration': 'underline'
                            }
                        ],
                        page_size=8,
                        css=[{
                            'selector': '.dash-cell div.dash-cell-value',
                            'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                        }]
                    )
                )
            ], className="content-card h-100 mb-4")
        ], width=12, lg=8),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="fas fa-chart-bar me-2"),
                        "Publisher Performance Trends"
                    ], className="section-title"),
                    dcc.Dropdown(
                        id='publisher-trend-dropdown',
                        options=[
                            {'label': publisher, 'value': publisher}
                            for publisher in sorted(df['publisher'].unique())
                        ],
                        placeholder="Select a publisher...",
                        className="publisher-select-dropdown mt-2"
                    )
                ]),
                dbc.CardBody([
                    dcc.Graph(
                        id='publisher-trend-graph',
                        config={'displayModeBar': False}
                    )
                ])
            ], className="content-card shadow-sm mb-4")
        ], width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="fas fa-robot me-2"),  
                        "AI Book Insights"
                    ], className="section-title")
                ]),
                dbc.CardBody([
    
                    dbc.Alert([
                        html.I(className="fas fa-info-circle me-2"),
                        "Select a book to get an AI-generated summary."
                    ], color="info", className="mb-4"),
                    
     
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Book", className="form-label fw-bold mb-2"),
                            dcc.Dropdown(
                                id='book-title-dropdown',
                                options=[
                                    {'label': f"{title} by {author}", 'value': json.dumps({'title': title, 'author': author})}
                                    for title, author in df[['title', 'author']].drop_duplicates().values
                                ],
                                placeholder="Choose a book from the collection...",
                                className="book-select-dropdown"
                            ),
                        ], width=12, lg=8, className="mb-3 mb-lg-0"),
                        dbc.Col([
                            html.Label("\u00A0", className="form-label d-none d-lg-block mb-2"),  
                            dbc.Button([
                                html.I(className="fas fa-magic me-2"),
                                "Generate Summary"
                            ], 
                            id="get-summary-button",
                            color="primary",
                            className="w-100 summary-button"
                            ),
                        ], width=12, lg=4),
                    ], className="mb-4"),

                    html.Div([
                        html.Div([
                            html.I(className="fas fa-book-reader me-2"),
                            "Book Summary",
                        ], className="summary-header mb-3"),
                        
                        dbc.Card([
                            dbc.CardBody([
                                dbc.Spinner(
                                    html.Div(
                                        id="summary-content",
                                        className="summary-text"
                                    ),
                                    color="primary",
                                    size="md",
                                    type="border"
                                )
                            ])
                        ], className="summary-container")
                    ], id="summary-section", className="mt-2")
                ])
            ], className="content-card shadow-sm")
        ], width=12)
    ]),

    dbc.Modal([
        dbc.ModalHeader(html.H4(id='summary-modal-title')),
        dbc.ModalBody(html.P(id='summary-modal-content')),
        dbc.ModalFooter(
            dbc.Button("Close", id='close-modal-button', className="ms-auto")
        )
    ], id='summary-modal', size='lg'),
], fluid=False, className="dashboard-container")

@app.callback(
    Output('top-publishers-container', 'children'),
    Input('top-publishers-container', 'id')
)
def update_top_publishers(id):
    top_ranked_books = df[df['rank'].between(1, 5)]
    publisher_counts = top_ranked_books['publisher'].value_counts().head(5)
    
    publisher_cards = []
    icons = ['fa-star', 'fa-gem', 'fa-crown', 'fa-award', 'fa-medal']
    colors = ['#4361ee', '#3a0ca3', '#7209b7', '#f72585', '#4cc9f0']
    
    for i, (publisher, count) in enumerate(publisher_counts.items()):
        card = dbc.Card([
            html.Div([
                html.Div([
                    html.I(className=f"fas {icons[i]}")
                ], className="publisher-icon", style={'backgroundColor': colors[i]}),
                html.Div([
                    html.H5(publisher, className="publisher-name"),
                    html.P([
                        html.I(className="fas fa-book me-2"),
                        f"{count} books in Top 5"
                    ], className="publisher-stats")
                ])
            ], className="publisher-card-content")
        ], className="publisher-card mb-3")
        publisher_cards.append(card)
    
    return publisher_cards

@app.callback(
    [Output('books-table', 'data'),
     Output('books-table', 'columns')],
    Input('date-dropdown', 'value')
)
def update_books_table(selected_date):
    if not selected_date:
        return [], []
    
    date_books = df[df['published_date'] == selected_date].sort_values('rank')
    
    table_data = date_books[[
        'title', 'author', 'publisher', 'rank'
    ]].to_dict('records')
    
    for row in table_data:
        row['get_summary'] = 'Click for Summary'
    
    columns = [
        {'name': 'Title', 'id': 'title'},
        {'name': 'Author', 'id': 'author'},
        {'name': 'Publisher', 'id': 'publisher'},
        {'name': 'Rank', 'id': 'rank', 'type': 'numeric'},
        {
            'name': 'Summary',
            'id': 'get_summary',
            'type': 'text',
            'presentation': 'markdown'
        }
    ]
    
    return table_data, columns

@app.callback(
    Output('summary-modal', 'is_open'),
    Output('summary-modal-title', 'children'),
    Output('summary-modal-content', 'children'),
    Input('books-table', 'active_cell'),
    Input('books-table', 'data'),
    Input('close-modal-button', 'n_clicks'),
    prevent_initial_call=True
)
def handle_summary_click(active_cell, table_data, close_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, "", ""
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    if trigger_id == 'close-modal-button.n_clicks':
        return False, "", ""
    
    if active_cell and active_cell['column_id'] == 'get_summary':
        row = table_data[active_cell['row']]
        title = row['title']
        author = row['author']
        summary = get_book_summary(title, author)
        return True, f"{title} by {author}", summary
    
    return False, "", ""

@app.callback(
    Output("summary-content", "children"),
    Input("get-summary-button", "n_clicks"),
    State("book-title-dropdown", "value"),
    prevent_initial_call=True
)
def update_book_summary(n_clicks, book_info):
    if not n_clicks or not book_info:
        return html.Div([
            html.I(className="fas fa-arrow-up me-2"),
            "Select a book and click 'Generate Summary'"
        ], className="text-muted text-center py-4")
    
    book_data = json.loads(book_info)
    summary = get_book_summary(book_data['title'], book_data['author'])
    
    return html.Div([
        html.H5([
            html.I(className="fas fa-book me-2"),
            f"{book_data['title']}"
        ], className="book-title mb-2"),
        html.P([
            html.I(className="fas fa-pen-fancy me-2"),
            f"By {book_data['author']}"
        ], className="text-muted mb-4"),
        html.Hr(),
        html.Div([
            html.I(className="fas fa-quote-left me-2 text-muted"),
            html.Span(summary, className="summary-content"),
            html.I(className="fas fa-quote-right ms-2 text-muted"),
        ], className="mt-3")
    ])

@app.callback(
    Output('publisher-trend-graph', 'figure'),
    Input('publisher-trend-dropdown', 'value')
)
def update_publisher_trend(selected_publisher):
    if not selected_publisher:
        return {
            'data': [],
            'layout': {
                'title': 'Select a publisher to view trends',
                'showlegend': False,
                'height': 400,
                'template': 'plotly_white'
            }
        }

    top_ranked_books = df[
        (df['rank'].between(1, 5)) & 
        (df['publisher'] == selected_publisher)
    ]
    
    top_ranked_books['year'] = pd.to_datetime(top_ranked_books['published_date']).dt.year
    yearly_counts = top_ranked_books.groupby('year').size().reset_index(name='count')

    max_count = yearly_counts['count'].max()

    if max_count <= 5:
        step = 1
    elif max_count <= 10:
        step = 2
    else:
        step = 5

    fig = go.Figure(data=[
        go.Bar(
            x=yearly_counts['year'],
            y=yearly_counts['count'],
            marker_color='#4361ee',
            text=yearly_counts['count'], 
            textposition='outside',  
        )
    ])
    
    fig.update_layout(
        title=f'Top 5 Bestsellers by {selected_publisher} (Yearly)',
        xaxis_title='Year',
        yaxis_title='Number of Books in Top 5',
        showlegend=False,
        height=400,
        template='plotly_white',
        xaxis=dict(
            tickmode='linear',
            tickangle=0,
        ),
        yaxis=dict(
            tickmode='linear',
            dtick=step,  
            range=[0, max_count + (step/2)], 
            
            
        ),
        margin=dict(t=80, r=20, b=40, l=60),  
        bargap=0.4,  
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8053)
