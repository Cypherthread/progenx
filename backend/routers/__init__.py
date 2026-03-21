try:
    from routers import auth_router
except Exception as e:
    print(f"[WARN] auth_router import failed: {e}")

try:
    from routers import designs_router
except Exception as e:
    print(f"[WARN] designs_router import failed: {e}")

try:
    from routers import challenges_router
except Exception as e:
    print(f"[WARN] challenges_router import failed: {e}")

try:
    from routers import analytics_router
except Exception as e:
    print(f"[WARN] analytics_router import failed: {e}")
    analytics_router = None

try:
    from routers import billing_router
except Exception as e:
    print(f"[WARN] billing_router import failed: {e}")

try:
    from routers import lab_router
except Exception as e:
    print(f"[WARN] lab_router import failed: {e}")
    lab_router = None
