from threading import Thread, Lock


class Job(Thread):
    """Represents a simple thread-based job."""

    type = None
    lock = None

    def __init__(self, job_type, lock, target, args=(), kwargs=None):
        """
        Creates a simple thread-based job.

        The arguments target, args, and kwargs are the same as they would be
        for threading.Thread

        Parameters
        ----------
        type : str (required)
            Type of Job as a string.
        lock : Lock (required)
            Some object with an interface equivalent to threading.Lock
        target : func (required)
            A callable object run by the job.
        args : List (optional)
            A list or tuple of arguments passed to the target function.
        kwargs : Dict (optional)
            A dictionary of keyword arguments passed to the target function.
        """
        if kwargs is None:
            kwargs = {}
        super().__init__(target=target, args=args, kwargs=kwargs)
        self.type = job_type
        self.lock = lock

    def run(self):
        """Gain lock and run."""
        with self.lock:
            super().run()


class JobManager:
    """Manages the Locks that control Jobs."""

    locks = {}

    def __init__(self, locks=None):
        """Create object with optional default dictionary mapping names to Locks."""
        if locks is None:
            locks = {}
        self.locks = locks

    def make_and_register(
        self,
        job_type,
        target,
        args=(),
        kwargs=None,
        allow_queue=True,
        populate_new_type=True,
        strict=False,
    ):
        """
        Create and register a Job by specifying target and keywords.

        This function automatically handles the management of Lock objects.
        The new Job is started/queued after it is created.

        Parameters
        ----------
        type : str
            Type of job to be added as a string.
        target : func
            Callable function for the new job.
        args : List
            List of arguments for the callable target.
        kwargs : Dict
            Dictionary of keyword arguments for the callable target.
        allow_queue : bool
            If type already exists and the Lock for that type is aquired,
            determines if the new job will be queued to run after the old one.
        populate_new_type : bool
            If the type does not already exist, determines if we will add it.
        strict : bool
            Determines if the behavior from allow_queue and populate_new_type will
            additionally raise a ValueError instead of failing silently.
        """
        if kwargs is None:
            kwargs = {}
        if type not in self.locks:
            if not populate_new_type:
                if strict:
                    raise ValueError(
                        f"Attempted to add new {type} Job when not permitted"
                    )
                return  # Silent failure
            self.locks[type] = Lock()
        if self.locks[type].locked() and not allow_queue:
            if strict:
                raise ValueError(
                    f"Attempted to queue a new {type} Job when not permitted"
                )
            return  # Silent failure
        job = Job(job_type, self.locks[type], target, args, kwargs)
        job.start()

    def register(self, job, merge=False, allow_queue=True, strict=True):
        """
        Register a new instance of a Job class.

        Newly registered Jobs are automatically started/queued.
        If merge is False and this manager already has a job of job.type,
        the new job will not be registered.
        Creates a new Lock if job.lock is None.

        Parameters
        ----------
        job : Job
            An instance of a Job class.
        merge : bool
            Determines if job.type will be merged into already known jobs of that type.
            Can fail silently if strict is False.
        allow_queue : bool
            If merging with known jobs and the Lock for that type is aquired, determine
            if we will still queue the new job after the old one.
            Will throw exception if strict is True.
        strict : bool
            Determines if this function will choose to throw exceptions.
        """
        if job.type in self.locks:
            if not merge:
                if strict:
                    raise ValueError(
                        f"Registering more {job.type} Jobs is not permitted"
                    )
                return  # Silent failure
            if self.locks[type].locked() and not allow_queue:
                if strict:
                    raise ValueError(
                        f"Attempted to queue a new {type} Job when not permitted"
                    )
                return  # Silent failure
            job.lock = self.locks[type]
            job.start()
            return
        if job.lock is None:
            job.lock = Lock()
        self.locks[type] = job.lock
        job.start()
