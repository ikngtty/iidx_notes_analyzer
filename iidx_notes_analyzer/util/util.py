from contextlib import contextmanager
import os
import shutil
import tempfile
import time
from typing import Any, Callable, IO, Iterator, TypeGuard

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

@contextmanager
def make_file_atomically(file_path: str) -> Iterator[IO[str]]:
    """
    完全性が保証されたファイル書き込み。
    書き込み中にエラーが起きた場合、ファイルの作成自体を取りやめるので、
    中途半端なファイルが残ることがない。

    具体的には、一時ファイルを作成して書き込み、無事完了したらリネームしている。
    """

    file_name = os.path.basename(file_path)

    temp_prefix = file_name + '.'
    temp_suffix = '.tmp'

    # 一時ファイルは本来の保存先と同じディレクトリにする。
    temp_dir = os.path.dirname(file_path)

    with tempfile.NamedTemporaryFile(
        mode='w', dir=temp_dir, delete=True,
        prefix=temp_prefix, suffix=temp_suffix,
    ) as temp_file:

        yield temp_file

        temp_file.flush()
        os.fsync(temp_file.fileno())

        shutil.move(temp_file.name, file_path)

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
