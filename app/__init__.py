from typing import Annotated
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from .database.models import User, Item
from .database import create_db_and_tables, SessionDep
from .security import verify_password, hash_password
from .auth import create_access_token, get_current_user


app = FastAPI()

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 configuration (required for the lock icon)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Root
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Token route for Swagger login (form-based)
@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep
):
    user = session.exec(select(User).where(User.email == form_data.username)).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# JSON-based login route (non-Swagger, utile pour les clients custom)
@app.post("/api/v1/auth/login")
async def auth_login(user: User, session: SessionDep):
    db_user = session.exec(select(User).where(User.email == user.email)).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    token = create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

# Dummy route to simulate file serving
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}

# CRUD Items
@app.post("/api/v1/items/create")
async def create_item(
    item: Item,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    item.user_id = current_user.id  # Associer l'item à l'utilisateur connecté
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@app.get("/api/v1/items/me")
def read_my_items(session: SessionDep, current_user: User = Depends(get_current_user)):
    return session.exec(select(Item).where(Item.owner_id == current_user.id)).all()


@app.put("/api/v1/items/{item_id}")
async def update_item(
    item_id: int,
    item: Item,
    token: Annotated[str, Depends(oauth2_scheme)]
):
    return {"item_id": item_id, **item.dict()}

@app.get("/api/v1/items")
def read_items(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Item]:
    return session.exec(select(Item).offset(offset).limit(limit)).all()

@app.get("/api/v1/items/{item_id}")
def read_item(item_id: int, session: SessionDep) -> Item:
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.delete("/api/v1/items/{item_id}")
def delete_item(
    item_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé : admin uniquement.")
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item non trouvé")
    session.delete(item)
    session.commit()
    return {"ok": True, "message": f"Item {item_id} supprimé"}

# User routes
@app.get("/api/v1/users/me")
async def read_user_me(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email}

@app.get("/api/v1/users/")
async def read_users(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"message": "Liste des utilisateurs restreinte"}

@app.post("/api/v1/users/create")
async def create_user(user: User, session: SessionDep):
    user.password = hash_password(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {
        "id": user.id,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "email": user.email,
        "photo_name": user.photo_name,
        "role": user.role
    }
