# Django Blog Project

- Tagging system
- SEO-friendly URLs for blog posts
- Recommendation Posts using QuerySets
- Search Engine with PostgreSQL
- Custom template tags and filters
- Sitemap and Feed RSS

## Setup

Rename the __.env.example__ file to __.env__ then follow the steps:

1. `docker-compose up -d` for database
2. `pip install -r requirements.txt` to install dependencies
3. `python3 manage.py migrate` for migrations
4. `python3 manage.py loaddata blog_data.json` to load data
5. `python3 manage.py runserver` to start server

Go to http://127.0.0.1:8000 and start to use
