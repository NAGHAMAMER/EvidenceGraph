from typing import Annotated
from uuid import UUID

from fastapi import Header


def get_client_id(
    x_client_id: Annotated[
        UUID,
        Header(
            alias="X-Client-ID",
            description="Anonymous browser identity.",
        ),
    ],
) -> str:
    return str(x_client_id)
