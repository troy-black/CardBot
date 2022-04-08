import abc
import concurrent.futures
import threading
from typing import Callable, List

from tdb.cardbot import database
from tdb.cardbot import models
from tdb.cardbot import schemas
from tdb.cardbot.crud import job


class JobPool(abc.ABC):
    _lock = threading.Lock()
    _database: database.BaseDatabase

    last_job_id: int = 0

    @classmethod
    @abc.abstractmethod
    def _run(cls, **kwargs):
        pass

    @classmethod
    async def run(cls, **kwargs) -> models.Job:
        """
        Run Job in background process

        :param kwargs: Dict passed to the function as kwargs
        :return: JobDetails
        """
        with cls._database.db_contextmanager() as db:
            if cls._lock.acquire(False):
                details = schemas.JobDetails(job_type=cls.__name__)
                record = job.Job.create(db, details)

                details = schemas.JobDetails(**record.__dict__)

                # TODO - Should this be multiprocessing instead of threading
                #        Must run in background and continue
                thread = threading.Thread(target=cls._run, args=(details,), kwargs=kwargs)
                thread.start()
            else:
                details = job.Job.read_one(db, cls.last_job_id)

        return details


class Thread:
    def __init__(self, function: Callable, results_id: str = None, **kwargs):
        """
        Details for a background thread

        :param function: Function to run in the background
        :param results_id: Key used in ThreadPool.run() results
        :param kwargs: Dict passed to the function as kwargs
        """
        self.function = function
        self.results_id = results_id
        self.kwargs = kwargs


class ThreadPool:
    @classmethod
    def run(cls, threads: List[Thread], thread_prefix: str = 'Thread') -> dict:
        """
        Run a List[Thread] details through ThreadPoolExecutor

        :param threads: List[Thread] details
        :param thread_prefix: Prefix to use in results and logging
        :return: Dict of thread function results keyed by Thread().result_id
        """
        with concurrent.futures.ThreadPoolExecutor(thread_name_prefix=thread_prefix) as executor:
            futures = {}
            for r in range(len(threads)):
                results_id = threads[r].results_id or f'{thread_prefix}_{r}'
                fn = threads[r].function
                futures[executor.submit(fn, **threads[r].kwargs)] = results_id

            results = {}
            for future in concurrent.futures.as_completed(futures):
                results_id = futures[future]
                results[results_id] = future.result()

        return results
