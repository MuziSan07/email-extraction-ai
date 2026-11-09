"""Email business-information extractor.

A FastAPI application that extracts structured business contact details
(name, title, company, email, phone, address, website) from email text using
an LLM (Groq via LangChain), stores them in SQLite, and can optionally pull
messages from Gmail via OAuth.

The package follows the Model-View-Controller (MVC) pattern:

    model/      Data access and domain logic (database, repository, schemas,
                LLM extraction, Gmail integration).
    view/       Presentation layer (Jinja2 templates, static assets).
    controller/ HTTP routes wiring requests to the model and view.
"""

__version__ = "1.0.0"
