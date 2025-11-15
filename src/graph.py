from typing import Dict, List, Set, Optional
from collections import deque


class DependencyGraph:
    """
    Класс для представления и анализа графа зависимостей пакетов
    """
    
    def __init__(self):
        self.graph: Dict[str, List[str]] = {}  # граф зависимостей
        self.visited: Set[str] = set()         # посещенные узлы
        self.recursion_stack: Set[str] = set() # стек для обнаружения циклов
    
    def build_dependency_graph(self, fetcher, package_name: str, max_depth: int = -1, 
                              filter_substring: str = "") -> Dict[str, List[str]]:
        """
        Строит полный граф зависимостей с учетом транзитивности используя BFS с рекурсией
        
        Аргументы:
            fetcher: экземпляр CargoAPIFetcher или TestDataFetcher
            package_name: корневой пакет для анализа
            max_depth: максимальная глубина рекурсии (-1 = без ограничений)
            filter_substring: подстрока для фильтрации пакетов
            
        Возвращает:
            Словарь представляющий граф зависимостей
        """
        print(f" Построение графа зависимостей для '{package_name}'...")
        print(f"   Макс. глубина: {max_depth if max_depth != -1 else 'без ограничений'}")
        if filter_substring:
            print(f"   Фильтр: исключаются пакеты содержащие '{filter_substring}'")
        
        self.graph = {}
        self.visited.clear()
        
        # Запускаем BFS с рекурсией
        self._bfs_with_recursion(fetcher, package_name, max_depth, filter_substring, current_depth=0)
        
        print(f" Граф построен: {len(self.graph)} пакетов, {sum(len(deps) for deps in self.graph.values())} зависимостей")
        return self.graph
    
    def _bfs_with_recursion(self, fetcher, package: str, max_depth: int, 
                           filter_substring: str, current_depth: int):
        """
        BFS с рекурсией для построения графа зависимостей
        
        Аргументы:
            fetcher: экземпляр фетчера
            package: текущий пакет для анализа
            max_depth: максимальная глубина
            filter_substring: подстрока для фильтрации
            current_depth: текущая глубина рекурсии
        """
        # Проверяем ограничение глубины
        if max_depth != -1 and current_depth > max_depth:
            return
        
        # Проверяем циклы
        if package in self.recursion_stack:
            print(f"  Обнаружен цикл: {package}")
            return
        
        # Если пакет уже посещен на этом уровне, пропускаем
        if package in self.visited:
            return
        
        self.visited.add(package)
        self.recursion_stack.add(package)
        
        try:
            # Получаем зависимости текущего пакета
            if hasattr(fetcher, 'get_test_dependencies'):
                # Тестовый режим
                dependencies = fetcher.get_test_dependencies(package)
            else:
                # Продакшн режим
                dependencies = fetcher.get_direct_dependencies(package)
            
            # Фильтруем зависимости
            filtered_dependencies = []
            for dep in dependencies:
                if filter_substring and filter_substring in dep:
                    print(f"    Отфильтрован: {dep}")
                    continue
                filtered_dependencies.append(dep)
            
            # Добавляем в граф
            self.graph[package] = filtered_dependencies
            
            # Рекурсивно обрабатываем зависимости
            for dep in filtered_dependencies:
                self._bfs_with_recursion(fetcher, dep, max_depth, filter_substring, current_depth + 1)
                
        except Exception as e:
            print(f" Ошибка при обработке пакета {package}: {e}")
        finally:
            self.recursion_stack.remove(package)
    
    def detect_cycles(self) -> List[List[str]]:
        """
        Обнаруживает циклические зависимости в графе
        
        Возвращает:
            Список циклов (каждый цикл - список пакетов)
        """
        visited = set()
        recursion_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]):
            if node in recursion_stack:
                # найден цикл
                cycle_start = path.index(node)
                cycle = path[cycle_start:]
                if cycle not in cycles:
                    cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            recursion_stack.add(node)
            path.append(node)
            
            for neighbor in self.graph.get(node, []):
                dfs(neighbor, path.copy())
            
            recursion_stack.remove(node)
            path.pop()
        
        for node in self.graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def get_dependency_count(self) -> Dict[str, int]:
        """
        Возвращает статистику по зависимостям
        
        Возвращает:
            Словарь с количеством зависимостей для каждого пакета
        """
        return {package: len(dependencies) for package, dependencies in self.graph.items()}
    
    def display_graph(self):
        """
        Выводит граф зависимостей в читаемом формате
        """
        if not self.graph:
            print(" Граф пуст")
            return
        
        print(f"\n ГРАФ ЗАВИСИМОСТЕЙ ({len(self.graph)} пакетов):")
        print("=" * 60)
        
        for package, dependencies in self.graph.items():
            if dependencies:
                deps_str = ", ".join(dependencies)
                print(f" {package}")
                print(f"   └── зависит от: {deps_str}")
            else:
                print(f" {package} (нет зависимостей)")
        
        print("=" * 60)
        
        # показываем циклы если есть
        cycles = self.detect_cycles()
        if cycles:
            print(f" Обнаружено циклов: {len(cycles)}")
            for i, cycle in enumerate(cycles, 1):
                print(f"   Цикл {i}: {' → '.join(cycle)} → ...")


class TestGraphBuilder:
    """
    Класс для тестирования на простых данных
    """
    
    @staticmethod
    def build_test_graph() -> Dict[str, List[str]]:
        """
        Строит тестовый граф для демонстрации
        
        Returns:
            Тестовый граф зависимостей
        """
        # Тестовый граф с циклами и сложными зависимостями
        test_graph = {
            'A': ['B', 'C'],
            'B': ['D', 'E'],
            'C': ['B', 'F'],
            'D': ['G'],
            'E': ['D', 'H'],
            'F': ['E', 'I'],
            'G': ['B'],  # цикл: B -> D -> G -> B
            'H': [],     # конечный узел
            'I': ['F']   # цикл: F -> I -> F
        }
        return test_graph
    
    @staticmethod
    def display_test_graph():
        """
        Выводит тестовый граф
        """
        graph = TestGraphBuilder.build_test_graph()
        dependency_graph = DependencyGraph()
        dependency_graph.graph = graph
        
        print(" ТЕСТОВЫЙ ГРАФ:")
        dependency_graph.display_graph()
        
        # анализ циклов
        cycles = dependency_graph.detect_cycles()
        if cycles:
            print(f"\n ОБНАРУЖЕНЫ ЦИКЛЫ:")
            for i, cycle in enumerate(cycles, 1):
                print(f"   Цикл {i}: {' → '.join(cycle)}")