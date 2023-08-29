from typing import List
from queue import Queue, Empty as EmptyQueue
from .base import DataUnit


def get_all(queue: Queue) -> List[DataUnit]:
    items = []
    while True:
        try:
            item = queue.get_nowait()
        except EmptyQueue:
            break
        else:
            items.append(item)
    return items
