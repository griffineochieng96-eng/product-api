import platform
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Response
from sqlmodel import Session, select

from database.session import get_session
from models.user import User, UserResponse
from models.product import Product
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from security.password import hash_password, verify_password
from security.auth import get_current_user
from config import SECRET_KEY, ALGORITHM

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Product API",
    lifespan=lifespan,
)

START_TIME = time.time()
APP_VERSION = "1.0.0"



@app.get("/")
def root():
    return {"message": "Product API is running"}

@app.get("/health")
def health():
    uptime = time.time() - START_TIME

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": APP_VERSION,
        "uptime_seconds": round(uptime, 2),
        "system": {
            "platform": platform.system(),
            "python_version": platform.python_version(),
        },
    }

@app.post("/register", status_code=201, response_model=UserResponse)
def register(user: User, session: Session = Depends(get_session)):
    existing_user = session.exec(
        select(User).where(User.username == user.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Username already exists",
        )
    user.password = hash_password(user.password)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user




@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.exec(
        select(User).where(User.username == form_data.username)
    ).first()

    if not user or not verify_password(
     form_data.password,
     user.password,
):
     raise HTTPException(
        status_code=401,
        detail="Invalid username or password",
    )

    token = jwt.encode(
        {
            "sub": user.username,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }
@app.post("/products", status_code=201)
def create_product(
    product: Product,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    session.add(product)
    session.commit()
    session.refresh(product)

    return product

@app.get("/products")
def get_products(
    session: Session = Depends(get_session),
     current_user: User = Depends(get_current_user),
):
    products = session.exec(select(Product)).all()
    return products

@app.get("/products/{product_id}")
def get_product(
    product_id: int,
    session: Session = Depends(get_session),
     current_user: User = Depends(get_current_user),
):
    product = session.get(Product, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product
@app.patch("/products/{product_id}")
def update_product(
    product_id: int,
    product_data: Product,
    session: Session = Depends(get_session),
     current_user: User = Depends(get_current_user),
):
    product = session.get(Product, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    product.name = product_data.name
    product.description = product_data.description
    product.price = product_data.price
    product.stock = product_data.stock

    session.add(product)
    session.commit()
    session.refresh(product)

    return product

@app.delete("/products/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    session: Session = Depends(get_session),
     current_user: User = Depends(get_current_user),
):
    product = session.get(Product, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    session.delete(product)
    session.commit()

    return Response(status_code=204)