from fastapi import APIRouter
from app.api.v1.vegetables.vegetable_create import router as veg_router
from app.api.v1.billing.bill_create import router as bill_router

router = APIRouter(prefix="/api/v1")

router.include_router(veg_router, tags=["Vegetables"])
router.include_router(bill_router, tags=["Billing"])
