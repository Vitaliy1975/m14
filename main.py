from src.routes import contacts,auth,users
import redis.asyncio as redis
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from src.conf.config import settings
from fastapi.middleware.cors import CORSMiddleware


# Create a FastAPI instance
app = FastAPI()

# Define allowed origins for CORS
origins = ["*"]

# Add CORS middleware to enable cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for different API endpoints
app.include_router(contacts.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(users.router,prefix="/api")

# Define an event handler to initialize Redis and FastAPI limiter on startup
@app.on_event("startup")
async def startup():
    """
    This function is called when the FastAPI application starts.
    It initializes a Redis connection and sets up the FastAPI limiter.
    """
    # Connect to Redis
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",decode_responses=True)

    # Initialize the FastAPI limiter using the Redis connection
    await FastAPILimiter.init(r)

# Define a GET endpoint for the root path
@app.get("/")
def read_root():
    """
    This endpoint returns a simple message "Hello World" when accessed.
    """
    return {"message": "Hello World"}
