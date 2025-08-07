from setuptools import setup, find_packages
setup(
    name="osedev",
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        "fabric3",
        "psycopg2==2.8",
        "django==2.0",
        "django-fsm",
        "django-allauth",
        "django-allauth-extras",
        "django-dartium",
        "django-yamlfield",
        "jsonfield",
        "celery",
        "channels==1.1.8",
        "asgi_ipc",
        "markdown2",
        "googlemaps",
        "google-api-python-client",
    ],
    extras_require={
        "lint": [
            "pylint==2.10.0"
        ],
        "test": [
            "coverage",
            "factory-boy",
            "coverage",
        ],
    },
)
