import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api.routes.general_purpose_assistant import general_purpose_assistant_router

app = FastAPI(
    # docs_url=None,
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(meta_router)
app.include_router(general_purpose_assistant_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8012)