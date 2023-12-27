from flask import jsonify
from sqlalchemy import or_
from .models import APICall
from .database import db


def add_record(model, **kwargs):
    record = model(**kwargs)
    db.session.add(record)
    db.session.commit()
    return record.to_dict()


def update_record(model, record_id, **updates):
    record = model.query.get(record_id)
    if record:
        for key, value in updates.items():
            setattr(record, key, value)
        db.session.commit()
        return record.to_dict()
    return None


def find_record_by_id(model, record_id):
    record = model.query.get(record_id)
    return record.to_dict() if record else None


def find_records_paginated(model, page, per_page, **filters):
    query = model.query
    for attr, value in filters.items():
        query = query.filter(getattr(model, attr) == value)
    paginated_records = query.paginate(page, per_page, error_out=False)
    return {
        "items": [item.to_dict() for item in paginated_records.items],
        "total": paginated_records.total,
        "pages": paginated_records.pages,
        "current_page": page,
    }


def delete_record_by_id(model, record_id):
    record = model.query.get(record_id)
    if record:
        db.session.delete(record)
        db.session.commit()
        return {"status": "success"}
    return {"status": "record not found"}


def count_records_by_attribute(model, **attributes):
    count = model.query.filter_by(**attributes).count()
    return count


def search_records(model, search_term, fields):
    search_query = " ".join(f"{field}.ilike('%{search_term}%')" for field in fields)
    results = model.query.filter(db.text(search_query)).all()
    return [result.to_dict() for result in results]


def bulk_insert(model, list_of_dicts):
    db.session.bulk_insert_mappings(model, list_of_dicts)
    db.session.commit()


def bulk_update(model, updates):  # updates should be a list of dictionaries
    db.session.bulk_update_mappings(model, updates)
    db.session.commit()


def get_distinct_attribute_values(model, attribute):
    distinct_values = db.session.query(getattr(model, attribute)).distinct().all()
    return [value[0] for value in distinct_values if value[0] is not None]


def get_records_as_json(model, **filters):
    """
    Query records from the given SQLAlchemy model table, apply filters, and return as JSON.

    Args:
    model (db.Model): The SQLAlchemy model class to query.
    **filters: Optional keyword arguments that are used to filter the query results.

    Returns:
    str: A JSON string of the queried records.
    """
    try:
        query = model.query
        # Apply filters if provided
        for attr, value in filters.items():
            # Here we assume the filter is a direct equality, but you can customize this as needed
            # If the value is a list, we generate an OR condition
            if isinstance(value, list):
                query = query.filter(or_(*[getattr(model, attr) == v for v in value]))
            else:
                query = query.filter(getattr(model, attr) == value)

        # Execute the query and fetch all results
        records = query.all()
        # Convert records to a list of dictionaries
        records_list = [
            record.to_dict() for record in records
        ]  # Assumes a to_dict method on the model

        # Convert the list of dictionaries to a JSON string and return it
        return jsonify(records_list)
    except Exception as e:
        # Return an error message in JSON format
        return jsonify({"status": "error", "message": str(e)})


def delete_all_records(model):
    """
    Delete all records from the given SQLAlchemy model table.

    Args:
    model (db.Model): The SQLAlchemy model class of which all records will be deleted.

    Returns:
    dict: A dictionary with the status of the deletion and number of rows deleted or an error message.
    """
    try:
        # Delete all records from the table
        num_rows_deleted = db.session.query(model).delete()
        # Commit the changes to the database
        db.session.commit()
        return {"status": "success", "rows_deleted": num_rows_deleted}
    except Exception as e:
        # Rollback in case of any error
        db.session.rollback()
        return {"status": "error", "message": str(e)}
