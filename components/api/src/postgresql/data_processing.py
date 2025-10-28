import logging
import os
from pathlib import Path
from typing import Type

import pandas as pd
from azure.storage.blob import ContainerClient
from postgresql.models import ChatMessage, Law, SelectieLijsten
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
SL_CONTAINER_NAME = "selectielijsten"

LOCAL_STORAGE = os.getenv("LOCAL_STORAGE", True)
FILE_SOURCES = {
    "selectielijsten.csv": os.getcwd()
    / Path(__file__).parent.parent.parent
    / "scrapers"
    / "selectielijsten"
    / "csv"
    / "selectielijsten.csv",
}


def download_csv_from_blob(file_name: str, db: Session) -> pd.DataFrame:
    container_client = ContainerClient.from_connection_string(
        AZURE_STORAGE_CONNECTION_STRING, SL_CONTAINER_NAME
    )
    blob_client = container_client.get_blob_client(file_name)
    stream = blob_client.download_blob().readall()
    df = pd.read_csv(
        pd.io.common.BytesIO(stream), encoding="utf-8", encoding_errors="replace"
    )
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df = df.fillna("NaN")

    return df


def get_model_from_filename(filename: str) -> Type[DeclarativeMeta]:
    """Return the SQLAlchemy model based on the filename."""
    model_mapping = {
        "law.csv": Law,
        "chat_message.csv": ChatMessage,
        "selectielijsten.csv": SelectieLijsten,
    }

    # Extract the base name of the file to handle full paths
    base_filename = filename.split("/")[-1]

    model = model_mapping.get(base_filename)
    if model is None:
        raise ValueError(f"No model found for filename: {filename}")

    return model


def get_sqlalchemy_schema(model) -> dict:
    """Extract column names and types from a SQLAlchemy model."""
    inspector = inspect(model)
    return {column.name: str(column.type) for column in inspector.columns}


def validate_csv(df, model):
    schema = get_sqlalchemy_schema(model)

    schema.pop("id", None)
    # Check for missing or extra columns
    missing_columns = set(schema.keys()) - set(df.columns)
    extra_columns = set(df.columns) - set(schema.keys())

    if missing_columns:
        raise ValueError(f"Missing columns in CSV: {missing_columns}")
    if extra_columns:
        raise ValueError(f"Extra columns in CSV: {extra_columns}")

    logger.info("CSV schema validated successfully!")
    return True


def insert_data(df, session: Session, model: Type[DeclarativeMeta]):
    """Insert valid CSV data into PostgreSQL using a SQLAlchemy ORM model."""
    # NOTE: needs to be upated to be modular (specifically the record check)
    records = df.to_dict(orient="records")

    try:
        instances = []

        for record in records:
            # Check if record with the same unique combination exists in the db
            existing_instance = (
                session.query(model)
                .filter_by(
                    selectielijsten=record.get("selectielijsten"),
                    categorie=record.get("categorie"),
                    waardering=record.get("waardering"),
                    voorbeeldstukken=record.get("voorbeeldstukken"),
                )
                .first()
            )

            if existing_instance is None:
                instances.append(model(**record))
            else:
                logger.info(
                    f"Skipping existing record with selectielijsten=\
                        {record.get('selectielijsten')}, "
                    f"categorie={record.get('categorie')}, waardering=\
                        {record.get('waardering')}, \
                    voorbeeldstukken={record.get('voorbeeldstukken')}"
                )

        if instances:
            session.add_all(instances)
            session.commit()
            logger.info(
                f"Data successfully inserted into \
                        {model.__tablename__}!"
            )
        else:
            logger.info("No new records to insert.")

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error inserting data into {model.__tablename__}: {e}")

    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error: {e}")


def upload_csv_to_db(file_name: str, db: Session):
    if LOCAL_STORAGE:
        # If using local storage, read the CSV file directly
        try:
            df = pd.read_csv(
                FILE_SOURCES[file_name], encoding="utf-8", encoding_errors="replace"
            ).fillna("")
        except FileNotFoundError:
            raise FileNotFoundError(
                f"File {FILE_SOURCES[file_name]} not found in local storage."
            )
    else:
        df = download_csv_from_blob(file_name, db)
    model = get_model_from_filename(file_name)
    validate_csv(df, model)
    insert_data(df, db, model)
    return f"Successfully uploaded data from CSV '{file_name}' \
        to {model.__tablename__}"
