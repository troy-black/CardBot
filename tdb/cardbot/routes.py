import io

import fastapi
from starlette import responses, templating


class BaseRoutes:
    router = fastapi.APIRouter()

    templates: templating.Jinja2Templates  # (directory=str(Path(str(Path(__file__).parent), 'templates')))

    @staticmethod
    @router.get("/")
    async def docs_redirect():
        return responses.RedirectResponse(url="/docs")

    @staticmethod
    def pillow_image_as_bytes(pillow_image, save_format: str = "PNG") -> bytes:
        stream = io.BytesIO()

        pillow_image.save(stream, format=save_format)

        stream.seek(0)
        read = stream.read()
        return read

    @staticmethod
    def return_pillow_image_as_png(pillow_image):
        return responses.Response(
            BaseRoutes.pillow_image_as_bytes(pillow_image), media_type="image/png"
        )
