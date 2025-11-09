import sys
import os

# Добавляем путь к src для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.config import Config, create_default_config


def main():
    """
    Основная функция CLI приложения
    """
    print("=== Инструмент визуализации графа зависимостей ===")
    print("Этап 1: Минимальный прототип с конфигурацией\n")
    
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
        
        # Демонстрация работы приложения
        print(f"\nГотов к анализу пакета: {settings['package_name']}")
        
        if settings['test_mode']:
            print("Режим: ТЕСТИРОВАНИЕ (используются локальные данные)")
        else:
            print(f"Режим: ПРОД (данные из: {settings['repo_url']})")
        
        print(f"Макс. глубина анализа: {settings['max_depth'] if settings['max_depth'] != -1 else 'без ограничений'}")
        
        if settings['filter_substring']:
            print(f"Фильтрация пакетов: исключаются пакеты содержащие '{settings['filter_substring']}'")
        
        print(f"Результат будет сохранен в: {settings['output_file']}")
        
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