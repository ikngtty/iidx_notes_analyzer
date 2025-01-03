import time
from typing import Any, Callable, TypeGuard

# TODO: `is_list_of_T`みたいにTを指定して使える汎用的な関数にしたい
def is_list_of_list(l: list) -> TypeGuard[list[list]]:
    return all(isinstance(item, list) for item in l)

def is_list_of_dict(l: list) -> TypeGuard[list[dict]]:
    return all(isinstance(item, dict) for item in l)

def is_list_of_str_dict(l: list[dict]) -> TypeGuard[list[dict[str, Any]]]:
    return all(
        all(isinstance(key, str) for key in item)
        for item in l
    )

class CoolExecutor:
    wait_begun: Callable[[], None] | None
    wait_ended: Callable[[], None] | None
    _cool_time_sec: float
    _last_executed: float | None

    def __init__(self, cool_time_sec: float) -> None:
        if cool_time_sec < 0:
            raise ValueError(cool_time_sec)

        self.wait_begun = None
        self.wait_ended = None
        self._cool_time_sec = cool_time_sec
        self._last_executed = None

    def __call__[T](self, call: Callable[[], T]) -> T:
        if self._last_executed is not None:
            elasped = time.time() - self._last_executed
            if elasped < self._cool_time_sec:
                if self.wait_begun:
                    self.wait_begun()
                time.sleep(self._cool_time_sec - elasped)
                if self.wait_ended:
                    self.wait_ended()

        result = call()
        self._last_executed = time.time()
        return result
