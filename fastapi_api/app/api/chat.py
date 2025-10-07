"""Назначение: определяет, какие HTTP-запросы будут обрабатываться и как."""
from fastapi import APIRouter


chat_router = APIRouter(prefix="/chat", tags=["chat"])
tasks_router = APIRouter(prefix="/status/{task_id}", tags=["tasks"])
