class PriorityQueue:
    """
    Min-priority queue for RescueNet.

    Smaller priority value = higher priority.

    The AllocationEngine expects:
        enqueue(priority, value)
        dequeue()

    Internally this uses a binary min-heap.
    """

    def __init__(self):
        self._heap = []

    def is_empty(self):
        return len(self._heap) == 0

    def __len__(self):
        return len(self._heap)

    def enqueue(self, priority, value):
        """Add an item to the priority queue."""
        self._heap.append((priority, value))
        self._bubble_up(len(self._heap) - 1)

    def dequeue(self):
        """Remove and return the item with the smallest priority."""

        if self.is_empty():
            raise IndexError("dequeue from empty PriorityQueue")

        if len(self._heap) == 1:
            return self._heap.pop()

        minimum = self._heap[0]

        self._heap[0] = self._heap.pop()

        self._bubble_down(0)

        return minimum

    def peek(self):
        """Return the smallest-priority item without removing it."""

        if self.is_empty():
            raise IndexError("peek from empty PriorityQueue")

        return self._heap[0]

    def _bubble_up(self, index):
        while index > 0:

            parent = (index - 1) // 2

            if self._heap[parent][0] <= self._heap[index][0]:
                break

            self._heap[parent], self._heap[index] = (
                self._heap[index],
                self._heap[parent],
            )

            index = parent

    def _bubble_down(self, index):
        size = len(self._heap)

        while True:

            left = 2 * index + 1
            right = 2 * index + 2

            smallest = index

            if (
                left < size
                and self._heap[left][0] < self._heap[smallest][0]
            ):
                smallest = left

            if (
                right < size
                and self._heap[right][0] < self._heap[smallest][0]
            ):
                smallest = right

            if smallest == index:
                break

            self._heap[index], self._heap[smallest] = (
                self._heap[smallest],
                self._heap[index],
            )

            index = smallest