import os
import time
import threading
import argparse
from multiprocessing import Queue, Process
from typing import List, Dict

QUEUE = Queue()


# Функція для пошуку ключових слів у файлі

def search_keywords_in_file(file_path: str, keywords: List[str],
                            results: Dict[str, List[str]]) -> None:
    """Функція для пошуку ключових слів у файлі"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read().lower()
            for keyword in keywords:
                if keyword.lower() in file_content:
                    if keyword not in results:
                        results[keyword] = []
                    results[keyword].append(file_path)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")


def process_files_in_chunk(
        files: List[str],
        keywords: List[str],
        queue: Queue = QUEUE) -> None:
    """Функція для обробки частини файлів в одному процесі"""
    results: Dict[str, List[str]] = {}
    for file_path in files:
        search_keywords_in_file(file_path, keywords, results)

    # Додаємо результати до черги
    queue.put(results)


def process_files_multiprocessing(
        files: List[str], keywords: List[str]) -> Dict[str, List[str]]:
    """Функція для обробки файлів з використанням багатопроцесорного підходу"""
    queue = QUEUE
    available_processes = os.cpu_count() - 2  # Резервуємо 2 процесори
    if available_processes < 1:
        # Якщо залишилось менше 1 процесора, використовуємо хоча б 1 процес
        available_processes = 1

    chunk_size = len(files) // available_processes
    processes = []
    for i in range(available_processes):
        chunk = files[i * chunk_size: (i + 1) * chunk_size] \
            if i < available_processes - 1 else files[i * chunk_size:]
        process = Process(
            target=process_files_in_chunk, args=(chunk, keywords, queue))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    return get_results_from_queue(queue)


# Функція для обробки файлів багатопотоково
def process_files_threaded(
        files: List[str], keywords: List[str]) -> Dict[str, List[str]]:
    """Функція для обробки файлів з використанням багатопотоково підходу"""
    queue = QUEUE  # Використовуємо Queue для збору результатів
    available_threads = os.cpu_count() - 2  # Резервуємо 2 потоки
    if available_threads < 1:
        # Якщо залишилось менше 1 потоку, використовуємо хоча б 1 потік
        available_threads = 1

    # Визначаємо розмір чанку
    chunk_size = len(files) // available_threads or 1
    threads = []

    for i in range(available_threads):
        chunk = files[i * chunk_size: (i + 1) * chunk_size] \
            if i < available_threads - 1 else files[i * chunk_size:]
        thread = threading.Thread(
            target=process_files_in_chunk, args=(chunk, keywords, queue))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return get_results_from_queue(queue)


def get_results_from_queue(queue):
    """Функція для збирання результатів з черги"""
    results: Dict[str, List[str]] = {}
    while not queue.empty():
        partial_result = queue.get()
        for keyword, file_paths in partial_result.items():
            if keyword not in results:
                results[keyword] = []
            results[keyword].extend(file_paths)
    return results


# Основна функція для адаптивного вибору
# між багатопотоковим та багатопроцесорним підходом
def main() -> None:
    # Парсинг аргументів командного рядка
    parser = argparse.ArgumentParser(
        description="Search for keywords in text files.")
    parser.add_argument('directory', type=str,
                        help="Path to the directory containing text files.")
    parser.add_argument('keywords', type=str, nargs='+',
                        help="List of keywords to search for.")
    args = parser.parse_args()

    directory = args.directory
    keywords = args.keywords

    if not os.path.isdir(directory):
        print(f"Error: The directory '{directory}' does not exist.")
        return

    # Отримуємо список текстових файлів у вказаній директорії
    files = [
        os.path.join(directory, f) for f in os.listdir(directory)
        if f.endswith('.txt')
    ]

    if not files:
        print(f"No text files found in directory '{directory}'.")
        return

    start_time = time.time()

    # Оцінка ресурсів та вибір між багатопотоковим і багатопроцесорним підходом
    available_cores = os.cpu_count()  # Кількість доступних ядер
    if available_cores > 2:
        # Якщо є більше 2-х ядер, можна використовувати багатопроцесорність
        print("Using multiprocessing (multi-core) approach...")
        results = process_files_multiprocessing(files, keywords)
    else:  # Якщо лише 2 або менше ядер, використовуємо багатопоточність
        print("Using threading (multi-threading) approach...")
        results = process_files_threaded(files, keywords)

    end_time = time.time()

    print("Results:")
    for keyword, file_paths in results.items():
        print(f"Keyword: '{keyword}' found in files: {file_paths}")

    print(f"Execution time: {end_time - start_time} seconds")


if __name__ == "__main__":
    main()
