# Local HTTP Server for Testing

This simple HTTP server serves files from the `local_html` and `assets` directories on localhost.

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. For Playwright, you need to install the browsers:

```bash
playwright install
```

## Running the Server

To start the HTTP server on the default port (8080):

```bash
python server.py
```

To specify a custom port:

```bash
python server.py 9000
```

The server will serve files from:
- `local_html/` - All HTML files
- `assets/` - All static assets (images, CSS, JS, etc.)

## Available Content Types

### Blog Articles

Blog articles are accessible at:
- http://localhost:8080/ikuoikuo_2005/e/[article_id].html

### Archive Pages

Archive pages are accessible at:
- http://localhost:8080/ikuoikuo_2005/arcv.html
- http://localhost:8080/ikuoikuo_2005/arcv_[number].html

### Monthly Archives

Monthly archive pages are accessible at:
- http://localhost:8080/ikuoikuo_2005/m/[YYYYMM].html

For example:
- http://localhost:8080/ikuoikuo_2005/m/201004.html (April 2010)
- http://localhost:8080/ikuoikuo_2005/m/200911.html (November 2009)

The sidebar "バックナンバー" (back number) section contains links to all monthly archives.

## Running the Playwright Test

The Playwright test script will:
1. Start the server automatically
2. Open a browser window
3. Navigate to the server
4. Take a screenshot
5. Wait for user input before closing

To run the test:

```bash
python playwright_test.py
```

Press Enter to continue after the browser opens, or Ctrl+C to exit.

## Manual Testing

You can also manually test by:

1. Starting the server: `python server.py`
2. Opening your browser and navigating to:
   - http://localhost:8080/

The server will automatically search for files in both `local_html/` and `assets/` directories. 

## Testing Monthly Archives

To test the monthly archive functionality:

1. Run the server: `python server.py`
2. Navigate to any blog article, e.g., http://localhost:8080/ikuoikuo_2005/e/4846a3e02780eec9e21428510723d478.html
3. Click on any month in the "バックナンバー" section in the sidebar
4. You should be redirected to the monthly archive page for that month 