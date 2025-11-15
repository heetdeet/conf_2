import sys
import os

# Добавляем путь к src для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.config import Config, create_default_config
from src.fetcher import CargoAPIFetcher, TestDataFetcher
from src.graph import DependencyGraph, TestGraphBuilder


def main():
    """
    Основная функция CLI приложения
    """
    print("=== Инструмент визуализации графа зависимостей ===")
    print("Этап 3: Основные операции над графом зависимостей\n")
    
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

        # создаем граф
        dependency_graph = DependencyGraph()

        # Получаем зависимости в зависимости от режима
        package_name = settings['package_name']
        
        if settings['test_mode']:
            print(f"\nРежим: ТЕСТИРОВАНИЕ")
            
            # демонстрация тестового графа
            print("\n" + "="*50)
            print("ДЕМОНСТРАЦИЯ АЛГОРИТМОВ НА ТЕСТОВОМ ГРАФЕ")
            print("="*50)
            TestGraphBuilder.display_test_graph()
            
            # построение графа для указанного пакета
            print(f"\nПОСТРОЕНИЕ ГРАФА ДЛЯ '{package_name}':")
            fetcher = TestDataFetcher()
            graph = dependency_graph.build_dependency_graph(
                fetcher, 
                package_name,
                max_depth=settings['max_depth'],
                filter_substring=settings['filter_substring']
            )
            dependency_graph.display_graph()
            
        else:
            print(f"\nРежим: ПРОД")
            fetcher = CargoAPIFetcher(config.get_api_url())
            
            # сначала покажем прямые зависимости (этап 2)
            fetcher.display_dependencies(package_name)
            
            # затем построим полный граф (этап 3)
            print(f"\nПОСТРОЕНИЕ ПОЛНОГО ГРАФА ЗАВИСИМОСТЕЙ:")
            graph = dependency_graph.build_dependency_graph(
                fetcher, 
                package_name,
                max_depth=settings['max_depth'],
                filter_substring=settings['filter_substring']
            )
            dependency_graph.display_graph()
        
        print(f"\nЭтап 3 завершен успешно!")
        
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