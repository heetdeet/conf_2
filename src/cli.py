import sys
import os

# Добавляем путь к src для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.config import Config, create_default_config
from src.fetcher import CargoAPIFetcher, TestDataFetcher


def main():
    """
    Основная функция CLI приложения
    """
    print("=== Инструмент визуализации графа зависимостей ===")
    print("Этап 2: Сбор данных о зависимостях\n")
    
    try:
        # Проверяем существование конфигурации
        config_path = "config.ini"
        if not os.path.exists(config_path):
            print("Файл конфигурации не найден. Создаем стандартный...")
            create_default_config(config_path)
        
        # Загружаем конфигурацию
        config = Config(config_path)
        settings = config.load_config()
        
        # Выводим параметры (требование этапа 1)
        config.display_config()

        # Получаем зависимости в зависимости от режима
        package_name = settings['package_name']
        
        if settings['test_mode']:
            print(f"\nРежим: ТЕСТИРОВАНИЕ")
            TestDataFetcher.display_test_dependencies(package_name)
        else:
            print(f"\nРежим: ПРОД")
            fetcher = CargoAPIFetcher(config.get_api_url())
            fetcher.display_dependencies(package_name)
        
        print(f"\nЭтап 2 завершен успешно!")
        
    except FileNotFoundError as e:
        print(f"ОШИБКА: {e}")
        print("Убедитесь, что файл config.ini существует в корне проекта")
        sys.exit(1)
    except ValueError as e:
        print(f"ОШИБКА КОНФИГУРАЦИИ: {e}")
        print("Проверьте параметры в файле config.ini")
        sys.exit(1)
    except Exception as e:
        print(f"НЕИЗВЕСТНАЯ ОШИБКА: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()