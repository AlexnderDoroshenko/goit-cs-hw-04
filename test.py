import unittest
import os
from tempfile import TemporaryDirectory
from typing import Dict, List

from adaptive_processing import (
    search_keywords_in_file,
    process_files_threaded,
    process_files_multiprocessing
)


class TestFileSearch(unittest.TestCase):

    def setUp(self) -> None:
        """Створення тимчасової директорії та файлів для тестів"""
        self.test_dir = TemporaryDirectory()
        self.files = []
        self.search_keywords = ['python', 'data', 'openai']

        # Створення тестових файлів
        for i in range(3):
            file_name = f"test_file_{i}.txt"
            file_path = os.path.join(self.test_dir.name, file_name)
            with open(file_path, 'w', encoding='utf-8') as f:
                if i == 0:
                    f.write("This is a Python test file with data and openai.")
                elif i == 1:
                    f.write("This file is about Python programming.")
                else:
                    f.write("OpenAI is a company that works with data.")
            self.files.append(file_path)

    def tearDown(self) -> None:
        """Очищення тимчасової директорії після тестів"""
        self.test_dir.cleanup()

    def test_search_keywords_in_file(self) -> None:
        """Тестуємо пошук ключових слів у файлах"""
        results: Dict[str, List[str]] = {}

        # Пошук по першому файлу
        search_keywords_in_file(self.files[0], self.search_keywords, results)
        self.assertIn('python', results)
        self.assertIn('data', results)
        self.assertIn('openai', results)

    def test_process_files_threaded(self) -> None:
        """Тестуємо багатопотокову обробку файлів"""
        results: Dict[str, List[str]] = process_files_threaded(
            self.files, self.search_keywords)

        # Перевірка, що ключові слова знайдено в результатах
        self.assertIn('python', results)
        self.assertIn('data', results)
        self.assertIn('openai', results)

        # Перевірка на наявність правильних шляхів до файлів
        self.assertTrue(any(file in results['python'] for file in self.files))
        self.assertTrue(any(file in results['data'] for file in self.files))
        self.assertTrue(any(file in results['openai'] for file in self.files))

    def test_process_files_multiprocessing(self) -> None:
        """Тестуємо багатопроцесорну обробку файлів"""
        results: Dict[str, List[str]] = process_files_multiprocessing(
            self.files, self.search_keywords)

        # Перевірка, що ключові слова знайдено в результатах
        self.assertIn('python', results)
        self.assertIn('data', results)
        self.assertIn('openai', results)

        # Перевірка на наявність правильних шляхів до файлів
        self.assertTrue(any(file in results['python'] for file in self.files))
        self.assertTrue(any(file in results['data'] for file in self.files))
        self.assertTrue(any(file in results['openai'] for file in self.files))


if __name__ == "__main__":
    unittest.main()
