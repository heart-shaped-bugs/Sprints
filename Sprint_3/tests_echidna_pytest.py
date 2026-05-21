import pytest
from animal import Echidna


class TestEchidnaReproduction:
    """Тест-план Спринт 3: Размножение ехидны"""

    @pytest.fixture
    def female_echidna(self):
        """Создание здоровой самки"""
        return Echidna(name="TestFemale", gender="female", age=3, weight=3.5)

    @pytest.fixture
    def male_echidna(self):
        """Создание самца"""
        return Echidna(name="TestMale", gender="male", age=3, weight=3.5)

    @pytest.fixture
    def pregnant_echidna(self):
        """Создание беременной самки"""
        e = Echidna(name="PregnantFemale", gender="female", age=3, weight=3.5)
        e.start_pregnancy()
        return e

    # ========== 1. Тестирование start_pregnancy() ==========

    def test_start_pregnancy_healthy_female(self, female_echidna):
        """№1: Позитив - Вызов start_pregnancy() у здоровой самки"""
        female_echidna.start_pregnancy()
        
        assert female_echidna.is_pregnant == True
        assert female_echidna.pregnancy_days == 0
        assert female_echidna.has_egg == False
        assert female_echidna.baby_in_pouch == False
        assert female_echidna.baby_in_hiding == False

    def test_start_pregnancy_already_pregnant(self, pregnant_echidna):
        """№2: Негатив - Вызов start_pregnancy() когда уже беременна"""
        with pytest.raises(ValueError, match="уже участвует в размножении"):
            pregnant_echidna.start_pregnancy()
        
        # Состояние не изменилось
        assert pregnant_echidna.is_pregnant == True
        assert pregnant_echidna.pregnancy_days == 0

    def test_start_pregnancy_male(self, male_echidna):
        """№3: Негатив - Вызов start_pregnancy() у самца"""
        with pytest.raises(ValueError, match="не может забеременеть"):
            male_echidna.start_pregnancy()
        
        assert male_echidna.is_pregnant == False

    def test_start_pregnancy_with_baby_in_pouch(self, female_echidna):
        """№4: Негатив - Вызов start_pregnancy() когда есть детёныш в сумке"""
        female_echidna.baby_in_pouch = True
        female_echidna.pouch_days = 10
        
        with pytest.raises(ValueError, match="уже участвует в размножении"):
            female_echidna.start_pregnancy()
        
        assert female_echidna.is_pregnant == False

    def test_start_pregnancy_after_previous_complete(self, female_echidna):
        """№5: Граница - Повторный вызов сразу после окончания предыдущей беременности"""
        # Первый цикл
        female_echidna.start_pregnancy()
        female_echidna.is_pregnant = False
        female_echidna.has_egg = False
        
        # Второй цикл должен работать
        female_echidna.start_pregnancy()
        assert female_echidna.is_pregnant == True
        assert female_echidna.pregnancy_days == 0

    # ========== 2. Тестирование simulate_day() - беременность и откладывание яйца ==========

    def test_pregnancy_day_20_no_egg(self, pregnant_echidna):
        """№6: 20 дней беременности - ещё нет яйца"""
        for _ in range(20):
            pregnant_echidna.simulate_day()
        
        assert pregnant_echidna.has_egg == False
        assert pregnant_echidna.is_pregnant == True

    def test_pregnancy_day_21_egg_laid(self, pregnant_echidna):
        """№7: 21 день беременности - яйцо отложено (ранняя граница нормы)"""
        for _ in range(21):
            pregnant_echidna.simulate_day()
        
        assert pregnant_echidna.has_egg == True
        assert pregnant_echidna.is_pregnant == False
        assert pregnant_echidna.egg_incubation_days == 0

    def test_pregnancy_day_28_egg_laid(self, pregnant_echidna):
        """№8: 28 дней беременности - яйцо отложено (поздняя граница нормы)"""
        for _ in range(28):
            pregnant_echidna.simulate_day()
        
        assert pregnant_echidna.has_egg == True
        assert pregnant_echidna.is_pregnant == False

    def test_pregnancy_day_29_egg_laid_but_anomaly(self, pregnant_echidna):
        """№9: 29 дней беременности - аномалия (выход за пределы нормы)"""
        # По коду: длительность 21-28 дней рандомно, на 29 дне яйцо уже должно быть отложено
        # Но при рандоме 28 дней яйцо отложится на 28 дне
        for _ in range(30):
            pregnant_echidna.simulate_day()
        
        # Яйцо должно быть отложено (уже инкубируется)
        assert pregnant_echidna.has_egg == True or pregnant_echidna.baby_in_pouch == True
        assert pregnant_echidna.is_pregnant == False

    @pytest.mark.parametrize("days", [21, 28])
    def test_pregnancy_boundary_egg_laid(self, pregnant_echidna, days):
        """№10,11: Граница - ровно 21 и 28 дней - яйцо отложено"""
        for _ in range(days):
            pregnant_echidna.simulate_day()
        
        assert pregnant_echidna.has_egg == True
        assert pregnant_echidna.is_pregnant == False

    def test_pregnancy_20_days_23_hours(self, pregnant_echidna):
        """№12: 20 дней 23 часа - яйцо ещё не отложено"""
        # Симуляция 20 дней (так как simulate_day работает с днями, а не часами)
        for _ in range(20):
            pregnant_echidna.simulate_day()
        
        assert pregnant_echidna.has_egg == False
        assert pregnant_echidna.is_pregnant == True

    # ========== 3. Тестирование simulate_day() - инкубация яйца ==========

    def test_incubation_9_days_no_hatch(self, female_echidna):
        """№13: 9 дней инкубации - яйцо ещё не вылупилось"""
        female_echidna.start_pregnancy()
        # Доводим до откладывания яйца
        for _ in range(21):
            female_echidna.simulate_day()
        # Инкубируем 9 дней
        for _ in range(9):
            female_echidna.simulate_day()
        
        assert female_echidna.has_egg == True
        assert female_echidna.baby_in_pouch == False

    def test_incubation_10_days_hatch(self, female_echidna):
        """№14: 10 дней инкубации - вылупление"""
        female_echidna.start_pregnancy()
        for _ in range(21):
            female_echidna.simulate_day()
        for _ in range(10):
            female_echidna.simulate_day()
        
        assert female_echidna.has_egg == False
        assert female_echidna.baby_in_pouch == True
        assert female_echidna.pouch_days == 0
        # Проверка веса новорождённого
        assert 0.0004 <= female_echidna.baby_weight <= 0.0005

    def test_incubation_11_days(self, female_echidna):
        """№15: 11 дней инкубации - вылупление уже произошло"""
        female_echidna.start_pregnancy()
        for _ in range(21):
            female_echidna.simulate_day()
        for _ in range(11):
            female_echidna.simulate_day()
        
        assert female_echidna.has_egg == False
        assert female_echidna.baby_in_pouch == True

    def test_incubation_exactly_10_days(self, female_echidna):
        """№16: Граница - ровно 10 дней - вылупление"""
        female_echidna.start_pregnancy()
        for _ in range(21):
            female_echidna.simulate_day()
        for _ in range(10):
            female_echidna.simulate_day()
        
        assert female_echidna.baby_in_pouch == True
        assert female_echidna.has_egg == False

    def test_hatch_without_egg(self, female_echidna):
        """№17: Негатив - вылупление без яйца (не должно происходить)"""
        # Эту ситуацию нужно создать принудительно
        female_echidna.has_egg = False
        female_echidna.egg_incubation_days = 10
        
        female_echidna.simulate_day()
        
        # Нет яйца - вылупления не должно быть
        assert female_echidna.baby_in_pouch == False

    # ========== 4. Тестирование роста детёныша в сумке ==========

    def test_pouch_growth_day_1(self, female_echidna):
        """№18: 1 день в сумке - вес увеличился по формуле"""
        female_echidna.baby_in_pouch = True
        female_echidna.pouch_days = 0
        female_echidna.baby_weight = 0.00045
        female_echidna.weight = 3.5
        
        female_echidna.simulate_day()
        
        expected_weight = 0.00045 * (900 ** (1/60))
        assert abs(female_echidna.baby_weight - expected_weight) < 0.00001

    def test_pouch_growth_day_30(self, female_echidna):
        """№19: 30 дней в сумке - вес ~ начальный * 30"""
        female_echidna.baby_in_pouch = True
        female_echidna.pouch_days = 29
        female_echidna.baby_weight = 0.00045
        female_echidna.weight = 3.5
        
        for _ in range(30):
            female_echidna.simulate_day()
        
        expected_weight = 0.00045 * (900 ** (30/60))
        assert abs(female_echidna.baby_weight - expected_weight) < 0.001
        assert 0.013 <= female_echidna.baby_weight <= 0.014

    def test_pouch_growth_day_60(self, female_echidna):
        """№20: 60 дней в сумке - вес ~ начальный * 900"""
        female_echidna.baby_in_pouch = True
        female_echidna.pouch_days = 0
        female_echidna.baby_weight = 0.00045
        female_echidna.weight = 3.5
        
        for _ in range(60):
            female_echidna.simulate_day()
        
        expected_weight = 0.00045 * 900
        assert abs(female_echidna.baby_weight - expected_weight) < 0.001
        assert 0.4 <= female_echidna.baby_weight <= 0.41

    def test_pouch_growth_day_0(self, female_echidna):
        """№21: Граница - 0 дней в сумке - вес = начальный вес"""
        female_echidna.baby_in_pouch = True
        female_echidna.pouch_days = 0
        female_echidna.baby_weight = 0.00045
        
        female_echidna._update_pouch_baby_growth()
        
        assert female_echidna.baby_weight == 0.00045

    def test_pouch_growth_day_50_early_exit(self, female_echidna):
        """№22: 50 дней (ранний выход) - детёныш ещё в сумке"""
        female_echidna.baby_in_pouch = True
        female_echidna.pouch_days = 0
        female_echidna.baby_weight = 0.00045
        
        for _ in range(49):
            female_echidna.simulate_day()
        
        assert female_echidna.baby_in_pouch == True
        assert female_echidna.baby_weight > 0

    def test_pouch_growth_day_55_late_exit(self, female_echidna):
        """№23: 55 дней (поздний выход) - детёныш ещё в сумке"""
        female_echidna.baby_in_pouch = True
        female_echidna.pouch_days = 0
        female_echidna.baby_weight = 0.00045
        
        for _ in range(54):
            female_echidna.simulate_day()
        
        assert female_echidna.baby_in_pouch == True

    def test_pouch_exit_day_56(self, female_echidna):
        """№24: 56 дней - детёныш должен покинуть сумку"""
        female_echidna.baby_in_pouch = True
        female_echidna.pouch_days = 0
        female_echidna.baby_weight = 0.00045
        
        for _ in range(56):
            female_echidna.simulate_day()
        
        assert female_echidna.baby_in_pouch == False
        assert female_echidna.baby_in_hiding == True

    def test_no_growth_when_no_baby(self, female_echidna):
        """№25: Негатив - рост при baby_in_pouch = False"""
        female_echidna.baby_in_pouch = False
        female_echidna.baby_weight = 0.0
        
        female_echidna._update_pouch_baby_growth()
        
        assert female_echidna.baby_weight == 0.0

    # ========== 5. Тестирование выхода детёныша из сумки ==========

    def test_exit_pouch_day_50(self, female_echidna):
        """№26: 50 дней в сумке - детёныш покидает сумку"""
        female_echidna.baby_in_pouch = True
        female_echidna.pouch_days = 0
        
        # Симулируем 50 дней
        for _ in range(50):
            female_echidna.simulate_day()
        
        assert female_echidna.baby_in_pouch == False
        assert female_echidna.baby_in_hiding == True
        assert female_echidna.days_since_last_feed == 0

    def test_exit_pouch_day_55(self, female_echidna):
        """№27: 55 дней в сумке - детёныш покидает сумку"""
        female_echidna.baby_in_pouch = True
        female_echidna.pouch_days = 0
        
        for _ in range(55):
            female_echidna.simulate_day()
        
        assert female_echidna.baby_in_pouch == False
        assert female_echidna.baby_in_hiding == True

    def test_still_in_pouch_day_49(self, female_echidna):
        """№28: 49 дней - всё ещё в сумке"""
        female_echidna.baby_in_pouch = True
        female_echidna.pouch_days = 0
        
        for _ in range(49):
            female_echidna.simulate_day()
        
        assert female_echidna.baby_in_pouch == True

    @pytest.mark.parametrize("days", [50, 55])
    def test_exit_boundary(self, female_echidna, days):
        """№29,30: Граница - выход происходит в 50 и 55 дней"""
        female_echidna.baby_in_pouch = True
        female_echidna.pouch_days = 0
        
        for _ in range(days):
            female_echidna.simulate_day()
        
        assert female_echidna.baby_in_pouch == False
        assert female_echidna.baby_in_hiding == True

    def test_exit_without_baby(self, female_echidna):
        """№31: Негатив - выход без детёныша в сумке"""
        female_echidna.baby_in_pouch = False
        female_echidna.pouch_days = 50
        
        female_echidna.simulate_day()
        
        assert female_echidna.baby_in_hiding == False

    # ========== 6. Тестирование mother_feeds() ==========

    def test_mother_feeds_normal(self, female_echidna):
        """№32: Позитив - кормление при baby_in_hiding = True"""
        female_echidna.baby_in_hiding = True
        female_echidna.baby_weight = 0.4
        female_echidna.days_since_last_feed = 5
        
        female_echidna.mother_feeds()
        
        assert female_echidna.baby_weight == 0.48  # 0.4 * 1.2
        assert female_echidna.days_since_last_feed == 0

    def test_mother_feeds_twice(self, female_echidna):
        """№33: Повторное кормление через 5 дней"""
        female_echidna.baby_in_hiding = True
        female_echidna.baby_weight = 0.4
        
        female_echidna.mother_feeds()
        assert female_echidna.baby_weight == 0.48
        
        female_echidna.days_since_last_feed = 5
        female_echidna.mother_feeds()
        assert female_echidna.baby_weight == 0.576  # 0.48 * 1.2
        assert female_echidna.days_since_last_feed == 0

    def test_mother_feeds_no_baby(self, female_echidna):
        """№34: Негатив - кормление при отсутствии детёныша"""
        female_echidna.baby_in_hiding = False
        
        with pytest.raises(ValueError, match="нет детёныша в укрытии"):
            female_echidna.mother_feeds()

    def test_mother_feeds_baby_in_pouch(self, female_echidna):
        """№35: Негатив - кормление при baby_in_pouch = True"""
        female_echidna.baby_in_pouch = True
        female_echidna.baby_in_hiding = False
        
        with pytest.raises(ValueError, match="нет детёныша в укрытии"):
            female_echidna.mother_feeds()

    def test_mother_feeds_weight_400g(self, female_echidna):
        """№36: Кормление с весом детёныша 400 г"""
        female_echidna.baby_in_hiding = True
        female_echidna.baby_weight = 0.4  # 400 г
        
        female_echidna.mother_feeds()
        
        assert female_echidna.baby_weight == 0.48  # 480 г

    # ========== 7. Тестирование голодания детёныша в укрытии ==========

    def test_starvation_5_days(self, female_echidna):
        """№37: 5 дней без кормления - норма"""
        female_echidna.baby_in_hiding = True
        female_echidna.baby_weight = 0.4
        female_echidna.days_since_last_feed = 4
        
        for _ in range(5):
            female_echidna.simulate_day()
        
        assert female_echidna.baby_in_hiding == True
        assert female_echidna.baby_weight == 0.4  # Вес не изменился

    def test_starvation_10_days(self, female_echidna):
        """№38: 10 дней без кормления - норма"""
        female_echidna.baby_in_hiding = True
        female_echidna.baby_weight = 0.4
        female_echidna.days_since_last_feed = 0
        
        for _ in range(10):
            female_echidna.simulate_day()
        
        assert female_echidna.baby_in_hiding == True
        assert female_echidna.baby_weight == 0.4

    def test_starvation_11_days_penalty(self, female_echidna):
        """№39: 11 дней без кормления - штраф (потеря веса)"""
        female_echidna.baby_in_hiding = True
        female_echidna.baby_weight = 0.4
        female_echidna.days_since_last_feed = 0
        
        for _ in range(11):
            female_echidna.simulate_day()
        
        assert female_echidna.baby_in_hiding == True
        assert female_echidna.baby_weight == 0.4 * (0.95 ** 1)  # Один день штрафа

    def test_starvation_15_days_critical(self, female_echidna):
        """№40: 15 дней без кормления - критическое состояние"""
        female_echidna.baby_in_hiding = True
        female_echidna.baby_weight = 0.4
        female_echidna.days_since_last_feed = 0
        
        for _ in range(15):
            female_echidna.simulate_day()
        
        assert female_echidna.baby_in_hiding == True
        # Должно быть 5 дней штрафа (дни 11-15)
        expected_weight = 0.4 * (0.95 ** 5)
        assert abs(female_echidna.baby_weight - expected_weight) < 0.001

    def test_starvation_16_days_death(self, female_echidna):
        """№41: 16 дней без кормления - детёныш погибает"""
        female_echidna.baby_in_hiding = True
        female_echidna.baby_weight = 0.4
        female_echidna.days_since_last_feed = 0
        
        for _ in range(16):
            female_echidna.simulate_day()
        
        assert female_echidna.baby_in_hiding == False
        assert female_echidna.baby_weight == 0.0

    def test_starvation_no_baby(self, female_echidna):
        """№42: Негатив - голодание при отсутствии детёныша"""
        female_echidna.baby_in_hiding = False
        female_echidna.days_since_last_feed = 10
        
        female_echidna.simulate_day()
        
        # Ничего не должно измениться
        assert female_echidna.baby_in_hiding == False

    # ========== 8. Тестирование get_reproduction_status() ==========

    def test_get_status_pregnant(self, pregnant_echidna):
        """№43: Беременна"""
        pregnant_echidna.pregnancy_days = 10
        status = pregnant_echidna.get_reproduction_status()
        
        assert status["is_pregnant"] == True
        assert status["pregnancy_days"] == 10
        assert status["has_egg"] == False

    def test_get_status_has_egg(self, female_echidna):
        """№44: Есть яйцо"""
        female_echidna.has_egg = True
        female_echidna.egg_incubation_days = 5
        status = female_echidna.get_reproduction_status()
        
        assert status["has_egg"] == True
        assert status["egg_incubation_days"] == 5

    def test_get_status_baby_in_pouch(self, female_echidna):
        """№45: Детёныш в сумке"""
        female_echidna.baby_in_pouch = True
        female_echidna.pouch_days = 30
        female_echidna.baby_weight = 0.013
        status = female_echidna.get_reproduction_status()
        
        assert status["baby_in_pouch"] == True
        assert status["pouch_days"] == 30
        assert status["baby_weight_kg"] == 0.013

    def test_get_status_baby_in_hiding(self, female_echidna):
        """№46: Детёныш в укрытии"""
        female_echidna.baby_in_hiding = True
        female_echidna.days_since_last_feed = 3
        female_echidna.baby_weight = 0.4
        status = female_echidna.get_reproduction_status()
        
        assert status["baby_in_hiding"] == True
        assert status["days_since_last_feed"] == 3

    def test_get_status_no_reproduction(self, female_echidna):
        """№47: Нет размножения"""
        status = female_echidna.get_reproduction_status()
        
        assert status["is_pregnant"] == False
        assert status["pregnancy_days"] == 0
        assert status["has_egg"] == False
        assert status["egg_incubation_days"] == 0
        assert status["baby_in_pouch"] == False
        assert status["pouch_days"] == 0
        assert status["baby_in_hiding"] == False

    def test_get_status_before_init(self):
        """№48: Вызов до инициализации репродукции"""
        e = Echidna(gender="female")
        status = e.get_reproduction_status()
        
        assert isinstance(status, dict)
        assert "is_pregnant" in status

    # ========== 9. Сквозные сценарии (интеграционные) ==========

    def test_full_reproduction_cycle(self, female_echidna):
        """№49: Полный цикл размножения"""
        female_echidna.start_pregnancy()
        
        # Беременность (21-28 дней)
        pregnancy_complete = False
        days = 0
        while not pregnancy_complete and days < 30:
            female_echidna.simulate_day()
            days += 1
            if female_echidna.has_egg:
                pregnancy_complete = True
        
        assert female_echidna.has_egg == True
        assert female_echidna.is_pregnant == False
        
        # Инкубация (10 дней)
        for _ in range(10):
            female_echidna.simulate_day()
        
        assert female_echidna.baby_in_pouch == True
        assert female_echidna.has_egg == False
        
        # В сумке (50-55 дней)
        pouch_complete = False
        days_in_pouch = 0
        while not pouch_complete and days_in_pouch < 60:
            female_echidna.simulate_day()
            days_in_pouch += 1
            if female_echidna.baby_in_hiding:
                pouch_complete = True
        
        assert female_echidna.baby_in_hiding == True
        assert female_echidna.baby_in_pouch == False
        
        # Кормление и независимость
        female_echidna.mother_feeds()
        assert female_echidna.days_since_last_feed == 0
        
        # Проверка, что все переходы прошли корректно
        assert female_echidna.alive == True

    def test_two_cycles_sequential(self, female_echidna):
        """№50: Два цикла размножения подряд"""
        # Первый цикл
        female_echidna.start_pregnancy()
        
        # Быстро проходим первый цикл
        for _ in range(100):  # Достаточно для полного цикла
            female_echidna.simulate_day()
            if female_echidna.baby_in_hiding and female_echidna.independent_age_days > 150:
                break
        
        # Проверяем, что репродуктивные поля сброшены
        assert female_echidna.is_pregnant == False
        assert female_echidna.has_egg == False
        assert female_echidna.baby_in_pouch == False
        assert female_echidna.baby_in_hiding == False
        
        # Второй цикл
        female_echidna.start_pregnancy()
        assert female_echidna.is_pregnant == True

    def test_feeding_interval_correct(self, female_echidna):
        """№51: Кормление в укрытии с правильным интервалом (каждые 5-10 дней)"""
        female_echidna.baby_in_hiding = True
        female_echidna.baby_weight = 0.4
        
        # Кормим каждые 7 дней
        for interval in range(5):
            # Пропускаем 7 дней
            for _ in range(7):
                female_echidna.simulate_day()
            female_echidna.mother_feeds()
        
        assert female_echidna.baby_in_hiding == True
        assert female_echidna.baby_weight > 0.4  # Детёныш вырос

    def test_starvation_death_16_days(self, female_echidna):
        """№52: Пропуск кормления на 16 дней - детёныш погибает"""
        female_echidna.baby_in_hiding = True
        female_echidna.baby_weight = 0.4
        
        # Не кормим 16 дней
        for _ in range(16):
            female_echidna.simulate_day()
        
        assert female_echidna.baby_in_hiding == False
        assert female_echidna.baby_weight == 0.0

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])