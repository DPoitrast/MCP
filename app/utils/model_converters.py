"""Utilities for converting between domain models and schemas."""

from typing import TypeVar, Type, List

from .. import models
from ..schemas import Herd as HerdSchema

T = TypeVar('T')
S = TypeVar('S')


def convert_domain_to_schema(domain_obj: models.Herd, schema_class: Type[HerdSchema]) -> HerdSchema:
    """
    Convert a domain model to a Pydantic schema.
    
    Args:
        domain_obj: Domain model instance
        schema_class: Target Pydantic schema class
        
    Returns:
        Converted schema instance
    """
    return schema_class.from_orm(domain_obj)


def convert_domain_list_to_schema(
    domain_list: List[models.Herd], 
    schema_class: Type[HerdSchema]
) -> List[HerdSchema]:
    """
    Convert a list of domain models to Pydantic schemas.
    
    Args:
        domain_list: List of domain model instances
        schema_class: Target Pydantic schema class
        
    Returns:
        List of converted schema instances
    """
    return [schema_class.from_orm(domain_obj) for domain_obj in domain_list]