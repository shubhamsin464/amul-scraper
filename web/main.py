from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import os

from core import database
from core.config import settings

app = FastAPI(title="Product Availability Monitor Dashboard")

templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    products = await database.get_products()
    pincodes = await database.get_pincodes()
    logs = await database.get_recent_logs(limit=100)
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "products": products,
            "pincodes": pincodes,
            "logs": logs
        }
    )

@app.post("/add_product")
async def add_product(url: str = Form(...), name: str = Form(...)):
    await database.add_product(url, name)
    return RedirectResponse(url="/", status_code=303)

@app.post("/remove_product")
async def remove_product(product_id: int = Form(...)):
    await database.remove_product(product_id)
    return RedirectResponse(url="/", status_code=303)

@app.post("/add_pincode")
async def add_pincode(pincode: str = Form(...)):
    await database.add_pincode(pincode)
    return RedirectResponse(url="/", status_code=303)

@app.post("/remove_pincode")
async def remove_pincode(pincode: str = Form(...)):
    await database.remove_pincode(pincode)
    return RedirectResponse(url="/", status_code=303)
