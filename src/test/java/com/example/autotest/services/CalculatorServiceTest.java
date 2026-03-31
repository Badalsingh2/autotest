package com.example.autotest.services;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

@ExtendWith(MockitoExtension.class)
public class CalculatorServiceTest {

    @InjectMocks
    private CalculatorService calculatorService;

    @Test
    @DisplayName("test add method with positive numbers")
    public void testAddMethodWithPositiveNumbers() {
        int result = calculatorService.add(5, 7);
        assertEquals(12, result);
    }

    @Test
    @DisplayName("test add method with negative numbers")
    public void testAddMethodWithNegativeNumbers() {
        int result = calculatorService.add(-5, -7);
        assertEquals(-12, result);
    }

    @Test
    @DisplayName("test add method with mixed numbers")
    public void testAddMethodWithMixedNumbers() {
        int result = calculatorService.add(-5, 7);
        assertEquals(2, result);
    }

    @Test
    @DisplayName("test divide method with positive numbers")
    public void testDivideMethodWithPositiveNumbers() {
        int result = calculatorService.divide(10, 2);
        assertEquals(5, result);
    }

    @Test
    @DisplayName("test divide method with negative numbers")
    public void testDivideMethodWithNegativeNumbers() {
        int result = calculatorService.divide(-10, -2);
        assertEquals(5, result);
    }

    @Test
    @DisplayName("test divide method with mixed numbers")
    public void testDivideMethodWithMixedNumbers() {
        int result = calculatorService.divide(-10, 2);
        assertEquals(-5, result);
    }

    @Test
    @DisplayName("test divide method by zero")
    public void testDivideMethodByZero() {
        RuntimeException exception = assertThrows(RuntimeException.class, () -> calculatorService.divide(10, 0));
        assertEquals("Cannot divide by zero", exception.getMessage());
    }
}