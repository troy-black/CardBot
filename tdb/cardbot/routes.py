from fastapi import APIRouter
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates


class BaseRoutes:
    router = APIRouter()

    templates: Jinja2Templates  # (directory=str(Path(str(Path(__file__).parent), 'templates')))

    @staticmethod
    @router.get('/')
    async def docs_redirect():
        return RedirectResponse(url='/docs')
