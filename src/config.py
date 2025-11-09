import configparser
import os
from typing import Dict, Any


class Config:
    """
    Класс для работы с конфигурацией из INI-файла
    """
    
    def __init__(self, config_path: str = "config.ini"):
        """
        Инициализация конфигурации
        
        Args:
            config_path: путь к файлу конфигурации
        """
        self.config_path = config_path
        # Параметры по умолчанию
        self.settings = {
            'package_name': '',           # имя пакета для анализа
            'repo_url': '',               # URL репозитория
            'test_mode': False,           # режим тестирования
            'output_file': 'graph.svg',   # файл для графа
            'max_depth': -1,              # макс. глубина (-1 = без ограничений)
            'filter_substring': ''        # подстрока для фильтрации
        }
    
    def load_config(self) -> Dict[str, Any]:
        """
        Загрузка и парсинг конфигурационного файла
        
        Returns:
            Словарь с настройками
            
        Raises:
            FileNotFoundError: если файл не найден
            ValueError: если неверный формат или значения
        """
        # Проверяем существование файла
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Файл конфигурации не найден: {self.config_path}")
        
        # Создаем парсер
        parser = configparser.ConfigParser()
        parser.read(self.config_path, encoding='utf-8')
        
        # Проверяем наличие секции [settings]
        if 'settings' not in parser:
            raise ValueError("В файле конфигурации отсутствует секция [settings]")
        
        # Читаем строковые значения
        self.settings['package_name'] = parser.get('settings', 'package_name', fallback='')
        self.settings['repo_url'] = parser.get('settings', 'repo_url', fallback='')
        self.settings['output_file'] = parser.get('settings', 'output_file', fallback='graph.svg')
        self.settings['filter_substring'] = parser.get('settings', 'filter_substring', fallback='')
        
        # Читаем булево значение (режим тестирования)
        test_mode_str = parser.get('settings', 'test_mode', fallback='false').lower()
        self.settings['test_mode'] = test_mode_str in ('true', 'yes', '1', 'on')
        
        # Читаем целочисленное значение (максимальная глубина)
        try:
            self.settings['max_depth'] = parser.getint('settings', 'max_depth', fallback=-1)
        except ValueError:
            raise ValueError("Параметр max_depth должен быть целым числом")
        
        # Валидируем конфигурацию
        self._validate_config()
        
        return self.settings
    
    def _validate_config(self):
        """
        Валидация параметров конфигурации
        
        Raises:
            ValueError: если параметры невалидны
        """
        # Проверяем обязательные поля
        if not self.settings['package_name']:
            raise ValueError("Параметр package_name обязателен")
        
        # URL репозитория обязателен, если не в режиме тестирования
        if not self.settings['repo_url'] and not self.settings['test_mode']:
            raise ValueError("Параметр repo_url обязателен, когда test_mode=false")
        
        # Проверяем корректность максимальной глубины
        if self.settings['max_depth'] < -1:
            raise ValueError("max_depth должен быть -1 (без ограничений) или положительным числом")
        
        # Проверяем расширение выходного файла
        if not self.settings['output_file'].endswith(('.svg', '.png', '.jpg')):
            print("Предупреждение: выходной файл рекомендуется сохранять в формате SVG, PNG или JPG")
    
    def display_config(self):
        """
        Вывод всех параметров конфигурации в формате ключ-значение
        (требование этапа 1)
        """
        print("Параметры конфигурации:")
        print("=" * 40)
        
        # Выводим все параметры в читаемом формате
        for key, value in self.settings.items():
            # Форматируем булевы значения для лучшей читаемости
            if isinstance(value, bool):
                display_value = "да" if value else "нет"
            else:
                display_value = value
            print(f"{key:20} : {display_value}")
        
        print("=" * 40)


def create_default_config(config_path: str = "config.ini"):
    """
    Создание файла конфигурации с настройками по умолчанию
    
    Args:
        config_path: путь для сохранения конфигурации
    """
    config = configparser.ConfigParser()
    
    # Секция с настройками
    config['settings'] = {
        'package_name': 'serde',
        'repo_url': 'https://crates.io/api/v1/crates',
        'test_mode': 'false',
        'output_file': 'graph.svg',
        'max_depth': '5',
        'filter_substring': 'test'
    }
    
    # Сохраняем конфигурацию
    with open(config_path, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    
    print(f"Создан файл конфигурации: {config_path}")