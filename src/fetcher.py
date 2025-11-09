import requests
import json
from typing import List, Dict, Any
from urllib.parse import urljoin


class CargoAPIFetcher:
    """
    Класс для получения данных о зависимостях из Cargo API
    """
    
    def __init__(self, base_url: str = "https://crates.io"):
        """
        Инициализация API клиента
        
        Args:
            base_url: базовый URL Cargo API
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        # Устанавливаем заголовки для вежливого scraping
        self.session.headers.update({
            'User-Agent': 'DependencyVisualizer/1.0 (educational project)',
            'Accept': 'application/json'
        })
    
    def get_package_info(self, package_name: str) -> Dict[str, Any]:
        """
        Получает основную информацию о пакете
        
        Args:
            package_name: имя пакета (например, 'serde')
            
        Returns:
            Словарь с информацией о пакете
            
        Raises:
            requests.RequestException: при ошибках сети
            ValueError: если пакет не найден или неверный ответ
        """
        url = f"{self.base_url}/api/v1/crates/{package_name}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()  # Проверяем HTTP ошибки
            
            data = response.json()
            
            # Проверяем структуру ответа
            if 'crate' not in data:
                raise ValueError(f"Неверный формат ответа для пакета {package_name}")
                
            return data
            
        except requests.exceptions.Timeout:
            raise requests.RequestException(f"Таймаут при запросе к {url}")
        except requests.exceptions.ConnectionError:
            raise requests.RequestException(f"Ошибка соединения с {url}")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise ValueError(f"Пакет не найден: {package_name}")
            else:
                raise requests.RequestException(f"HTTP ошибка {response.status_code}: {e}")
        except json.JSONDecodeError:
            raise ValueError(f"Неверный JSON в ответе от API для {package_name}")
    
    def get_latest_version(self, package_info: Dict[str, Any]) -> str:
        """
        Извлекает последнюю версию пакета из информации о пакете
        
        Args:
            package_info: информация о пакете из get_package_info()
            
        Returns:
            Номер последней версии (например, '1.0.197')
        """
        crate_data = package_info.get('crate', {})
        latest_version = crate_data.get('max_version')
        
        if not latest_version:
            raise ValueError("Не удалось определить последнюю версию пакета")
            
        return latest_version
    
    def get_dependencies(self, package_name: str, version: str) -> List[Dict[str, Any]]:
        """
        Получает зависимости для конкретной версии пакета
        
        Args:
            package_name: имя пакета
            version: версия пакета
            
        Returns:
            Список зависимостей
            
        Raises:
            requests.RequestException: при ошибках сети
            ValueError: если зависимости не найдены
        """
        url = f"{self.base_url}/api/v1/crates/{package_name}/{version}/dependencies"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Проверяем структуру ответа
            if 'dependencies' not in data:
                raise ValueError(f"Неверный формат ответа для зависимостей {package_name} {version}")
                
            return data['dependencies']
            
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"Ошибка при получении зависимостей: {e}")
        except json.JSONDecodeError:
            raise ValueError(f"Неверный JSON в ответе для зависимостей {package_name}")
    
    def get_direct_dependencies(self, package_name: str) -> List[str]:
        """
        Получает прямые зависимости пакета (основная функция для этапа 2)
        
        Args:
            package_name: имя пакета для анализа
            
        Returns:
            Список имен прямых зависимостей
            
        Raises:
            Exception: при любых ошибках получения данных
        """
        print(f"Получение информации о пакете: {package_name}")
        
        # Получаем информацию о пакете
        package_info = self.get_package_info(package_name)
        
        # Извлекаем последнюю версию
        latest_version = self.get_latest_version(package_info)
        print(f"Последняя версия: {latest_version}")
        
        # Получаем зависимости
        dependencies = self.get_dependencies(package_name, latest_version)
        
        # Извлекаем только имена пакетов
        dependency_names = []
        for dep in dependencies:
            # Исключаем зависимости от самого себя (иногда встречается)
            if dep.get('crate_id') != package_name:
                dependency_names.append(dep['crate_id'])
        
        print(f"Найдено зависимостей: {len(dependency_names)}")
        return dependency_names
    
    def display_dependencies(self, package_name: str):
        """
        Выводит прямые зависимости на экран (требование этапа 2)
        
        Args:
            package_name: имя пакета для анализа
        """
        try:
            dependencies = self.get_direct_dependencies(package_name)
            
            print(f"\nПРЯМЫЕ ЗАВИСИМОСТИ ПАКЕТА '{package_name}':")
            print("=" * 50)
            
            if not dependencies:
                print("Зависимости не найдены")
            else:
                for i, dep in enumerate(dependencies, 1):
                    print(f"{i:2d}. {dep}")
            
            print("=" * 50)
            
        except Exception as e:
            print(f"Ошибка при получении зависимостей: {e}")
            return []


class TestDataFetcher:
    """
    Класс для тестовых данных (режим тестирования)
    """
    
    @staticmethod
    def get_test_dependencies(package_name: str) -> List[str]:
        """
        Возвращает тестовые зависимости для демонстрации
        
        Args:
            package_name: имя пакета (игнорируется в тестовом режиме)
            
        Returns:
            Список тестовых зависимостей
        """
        # Тестовые данные для демонстрации
        test_dependencies = {
            'A': ['B', 'C', 'D'],
            'B': ['D', 'E'],
            'C': ['B', 'F'],
            'serde': ['serde_derive', 'proc-macro2', 'quote', 'syn'],
            'tokio': ['bytes', 'mio', 'num_cpus', 'pin-project-lite']
        }
        
        # Возвращаем зависимости для указанного пакета или стандартный набор
        return test_dependencies.get(package_name, ['test_dep1', 'test_dep2', 'test_dep3'])
    
    @staticmethod
    def display_test_dependencies(package_name: str):
        """
        Выводит тестовые зависимости на экран
        """
        dependencies = TestDataFetcher.get_test_dependencies(package_name)
        
        print(f"\nТЕСТОВЫЕ ЗАВИСИМОСТИ ПАКЕТА '{package_name}':")
        print("=" * 50)
        
        for i, dep in enumerate(dependencies, 1):
            print(f"{i:2d}. {dep}")
        
        print("=" * 50)
        print("Режим ТЕСТИРОВАНИЯ - используются локальные данные")