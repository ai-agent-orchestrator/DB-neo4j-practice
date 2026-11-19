"""Keep this project's writes in its dedicated database."""
DATABASE = 'mbti-zodiac'


def project_database(value):
    if value != DATABASE:
        raise ValueError(f'NEO4J_DATABASE must be {DATABASE}; restaurant DB is reserved.')
    return value
