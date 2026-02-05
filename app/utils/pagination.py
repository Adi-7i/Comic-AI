"""
Pagination utilities.

Standardizes pagination for list endpoints.
"""

from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field, conint
from beanie import Document
from fastapi import Query

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """
    Generic pagination response using Pydantic generics.
    
    Structure:
    {
        "items": [...],
        "total": 100,
        "page": 1,
        "size": 20,
        "pages": 5
    }
    """
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [{"id": 1, "name": "Item 1"}],
                "total": 100,
                "page": 1,
                "size": 20,
                "pages": 5
            }
        }
    }


class Params(BaseModel):
    """
    Pagination query parameters.
    """
    page: int = 1
    size: int = 20


def pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
) -> Params:
    """Dependency for query parameters."""
    return Params(page=page, size=size)


async def paginate(
    query,
    params: Params,
    model_class
) -> Page[T]:
    """
    Paginate a Beanie find query.
    
    Args:
        query: Beanie FindMany object
        params: Pagination params (page, size)
        model_class: The Pydantic model class for response items (can be same as Beanie doc)
        
    Returns:
        Page[T] response
    """
    total = await query.count()
    skip = (params.page - 1) * params.size
    
    items_docs = await query.skip(skip).limit(params.size).to_list()
    
    # If model_class is different from Beanie Document (e.g. Response Schema),
    # we might need conversion. Assuming items_docs are compatible or same type for now.
    # In many cases usage will be: paginate(User.find(...), params, UserResponse)
    
    # Simple conversion if needed, otherwise distinct
    # For simplicity, we assume items_docs are list of Documents satisfying the Generics T
    
    total_pages = (total + params.size - 1) // params.size
    
    return Page(
        items=items_docs,
        total=total,
        page=params.page,
        size=params.size,
        pages=total_pages
    )
