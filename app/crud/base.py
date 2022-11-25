from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD)
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def apply_filters(self, query, filters, exclude: List[str] = ()):
        if not is_dataclass(filters) or isinstance(filters, type):
            raise ValueError("Filters argument must be a dataclass")
        for filter_name, filter_value in asdict(filters).items():
            if filter_name not in exclude and filter_value is not None:
                model_attribute = getattr(self.model, filter_name, None)
                if model_attribute is not None:
                    query = query.filter(model_attribute == filter_value)
        return query

    def apply_ordering(self, query, ordering):
        if not is_dataclass(ordering) or isinstance(ordering, type):
            raise ValueError("Ordering argument must be a dataclass")
        ordering_dict = asdict(ordering)
        model_attribute = getattr(self.model, ordering_dict["order_by"], None)
        if model_attribute:
            query = (
                query.order_by(model_attribute.asc())
                if ordering_dict["direction"] == "asc"
                else query.order_by(model_attribute.desc())
            )
        return query

    def search(self, query, keyword: Any, search_fields: list):
        d = {column: keyword for column in search_fields}
        condition = or_(
            *[getattr(self.model, col).ilike(f"{val}%") for col, val in d.items()]
        )
        # for col, val in d.items():
        #     query = query.filter(getattr(self.model, col).ilike(f"{val}%"))
        query = query.filter(condition)
        return query

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: dataclass = None,
        ordering: dataclass = None,
        search_params: dataclass = None,
    ) -> List[ModelType]:

        query = db.query(self.model)
        if search_params and search_params.search and search_params.fields:
            query = self.search(
                query=query,
                keyword=search_params.search,
                search_fields=search_params.fields,
            )
        if filters and (not search_params or not search_params.search):
            query = self.apply_filters(query=query, filters=filters)
        if ordering and ordering.order_by:
            query = self.apply_ordering(query=query, ordering=ordering)
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
