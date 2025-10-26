#  -----------------------------------------------------------------------------
#  Copyright (c) 2024 Bud Ecosystem Inc.
#  #
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  #
#      http://www.apache.org/licenses/LICENSE-2.0
#  #
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#  -----------------------------------------------------------------------------

"""The main entry point for the application, initializing the FastAPI app and setting up the application's lifespan management, including configuration and secret syncs."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from budmicroframe.main import configure_app
from budmicroframe.shared.dapr_workflow import DaprWorkflow
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth.routes import auth_router
from .commons.config import app_settings, secrets_settings
from .commons.exceptions import SeederException
from .engine.routes import engine_router
from .eval.routes import eval_router
from .guardrails.routes import guardrail_router
from .license.routes import license_router
from .model.routes import model_router
from .provider.routes import provider_router
from .seeders import seeders


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage the lifespan of the FastAPI application, including scheduling periodic syncs of configurations and secrets.

    This context manager starts a background task that periodically syncs configurations and secrets from
    their respective stores if they are configured. The sync intervals are randomized between 90% and 100%
    of the maximum sync interval specified in the application settings. The task is canceled upon exiting the
    context.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: Yields control back to the context where the lifespan management is performed.
    """
    # task = asyncio.create_task(schedule_secrets_and_config_sync())

    # Only run seeders if enabled via environment variable
    if app_settings.run_seeders_on_startup:
        logger.info("Running database seeders on startup...")
        for seeder_name, seeder in seeders.items():
            try:
                await seeder().seed()  # type: ignore[abstract]
                logger.info(f"Seeded {seeder_name} seeder successfully.")
            except SeederException as e:
                logger.error("Failed to seed %s. Error: %s", seeder_name, e.message)
            except Exception as e:
                logger.error(f"Failed to seed {seeder_name}. Error: {e}")
    else:
        logger.info("Skipping database seeders (RUN_SEEDERS_ON_STARTUP=false)")

    yield

    # NOTE: Config and secrets sync task is currently disabled
    # try:
    #     task.cancel()
    # except asyncio.CancelledError:
    #     logger.exception("Failed to cleanup config & store sync.")

    DaprWorkflow().shutdown_workflow_runtime()


# mypy: ignore-errors
app = configure_app(app_settings, secrets_settings, lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3004", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(engine_router)
app.include_router(eval_router)
app.include_router(license_router)
app.include_router(model_router)
app.include_router(guardrail_router)
app.include_router(provider_router)
