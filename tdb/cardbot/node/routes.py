import asyncio
import http
import pathlib
from typing import Union, List

import fastapi
import requests
from sqlalchemy import orm
from starlette import responses, templating

from tdb.cardbot import image, routes, node, schemas as base_schemas
from tdb.cardbot.node import camera, config, gpio, database, schemas
from tdb.cardbot.node.crud import scans

templates = templating.Jinja2Templates(directory=str(pathlib.Path(str(pathlib.Path(__file__).parent), 'templates')))


class Routes(routes.BaseRoutes):
    router = fastapi.APIRouter()

    loop: asyncio.AbstractEventLoop
    event: asyncio.Event
    image_store: image.ImageStore

    @staticmethod
    @router.get('/z/{steps}', response_model=int)
    def move_head(steps: int):
        return gpio.Gpio.z_stepper.step(steps)

    @staticmethod
    @router.get('/x/{steps}', response_model=int)
    def move_x(steps: int):
        return gpio.Gpio.x_stepper.step(steps)

    @staticmethod
    @router.get('/input/{steps}', response_model=int)
    def move_new(steps: int):
        return gpio.Gpio.input_stepper.step(steps)

    @staticmethod
    @router.get('/output/{steps}', response_model=int)
    def move_sorted(steps: int):
        return gpio.Gpio.output_stepper.step(steps)

    @staticmethod
    @router.get('/vacuum/{on}', response_model=bool)
    def vacuum(on: bool):
        return gpio.Gpio.vacuum_pump.change(on)

    @staticmethod
    @router.get('/setup')
    async def setup():
        return gpio.Gpio.setup()

    @staticmethod
    @router.get('/loop')
    async def loop():
        return gpio.Gpio.loop()

    @staticmethod
    @router.get("/process/image/last")
    async def last_process_image():
        print()
        img = await node.Indexer.get_event_image(Routes.event, Routes.image_store)
        return routes.BaseRoutes.return_pillow_image_as_png(img)

    @staticmethod
    @router.get('/preview/{on}', response_model=bool)
    def preview(on: bool):
        if on:
            camera.PiCameraDriver.camera.start_preview()
        else:
            camera.PiCameraDriver.camera.stop_preview()

        return on

    @staticmethod
    @router.get('/prop/{prop}/{val}', response_model=bool)
    def prop_change(prop: str, val: Union[int, str]):
        if hasattr(camera.PiCameraDriver.camera, prop):
            setattr(camera.PiCameraDriver.camera, prop, val)
            return True

        return False

    @staticmethod
    @router.get('/capture/new')
    def capture_new():
        return responses.Response(camera.PiCameraDriver.capture(), media_type='image/jpeg')

    @staticmethod
    @router.get('/capture')
    def capture():
        if camera.PiCameraDriver.last_image_bytes:
            return responses.Response(camera.PiCameraDriver.last_image_bytes, media_type='image/jpeg')

        return responses.Response(camera.PiCameraDriver.capture(), media_type='image/jpeg')

    @staticmethod
    @router.get('/indexer')
    async def get_indexer(request: fastapi.Request):
        return templates.TemplateResponse('indexer.html', {'request': request})

    @staticmethod
    @router.get('/reviewer')
    async def get_reviewer(request: fastapi.Request, db: orm.Session = fastapi.Depends(database.Database.get_db)):
        rows = scans.CardScan.read_stack_names(db)

        return templates.TemplateResponse(
            'reviewer.html',
            {
                'request': request,
                'stackNames': [
                    row[0]
                    for row in rows
                ]
            }
        )

    # @staticmethod
    # @router.get("/scan/{stack_name}/count", response_model=int)
    # async def get_index_count_by_stack(stack_name: str, db: orm.Session = fastapi.Depends(database.Database.get_db)):
    #     row = scans.CardScan.read_last_index_by_stack(db, stack_name)
    #
    #     return row[0]

    @staticmethod
    @router.get("/scan/{stack_name}/indexes", response_model=List[str])
    async def get_indexes_by_stack(stack_name: str, db: orm.Session = fastapi.Depends(database.Database.get_db)):
        rows = scans.CardScan.read_indexes_by_stack(db, stack_name)

        return [
            row[0]
            for row in rows
        ]

    @staticmethod
    @router.get('/start/index/{stack_name}/{language}/{foil}/{proxy}/{altered}',
                status_code=http.HTTPStatus.ACCEPTED, response_model=base_schemas.JobDetails)
    async def start_indexing(stack_name: str, language: str,
                             foil: bool, proxy: bool, altered: bool) -> base_schemas.JobDetails:
        Routes.loop = asyncio.get_running_loop()
        Routes.event = asyncio.Event(loop=Routes.loop)
        Routes.image_store = image.ImageStore()

        return await node.Indexer.run(
            stack_name=stack_name,
            language=language,
            foil=foil,
            proxy=proxy,
            altered=altered,
            event=Routes.event,
            image_store=Routes.image_store
        )

    @staticmethod
    @router.get("/scan/{stack_name}/{stack_index}/", response_model=schemas.CardScanDetails)
    async def get_scan_by_stack(stack_name: str, stack_index: int,
                                db: orm.Session = fastapi.Depends(database.Database.get_db)):
        scan = scans.CardScan.read_one_by_stack(db, stack_name, stack_index)

        if not scan:
            raise fastapi.HTTPException(status_code=404, detail="Card not found")

        return scan

    @staticmethod
    @router.get("/details/{stack_name}/{stack_index}/", response_model=schemas.CardScanDetails)
    async def get_details_by_stack(stack_name: str, stack_index: int,
                                   db: orm.Session = fastapi.Depends(database.Database.get_db)):
        ...

    @staticmethod
    @router.put("/scan/{stack_name}/{stack_index}/{card_id}", response_model=schemas.CardScanDetails)
    async def put_scan_by_stack_update(stack_name: str, stack_index: int, card_id: str,
                                       db: orm.Session = fastapi.Depends(database.Database.get_db)):

        scan = scans.CardScan.read_one_by_stack(db, stack_name, stack_index)

        if not scan:
            raise fastapi.HTTPException(status_code=404, detail="Card not found")

        scan.card_id = card_id
        db.commit()

        return scan

    @staticmethod
    @router.get("/scan/{stack_name}/{stack_index}/processed")
    async def get_scan_image(stack_name: str, stack_index: int):
        filepath = pathlib.Path(config.NodeConfig.image_path, stack_name, f'processed_{stack_index:03}.jpg')
        img = image.Image(filepath)

        return Routes.return_pillow_image_as_png(img.modified_image)

    @staticmethod
    @router.get("/card/{card_id}/image")
    async def get_card_image_by_id(card_id: str):
        response = requests.get(f'{config.NodeConfig.core_url}/card/{card_id}/image')

        return responses.Response(response.content, media_type='image/png')
