from datetime import date
from typing import Optional
from uuid import UUID
from uuid import uuid4

from fastapi import Query
from pydantic import validator, Field

""" Модели и валидация входящих данных через pydantic """
