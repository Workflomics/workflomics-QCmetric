import os
import pytest
from fastapi.testclient import TestClient
from pubmetric.api_controller import app, periodic_graph_generation, recreate_graph


from fastapi import FastAPI
from fastapi.testclient import TestClient


client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Welcome to Pubmetric!"}


def test_graph_generation():
    periodic_graph_generation()
