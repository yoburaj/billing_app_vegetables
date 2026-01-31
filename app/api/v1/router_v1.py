from fastapi import APIRouter
from app.api.v1.vegetables.vegetable_create import router as veg_router
from app.api.v1.vegetables.price_update import router as price_router
from app.api.v1.billing.bill_create import router as bill_router
from app.api.v1.auth.login import router as login_router
from app.api.v1.auth.signup import router as signup_router
from app.api.v1.admin.admin import router as admin_router
from app.api.v1.inventory.inventory_api import router as inventory_router

router = APIRouter(prefix="/api/v1")

router.include_router(login_router, prefix="/auth", tags=["Authentication"])
router.include_router(signup_router, prefix="/auth", tags=["Authentication"])
router.include_router(admin_router, prefix="/admin", tags=["Admin"])
router.include_router(inventory_router, tags=["Inventory"])
router.include_router(veg_router, tags=["Vegetables"])
router.include_router(price_router, tags=["Vegetables"])
router.include_router(bill_router, tags=["Billing"])
