"""Utilities for converting between domain models and schemas."""

from typing import TypeVar, Type, List, Any

# T represents the source domain model type
T = TypeVar('T')
# S represents the target Pydantic schema type
S = TypeVar('S')


def convert_domain_to_schema(domain_obj: T, schema_class: Type[S]) -> S:
    """
    Convert a domain model instance to a Pydantic schema instance.

    Relies on Pydantic's `from_orm` or `model_validate` with `from_attributes=True`
    being effective for the given types.
    
    Args:
        domain_obj: The source domain model instance (e.g., models.Herd).
        schema_class: The target Pydantic schema class (e.g., schemas.Herd).
        
    Returns:
        An instance of the target Pydantic schema.
    """
    if domain_obj is None:
        # Or handle as per desired behavior, e.g., raise ValueError
        return None # type: ignore
    return schema_class.from_orm(domain_obj) # type: ignore


def convert_domain_list_to_schema(
    domain_list: List[T],
    schema_class: Type[S]
) -> List[S]:
    """
    Convert a list of domain model instances to a list of Pydantic schema instances.
    
    Args:
        domain_list: List of source domain model instances.
        schema_class: Target Pydantic schema class.
        
    Returns:
        A list of target Pydantic schema instances.
    """
    return [schema_class.from_orm(domain_obj) for domain_obj in domain_list if domain_obj is not None] # type: ignore