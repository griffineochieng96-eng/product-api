import platform
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse
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


@app.get("/", response_class=HTMLResponse)
def portfolio():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Griffine Ochieng - Backend Portfolio</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                background: #f5f5f5;
            }

            .container {
                max-width: 900px;
                margin: auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }

            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }

            .student-info {
                background: #e8f4fd;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }

            .admission {
                color: #2980b9;
                font-weight: bold;
            }

            .assignment {
                margin: 12px 0;
                padding: 15px;
                background: #f8f9fa;
                border-left: 4px solid #3498db;
                border-radius: 6px;
            }

            .assignment a {
                color: #0366d6;
                text-decoration: none;
                font-weight: bold;
            }

            .assignment a:hover {
                text-decoration: underline;
            }

            .badge {
                background: #3498db;
                color: white;
                padding: 4px 10px;
                border-radius: 12px;
                margin-right: 10px;
                font-size: 0.85em;
            }

            .not-assigned {
                color: #7f8c8d;
            }

            .footer {
                margin-top: 30px;
                text-align: center;
                color: #95a5a6;
                border-top: 1px solid #ddd;
                padding-top: 20px;
            }
        </style>
    </head>

    <body>
        <div class="container">

            <h1>📚 Backend Development Portfolio</h1>

            <div class="student-info">
                <p><strong>Student Name:</strong> Griffine Ochieng</p>

                <p>
                    <strong>Admission Number:</strong>
                    <span class="admission">C027-01-0914/2024</span>
                </p>

                <p>
                    <strong>Email:</strong>
                    griffine.otieno24@students.dkut.ac.ke
                </p>
            </div>

            <h2>📝 Backend Assignments</h2>

            <p>
                Click on an assignment to view the source code on GitHub.
            </p>

            <div class="assignment">
                <span class="badge">Lesson 1</span>
                <span class="not-assigned">Not assigned</span>
            </div>

            <div class="assignment">
                <span class="badge">Lesson 2</span>
                <span class="not-assigned">Not assigned</span>
            </div>

            <div class="assignment">
                <span class="badge">Lesson 3</span>
                <span class="not-assigned">Not assigned</span>
            </div>

            <div class="assignment">
                <a href="https://github.com/griffineochieng96-eng/gighub-api"
                   target="_blank">
                    <span class="badge">Lesson 4</span>
                    PostgreSQL & SQLModel – Your First Database
                </a>
            </div>

            <div class="assignment">
                <a href="https://github.com/griffineochieng96-eng/library-api-lab4"
                   target="_blank">
                    <span class="badge">Lesson 5</span>
                    CRUD Operations
                </a>
            </div>

            <div class="assignment">
                <a href="https://github.com/griffineochieng96-eng/bookstore-api"
                   target="_blank">
                    <span class="badge">Lesson 6</span>
                    Error Handling & Validation
                </a>
            </div>

            <div class="assignment">
                <a href="https://github.com/griffineochieng96-eng/techvault-api"
                   target="_blank">
                    <span class="badge">Lesson 7</span>
                    User Authentication – JWT & Password Hashing
                </a>
            </div>

            <div class="assignment">
                <a href="https://github.com/griffineochieng96-eng/healthtrack-api"
                   target="_blank">
                    <span class="badge">Lesson 8</span>
                    Authorization & Rate Limiting
                </a>
            </div>

            <div class="assignment">
                <a href="https://github.com/griffineochieng96-eng/sendIt-api"
                   target="_blank">
                    <span class="badge">Lesson 9</span>
                    File Uploads & External APIs
                </a>
            </div>

            <div class="assignment">
                <a href="https://github.com/griffineochieng96-eng/product-api"
                   target="_blank">
                    <span class="badge">Lesson 10</span>
                    Testing & Deployment (Cloud)
                </a>
            </div>

            <div class="footer">
                <p>📍 Deployed on Render</p>
                <p>Backend Development Portfolio — Griffine Ochieng</p>
            </div>

        </div>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)
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