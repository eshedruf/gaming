import hashlib
import multiprocessing
import time

class Client:
    def __init__(self, target_md5, range_start, range_end):
        """
        Initializes the Client with the target MD5 hash and the search range.
        """
        self.target_md5 = target_md5
        self.range_start = range_start
        self.range_end = range_end
        self.cpu_count = multiprocessing.cpu_count()

    @staticmethod
    def compute_md5_and_check(start, end, target_hash):
        """
        Computes MD5 hashes for numbers in the range [start, end).
        Returns (True, number) if target_hash is found, otherwise (False, -1).
        """
        for num in range(start, end):
            num_hash = hashlib.md5(str(num).encode()).hexdigest()
            if num_hash == target_hash:
                return True, num
        return False, -1

    def find_md5_hash_in_range(self):
        """
        Splits the range across available CPU cores and checks for the target MD5 hash.
        """
        step = (self.range_end - self.range_start) // self.cpu_count
        ranges = [
            (self.range_start + i * step, self.range_start + (i + 1) * step)
            for i in range(self.cpu_count)
        ]
        # Ensure the last range ends at 'self.range_end'
        ranges[-1] = (ranges[-1][0], self.range_end)

        # Use multiprocessing pool to parallelize the work
        with multiprocessing.Pool(self.cpu_count) as pool:
            results = pool.starmap(
                self.compute_md5_and_check, [(r[0], r[1], self.target_md5) for r in ranges]
            )

        # Check results for a successful match
        for is_found, num in results:
            if is_found:
                return True, num
        return False, -1

    def run(self):
        """
        Runs the search process and prints the result with the elapsed time.
        """
        print("Starting search...")
        start_time = time.time()

        found, number = self.find_md5_hash_in_range()

        end_time = time.time()
        elapsed_time = end_time - start_time

        if found:
            print(f"Hash found! The number is: {number}")
        else:
            print("Hash not found in the range.")
        print(f"Search completed in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    target_md5 = input("Enter the target MD5 hash: ").strip()
    range_start = 1_000_000_000_000
    range_end = range_start + 5_000_000

    client = Client(target_md5, range_start, range_end)
    client.run()
