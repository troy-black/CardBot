import threading
from abc import ABC, abstractmethod

from tdb.cardbot.core import models
from tdb.cardbot.core.crud.job import Job
from tdb.cardbot.core.database import Database
from tdb.cardbot.core.schemas import JobDetails


class JobPool(ABC):
    _lock = threading.Lock()

    last_job_id: int = 0

    @classmethod
    @abstractmethod
    def _run(cls, **kwargs):
        pass

    @classmethod
    async def run(cls, **kwargs) -> models.Job:
        """
        Run Job in background process

        :param kwargs: Dict passed to the function as kwargs
        :return: JobDetails
        """
        with Database.db_contextmanager() as db:
            if cls._lock.acquire(False):
                details = JobDetails(job_type=cls.__name__)
                record = Job.create(db, details)

                details = JobDetails(**record.__dict__)

                # TODO - Should this be multiprocessing instead of threading
                #        Must run in background and continue
                thread = threading.Thread(target=cls._run, args=(details,), kwargs=kwargs)
                thread.start()
            else:
                details = Job.read_one(db, cls.last_job_id)

        return details
