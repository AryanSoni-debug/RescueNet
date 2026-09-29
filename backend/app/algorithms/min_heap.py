class MinHeap:
    """
    Simple binary Min Heap.

    Stores items as:
        (priority, value)

    The item with the smallest priority is always
    available through peek() / pop().
    """

    def __init__(self):
        self.heap = []

    def is_empty(self):
        return len(self.heap) == 0

    def push(self, priority, value):
        """Insert an item into the heap."""
        self.heap.append((priority, value))
        self._bubble_up(len(self.heap) - 1)

    def pop(self):
        """Remove and return the item with the smallest priority."""
        if self.is_empty():
            raise IndexError("pop from empty MinHeap")

        if len(self.heap) == 1:
            return self.heap.pop()

        minimum = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._bubble_down(0)

        return minimum

    def peek(self):
        """Return the smallest item without removing it."""
        if self.is_empty():
            raise IndexError("peek from empty MinHeap")

        return self.heap[0]

    def _bubble_up(self, index):
        while index > 0:
            parent = (index - 1) // 2

            if self.heap[parent][0] <= self.heap[index][0]:
                break

            self.heap[parent], self.heap[index] = (
                self.heap[index],
                self.heap[parent],
            )

            index = parent

    def _bubble_down(self, index):
        size = len(self.heap)

        while True:
            left = 2 * index + 1
            right = 2 * index + 2
            smallest = index

            if (
                left < size
                and self.heap[left][0] < self.heap[smallest][0]
            ):
                smallest = left

            if (
                right < size
                and self.heap[right][0] < self.heap[smallest][0]
            ):
                smallest = right

            if smallest == index:
                break

            self.heap[index], self.heap[smallest] = (
                self.heap[smallest],
                self.heap[index],
            )

            index = smallest

    def __len__(self):
        return len(self.heap)