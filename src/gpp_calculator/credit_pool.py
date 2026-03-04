class CreditPool:
    def __init__(self, capacity: int, cate_names: list[str]):
        if capacity < 0:
            raise ValueError("Capacity must be a non-negative integer.")
        self._credits = 0
        self._capacity = capacity
        self._cate_names = cate_names

    def credits(self) -> int:
        return self._credits

    def add_credits(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Cannot add negative credits.")

        if self._credits + amount > self._capacity:
            self._credits = self._capacity
            surplus_credits = amount - (self._capacity - self._credits)
        else:
            self._credits += amount
            surplus_credits = 0
        return surplus_credits

    def use_credits(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Cannot use negative credits.")
        if amount > self._credits:
            returned_credits = self._credits
            self._credits = 0
        else:
            returned_credits = amount
            self._credits -= amount
        return returned_credits

    def get_category_names(self) -> list[str]:
        return self._cate_names