"""Shared graph connection, explicitly restricted to this lab's database."""
import os
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase
from mbti_lab.database import project_database


def database():
    load_dotenv(Path(__file__).resolve().parent / '.env.mbti')
    return project_database(os.getenv('NEO4J_DATABASE', 'mbti-zodiac'))


def get_driver():
    database()
    if not os.getenv('NEO4J_PASSWORD'):
        raise ValueError('Set NEO4J_PASSWORD in local .env.mbti')
    driver = GraphDatabase.driver(os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
                                 auth=(os.getenv('NEO4J_USERNAME', 'neo4j'),
                                       os.environ['NEO4J_PASSWORD']))
    try:
        driver.verify_connectivity()
    except Exception:
        driver.close()
        raise
    return driver


def run(driver, cypher, **params):
    records, _, _ = driver.execute_query(cypher, parameters_=params, database_=database())
    return [record.data() for record in records]
