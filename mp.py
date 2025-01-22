import hashlib
import multiprocessing


class Multiprocessing:
    def __init__(self):
        self.range_start = 3
        self.range_end = 6
        self.cpu_count = multiprocessing.cpu_count()
        self.target_md5 = "g"

    def compute_md5_and_check(self, start, end, target_hash):
        for num in range(start, end):
            num_hash = hashlib.md5(str(num).encode()).hexdigest()
            if num_hash == target_hash:
                return True, num
        return False, -1

    def find_md5_hash_in_range(self):
        print(self.range_start, )
        step = max(1, (self.range_end - self.range_start) // self.cpu_count)
        ranges = [
            (self.range_start + i * step, self.range_start + (i + 1) * step)
            for i in range(self.cpu_count)
        ]
        ranges[-1] = (ranges[-1][0], self.range_end)
        with multiprocessing.Pool(self.cpu_count) as pool:
            results = pool.starmap(
                self.compute_md5_and_check, [(r[0], r[1], self.target_md5) for r in ranges]
            )
        # Check results for a successful match
        for is_found, num in results:
            if is_found:
                self.finish = True
                return True, num
        return False, -1