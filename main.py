from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from databases import Database
from uuid import UUID as UUIDType
from datetime import datetime
from enum import Enum as PyEnum
import uuid
import os

# URL подключения к базе данных PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/tender_service")


# Создание экземпляра FastAPI
app = FastAPI()

# URL подключения к базе данных PostgreSQL
# DATABASE_URL = "postgresql://postgres:postgres@db/tender_service"

# Метаданные базы данных для SQLAlchemy
metadata = MetaData()


# Определение типа организации
class OrganizationType(PyEnum):
    IE = "IE"
    LLC = "LLC"
    JSC = "JSC"


# Определение таблицы организаций (organizations)
organizations = Table(
    "organization",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("name", String(100), nullable=False),
    Column("description", String),
    Column("type", Enum(OrganizationType), nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow),
)

# Определение таблицы пользователей (employees)
employees = Table(
    "employee",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("username", String(50), unique=True, nullable=False),
    Column("first_name", String(50)),
    Column("last_name", String(50)),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow),
)

# Определение таблицы тендеров (tenders)
tenders = Table(
    "tender",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("name", String(100), nullable=False),
    Column("description", String),
    Column("status", String(50), nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow),
    Column("organization_id", UUID(as_uuid=True), ForeignKey("organization.id")),
    Column("creator_username", String(50), nullable=False),
    Column("version", Integer, default=1)
)

# Таблица для хранения версий тендеров
tender_versions = Table(
    "tender_version",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("tender_id", UUID(as_uuid=True), ForeignKey("tender.id")),
    Column("name", String(100)),
    Column("description", String),
    Column("status", String(50)),
    Column("version", Integer),
    Column("created_at", DateTime),
    Column("updated_at", DateTime)
)

# Движок базы данных с помощью SQLAlchemy
engine = create_engine(DATABASE_URL)

# Подключение к базе данных через библиотеку databases
database = Database(DATABASE_URL)


# Создание таблиц при старте
def create_tables():
    metadata.create_all(engine)


# Старт приложения: подключение к базе данных и создание таблиц
@app.on_event("startup")
async def startup():
    await database.connect()
    create_tables()


# Завершение работы приложения: отключение от базы данных
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# Модель для создания организации
class OrganizationCreateRequest(BaseModel):
    name: str
    description: str
    type: str


# Эндпоинт для создания новой организации
@app.post("/api/organizations/new")
async def create_organization(request: OrganizationCreateRequest):
    organization_id = uuid.uuid4()  # Генерация UUID для организации
    now = datetime.utcnow()  # Текущая дата и время как объект datetime
    query = organizations.insert().values(
        id=organization_id,
        name=request.name,
        description=request.description,
        type=request.type,
        created_at=now,
        updated_at=now
    )
    try:
        await database.execute(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Organization created successfully", "organization_id": str(organization_id)}


# Модель для создания пользователя
class UserCreateRequest(BaseModel):
    username: str
    first_name: str
    last_name: str


# Эндпоинт для создания нового пользователя
@app.post("/api/users/new")
async def create_user(request: UserCreateRequest):
    user_id = uuid.uuid4()  # Генерация UUID для пользователя
    now = datetime.utcnow()
    query = employees.insert().values(
        id=user_id,
        username=request.username,
        first_name=request.first_name,
        last_name=request.last_name,
        created_at=now,  # Преобразованная дата
        updated_at=now  # Преобразованная дата
    )

    await database.execute(query)
    return {"message": "User created successfully", "id": str(user_id)}  # Возвращаем ID пользователя


# Модель для назначения ответственного пользователя за организацию
class AssignResponsibleRequest(BaseModel):
    organization_id: UUIDType
    user_id: UUIDType


# Таблица для хранения информации об ответственных за организацию
organization_responsible = Table(
    "organization_responsible",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("organization_id", UUID(as_uuid=True), ForeignKey("organization.id")),
    Column("user_id", UUID(as_uuid=True), ForeignKey("employee.id"))
)


# Эндпоинт для назначения ответственного за организацию
@app.post("/api/organizations/assign_responsible")
async def assign_responsible(request: AssignResponsibleRequest):
    responsible_id = uuid.uuid4()
    query = organization_responsible.insert().values(
        id=responsible_id,
        organization_id=request.organization_id,
        user_id=request.user_id
    )
    await database.execute(query)
    return {"message": "Responsible user assigned successfully", "id": responsible_id}


# Модель для создания тендера
class TenderCreateRequest(BaseModel):
    name: str
    description: str
    status: str
    organization_id: UUIDType
    creator_username: str


# Эндпоинт для создания нового тендера
@app.post("/api/tenders/new")
async def create_tender(request: TenderCreateRequest):
    tender_id = uuid.uuid4()
    query = tenders.insert().values(
        id=tender_id,
        name=request.name,
        description=request.description,
        status=request.status,
        organization_id=request.organization_id,
        creator_username=request.creator_username,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        version=1
    )
    await database.execute(query)

    return {"message": "Tender created successfully", "id": tender_id}


class TenderEditRequest(BaseModel):
    name: str
    description: str


# Логика для редактирования тендера и сохранения предыдущей версии
@app.patch("/api/tenders/{tender_id}/edit")
async def edit_tender(tender_id: UUIDType, request: TenderEditRequest):
    existing_tender = await database.fetch_one(tenders.select().where(tenders.c.id == tender_id))

    if existing_tender:
        # Если версия не задана (None), устанавливаем версию 1
        current_version = existing_tender['version'] or 1

        # Сохранение текущей версии в таблицу версий
        query = tender_versions.insert().values(
            id=uuid.uuid4(),  # Генерация UUID для версии тендера
            tender_id=existing_tender['id'],
            name=existing_tender['name'],
            description=existing_tender['description'],
            status=existing_tender['status'],
            version=current_version,
            created_at=existing_tender['created_at'],
            updated_at=existing_tender['updated_at']
        )
        await database.execute(query)

        # Обновляем тендер и увеличиваем версию
        query = tenders.update().where(tenders.c.id == tender_id).values(
            name=request.name,
            description=request.description,
            updated_at=datetime.utcnow(),
            version=current_version + 1
        )
        await database.execute(query)
        return {"message": "Tender updated successfully"}

    raise HTTPException(status_code=404, detail="Tender not found")


# Логика для отката версии тендера
@app.put("/api/tenders/{tender_id}/rollback/{version}")
async def rollback_tender(tender_id: UUIDType, version: int):
    # Поиск версии в таблице версий тендеров
    version_data = await database.fetch_one(tender_versions.select().where(
        (tender_versions.c.tender_id == tender_id) & (tender_versions.c.version == version)
    ))

    if version_data:
        # Откат к указанной версии
        query = tenders.update().where(tenders.c.id == tender_id).values(
            name=version_data['name'],
            description=version_data['description'],
            status=version_data['status'],
            version=version,
            updated_at=datetime.utcnow()
        )
        await database.execute(query)
        return {"message": f"Tender rolled back to version {version}"}
    else:
        raise HTTPException(status_code=404, detail="Version not found")


# Эндпоинт для публикации тендера
@app.post("/api/tenders/{tender_id}/publish")
async def publish_tender(tender_id: UUIDType):
    query = tenders.update().where(tenders.c.id == tender_id).values(status="PUBLISHED", updated_at=datetime.utcnow())
    await database.execute(query)
    return {"message": "Tender published successfully"}


# Эндпоинт для закрытия тендера
@app.post("/api/tenders/{tender_id}/close")
async def close_tender(tender_id: UUIDType):
    query = tenders.update().where(tenders.c.id == tender_id).values(status="CLOSED", updated_at=datetime.utcnow())
    await database.execute(query)
    return {"message": "Tender closed successfully"}


# Модель для редактирования тендера
class TenderEditRequest(BaseModel):
    name: str
    description: str


# Эндпоинт для редактирования тендера
@app.patch("/api/tenders/{tender_id}/edit")
async def edit_tender(tender_id: UUIDType, request: TenderEditRequest):
    query = tenders.update().where(tenders.c.id == tender_id).values(
        name=request.name,
        description=request.description,
        updated_at=datetime.utcnow()
    )
    await database.execute(query)
    return {"message": "Tender updated successfully"}


@app.put("/api/tenders/{tender_id}/rollback/{version}")
async def rollback_tender(tender_id: UUIDType, version: int):
    query = tenders.update().where(tenders.c.id == tender_id).values(
        status="ROLLED_BACK", updated_at=datetime.utcnow()
    )
    await database.execute(query)
    return {"message": f"Tender rolled back to version {version}"}


# Эндпоинт для получения списка тендеров
@app.get("/api/tenders")
async def get_tenders():
    query = tenders.select()
    results = await database.fetch_all(query)
    return results


# Получение тендеров пользователя
@app.get("/api/tenders/my")
async def get_user_tenders(username: str):
    query = tenders.select().where(tenders.c.creator_username == username)
    results = await database.fetch_all(query)
    return results


# Таблица для предложений
bids = Table(
    "bid",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("name", String(100), nullable=False),
    Column("description", String),
    Column("status", String(50), nullable=False),
    Column("tender_id", UUID(as_uuid=True), ForeignKey("tender.id")),
    Column("organization_id", UUID(as_uuid=True), ForeignKey("organization.id")),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("creator_username", String(50), nullable=False),
    Column("updated_at", DateTime, default=datetime.utcnow),
    Column("version", Integer, default=1)
)

# Таблица для хранения версий предложений
bid_versions = Table(
    "bid_version",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("bid_id", UUID(as_uuid=True), ForeignKey("bid.id")),
    Column("name", String(100)),
    Column("description", String),
    Column("status", String(50)),
    Column("version", Integer),
    Column("created_at", DateTime),
    Column("updated_at", DateTime)
)


# Модель для создания предложения
class BidCreateRequest(BaseModel):
    name: str
    description: str
    status: str
    tender_id: UUIDType
    organization_id: UUIDType
    creator_username: str


# Эндпоинт для создания нового предложения
@app.post("/api/bids/new")
@app.post("/api/bids/new")
async def create_bid(request: BidCreateRequest):
    bid_id = uuid.uuid4()
    query = bids.insert().values(
        id=bid_id,
        name=request.name,
        description=request.description,
        status=request.status,
        tender_id=request.tender_id,
        organization_id=request.organization_id,
        creator_username=request.creator_username,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    await database.execute(query)
    return {"message": "Bid created successfully", "id": bid_id}


# Модель для редактирования предложения
class BidEditRequest(BaseModel):
    name: str
    description: str


# Эндпоинт для редактирования предложения
@app.patch("/api/bids/{bid_id}/edit")
async def edit_bid(bid_id: UUIDType, request: BidEditRequest):
    # Проверка существования предложения
    existing_bid = await database.fetch_one(bids.select().where(bids.c.id == bid_id))
    if existing_bid:
        current_version = existing_bid['version'] if existing_bid['version'] is not None else 1

        # Сохранение текущей версии в таблицу bid_versions (если такая таблица существует)
        query = bid_versions.insert().values(
            id=uuid.uuid4(),
            bid_id=existing_bid['id'],
            name=existing_bid['name'],
            description=existing_bid['description'],
            status=existing_bid['status'],
            version=current_version,
            created_at=existing_bid['created_at'],
            updated_at=existing_bid['updated_at']
        )
        await database.execute(query)

        # Обновляем предложение и увеличиваем его версию
        query = bids.update().where(bids.c.id == bid_id).values(
            name=request.name,
            description=request.description,
            updated_at=datetime.utcnow(),
            version=current_version + 1  # Увеличиваем версию на 1
        )
        await database.execute(query)

        return {"message": "Bid updated successfully"}
    else:
        # Если предложение не найдено
        raise HTTPException(status_code=404, detail="Bid not found")


@app.put("/api/bids/{bid_id}/rollback/{version}")
async def rollback_bid(bid_id: UUIDType, version: int):
    version_data = await database.fetch_one(bid_versions.select().where(
        (bid_versions.c.bid_id == bid_id) & (bid_versions.c.version == version)
    ))
    if version_data:
        query = bids.update().where(bids.c.id == bid_id).values(
            name=version_data['name'],
            description=version_data['description'],
            status=version_data['status'],
            version=version,
            updated_at=datetime.utcnow()
        )
        await database.execute(query)
        return {"message": f"Bid rolled back to version {version}"}
    else:
        raise HTTPException(status_code=404, detail="Version not found")


# Получение списка предложений пользователя
@app.get("/api/bids/my")
async def get_user_bids(username: str):
    # Предполагается, что поле username добавлено в таблицу bids или связь реализована через тендеры
    query = bids.select().where(bids.c.creator_username == username)
    results = await database.fetch_all(query)
    return results


# Получение списка предложений для тендера
@app.get("/api/bids/{tender_id}/list")
async def get_bids_for_tender(tender_id: UUIDType):
    query = bids.select().where(bids.c.tender_id == tender_id)
    results = await database.fetch_all(query)
    return results


# Модель для редактирования предложения
class BidEditRequest(BaseModel):
    name: str
    description: str


# Эндпоинт для редактирования предложения
@app.patch("/api/bids/{bid_id}/edit")
async def edit_bid(bid_id: UUIDType, request: BidEditRequest):
    query = bids.update().where(bids.c.id == bid_id).values(
        name=request.name,
        description=request.description,
        updated_at=datetime.utcnow()
    )
    await database.execute(query)
    return {"message": "Bid updated successfully"}


# Эндпоинт для отката версии предложения
@app.put("/api/bids/{bid_id}/rollback/{version}")
async def rollback_bid(bid_id: UUIDType, version: int):
    # Предполагается, что версии отслеживаются и можно откатывать назад
    query = bids.update().where(bids.c.id == bid_id).values(
        status="ROLLED_BACK", updated_at=datetime.utcnow()
    )
    await database.execute(query)
    return {"message": f"Bid rolled back to version {version}"}


# Эндпоинт для просмотра отзывов на предложения
@app.get("/api/bids/{tender_id}/reviews")
async def get_reviews_for_bids(tender_id: UUIDType, author_username: str, organization_id: UUIDType):
    query = bids.select().where(
        (bids.c.tender_id == tender_id) &
        (bids.c.creator_username == author_username) &
        (bids.c.organization_id == organization_id)
    )
    results = await database.fetch_all(query)
    return results


# Простой endpoint для проверки доступности сервера
@app.get("/api/ping")
async def ping():
    return {"message": "ok"}
