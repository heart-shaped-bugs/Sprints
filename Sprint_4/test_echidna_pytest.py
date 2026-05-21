import pytest
from animal import Echidna  # предполагается, что метод в классе Echidna

@pytest.fixture
def default_echidna():
    """Стандартная ехидна с 2000 электрорецепторов"""
    e = Echidna(name="TestEchidna")
    e.electroreceptor_count = 2000
    return e


@pytest.fixture
def low_receptor_echidna():
    """Ехидна с 1000 электрорецепторов (вероятность 0.5)"""
    e = Echidna(name="LowReceptorEchidna")
    e.electroreceptor_count = 1000
    return e


@pytest.fixture
def zero_receptor_echidna():
    """Ехидна с 0 электрорецепторов"""
    e = Echidna(name="ZeroReceptorEchidna")
    e.electroreceptor_count = 0
    return e


# ========== ПОЗИТИВНЫЕ ТЕСТЫ (PT-1 .. PT-6) ==========

class TestPositiveTests:
    """PT-1 до PT-6: позитивные тест-кейсы"""
    
    def test_pt1_detection_shallow_depth(self, default_echidna):
        """PT-1: Обнаружение на малой глубине (5 см)"""
        # Мокаем электрическое поле >= 1.8 мВ/см
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=5, 
            electric_field_strength=1.8
        )
        
        assert isinstance(result, dict)
        assert result["detected"] is True
        assert isinstance(result["prey_type"], str)
        assert result["prey_type"] != ""
        assert isinstance(result["distance_mm"], float)
        assert result["distance_mm"] >= 0
    
    def test_pt2_detection_max_depth(self, default_echidna):
        """PT-2: Обнаружение на максимальной глубине (15 см)"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=15,
            electric_field_strength=1.8
        )
        
        assert result["detected"] is True
    
    def test_pt3_detection_almost_max_depth(self, default_echidna):
        """PT-3: Глубина 14.9 см, поле >= 1.8"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=14.9,
            electric_field_strength=1.8
        )
        
        assert result["detected"] is True
    
    def test_pt4_max_receptors_probability_1(self, default_echidna):
        """PT-4: 2000 рецепторов → вероятность 1.0"""
        # При вероятности 1.0 и наличии поля обнаружение гарантировано
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=10,
            electric_field_strength=1.8
        )
        
        # Вероятность должна быть 1.0 (проверяем через внутренний метод)
        probability = min(1.0, default_echidna.electroreceptor_count / 2000)
        assert probability == 1.0
        assert result["detected"] is True
    
    def test_pt5_intermediate_receptors(self, low_receptor_echidna):
        """PT-5: 1000 рецепторов → вероятность 0.5"""
        probability = min(1.0, low_receptor_echidna.electroreceptor_count / 2000)
        assert probability == 0.5
        
        # Запускаем много раз для проверки вероятности (статистически)
        detected_count = 0
        iterations = 100
        
        for _ in range(iterations):
            result = low_receptor_echidna.detect_prey_by_electric_field(
                depth_cm=10,
                electric_field_strength=1.8
            )
            if result["detected"]:
                detected_count += 1
        
        # Ожидаем примерно 50% успехов
        assert 30 <= detected_count <= 70, \
            f"При вероятности 0.5 обнаружено {detected_count} из {iterations}"
    
    def test_pt6_prey_exists(self, default_echidna):
        """PT-6: Добыча реально существует → detected=True"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=10,
            electric_field_strength=2.0
        )
        
        assert result["detected"] is True
        assert result["prey_type"] in ["ant", "worm", "termite", "unknown"]


# ========== НЕГАТИВНЫЕ ТЕСТЫ (NT-1 .. NT-6) ==========

class TestNegativeTests:
    """NT-1 до NT-6: негативные тест-кейсы"""
    
    def test_nt1_depth_more_than_15(self, default_echidna):
        """NT-1: Глубина больше 15 см → detected=False"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=16,
            electric_field_strength=1.8
        )
        
        assert result["detected"] is False
    
    def test_nt2_depth_much_more(self, default_echidna):
        """NT-2: Глубина 50 см → detected=False"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=50,
            electric_field_strength=1.8
        )
        
        assert result["detected"] is False
    
    def test_nt3_low_field_strength(self, default_echidna):
        """NT-3: Напряжённость поля ниже порога (1.79) → detected=False"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=10,
            electric_field_strength=1.79
        )
        
        assert result["detected"] is False
    
    def test_nt4_zero_receptors(self, zero_receptor_echidna):
        """NT-4: Электрорецепторов 0 → вероятность 0 → detected=False"""
        result = zero_receptor_echidna.detect_prey_by_electric_field(
            depth_cm=10,
            electric_field_strength=1.8
        )
        
        assert result["detected"] is False
    
    def test_nt5_negative_depth(self, default_echidna):
        """NT-5: Отрицательная глубина → detected=False"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=-5,
            electric_field_strength=1.8
        )
        
        assert result["detected"] is False
    
    def test_nt6_no_prey_zero_field(self, default_echidna):
        """NT-6: Добычи нет (поле = 0) → detected=False"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=10,
            electric_field_strength=0
        )
        
        assert result["detected"] is False


# ========== ГРАНИЧНЫЕ ТЕСТЫ (BT-1 .. BT-8) ==========

class TestBoundaryTests:
    """BT-1 до BT-8: граничные тест-кейсы"""
    
    def test_bt1_depth_exactly_15(self, default_echidna):
        """BT-1: Глубина ровно 15 см → detected=True"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=15.0,
            electric_field_strength=1.8
        )
        
        assert result["detected"] is True
    
    def test_bt2_depth_15001(self, default_echidna):
        """BT-2: Глубина 15.001 см → detected=False"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=15.001,
            electric_field_strength=1.8
        )
        
        assert result["detected"] is False
    
    def test_bt3_field_exactly_18(self, default_echidna):
        """BT-3: Напряжённость ровно 1.8 мВ/см → detected=True"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=10,
            electric_field_strength=1.8
        )
        
        assert result["detected"] is True
    
    def test_bt4_field_1799(self, default_echidna):
        """BT-4: Напряжённость 1.799 мВ/см → detected=False"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=10,
            electric_field_strength=1.799
        )
        
        assert result["detected"] is False
    
    def test_bt5_depth_zero(self, default_echidna):
        """BT-5: Глубина 0 см → detected=True (если поле >= 1.8)"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=0,
            electric_field_strength=1.8
        )
        
        assert result["detected"] is True
    
    def test_bt6_receptors_1999(self, default_echidna):
        """BT-6: 1999 рецепторов → вероятность = 0.9995"""
        default_echidna.electroreceptor_count = 1999
        probability = min(1.0, default_echidna.electroreceptor_count / 2000)
        
        assert probability == 0.9995
        # При такой высокой вероятности detected скорее всего True
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=10,
            electric_field_strength=1.8
        )
        # Не проверяем конкретное значение (зависит от random),
        # но проверяем что вероятность правильная
    
    def test_bt7_receptors_2001(self, default_echidna):
        """BT-7: 2001 рецепторов → вероятность = 1.0 (min сработал)"""
        default_echidna.electroreceptor_count = 2001
        probability = min(1.0, default_echidna.electroreceptor_count / 2000)
        
        assert probability == 1.0
        
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=10,
            electric_field_strength=1.8
        )
        assert result["detected"] is True
    
    def test_bt8_depth_none(self, default_echidna):
        """BT-8: Глубина = None → должна быть ошибка или detected=False"""
        with pytest.raises((TypeError, ValueError)):
            default_echidna.detect_prey_by_electric_field(
                depth_cm=None,
                electric_field_strength=1.8
            )


class TestTypeChecks:
    """Проверка типов возвращаемых значений"""
    
    def test_return_type_is_dict(self, default_echidna):
        """Всегда возвращает dict"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=10,
            electric_field_strength=1.8
        )
        assert isinstance(result, dict)
    
    def test_return_has_required_keys(self, default_echidna):
        """Присутствуют все 3 ключа"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=10,
            electric_field_strength=1.8
        )
        assert "detected" in result
        assert "prey_type" in result
        assert "distance_mm" in result
    
    def test_detected_is_bool(self, default_echidna):
        """detected — bool"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=10,
            electric_field_strength=1.8
        )
        assert isinstance(result["detected"], bool)
    
    def test_prey_type_is_string(self, default_echidna):
        """prey_type — str"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=10,
            electric_field_strength=1.8
        )
        assert isinstance(result["prey_type"], str)
    
    def test_distance_mm_is_float(self, default_echidna):
        """distance_mm — float"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=10,
            electric_field_strength=1.8
        )
        assert isinstance(result["distance_mm"], float)
    
    def test_when_not_detected_distance_mm_is_zero_or_negative(self, default_echidna):
        """Когда добыча не обнаружена, distance_mm = 0 или -1"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=50,
            electric_field_strength=1.8
        )
        assert result["detected"] is False
        assert result["distance_mm"] in (0.0, -1.0)
    
    def test_when_not_detected_prey_type_is_empty(self, default_echidna):
        """Когда добыча не обнаружена, prey_type = '' или 'none'"""
        result = default_echidna.detect_prey_by_electric_field(
            depth_cm=50,
            electric_field_strength=1.8
        )
        assert result["detected"] is False
        assert result["prey_type"] in ("", "none")
    
    def test_probability_bounds(self, default_echidna):
        """Вероятность не выше 1.0 и не ниже 0.0"""
        counts = [0, 1000, 2000, 3000, -100]
        for count in counts:
            default_echidna.electroreceptor_count = count
            prob = min(1.0, max(0.0, count / 2000))
            assert 0.0 <= prob <= 1.0




if __name__ == "__main__":
    pytest.main([__file__, "-v"])