import multiprocessing as mp

print(f"Pool from: {mp.Pool.__module__}")
print(f"Pool class: {mp.Pool}")

def dummy_task(_):
    return "Done"

if __name__ == '__main__':
    with mp.Pool(processes=2) as pool:
        results = pool.map(dummy_task, range(2))
        print(results)
