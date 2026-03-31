package com.example.autotest.services;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.Mock;
import org.mockito.InjectMocks;
import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
public class CalculatorServiceTest {

    @InjectMocks
    private CalculatorService calculatorService;

    @Mock
    private Object dependency; // this is not used in the CalculatorService class

    @BeforeEach
    void setup() {
        // no need to initialize anything in this case
    }

    @Test
    @DisplayName("test add method with positive numbers")
    void testAddMethodWithPositiveNumbers() {
        int result = calculatorService.add(5, 7);
        assertEquals(12, result);
    }

    @Test
    @DisplayName("test add method with negative numbers")
    void testAddMethodWithNegativeNumbers() {
        int result = calculatorService.add(-5, -7);
        assertEquals(-12, result);
    }

    @Test
    @DisplayName("test add method with mixed numbers")
    void testAddMethodWithMixedNumbers() {
        int result = calculatorService.add(-5, 7);
        assertEquals(2, result);
    }

    @Test
    @DisplayName("test divide method with positive numbers")
    void testDivideMethodWithPositiveNumbers() {
        int result = calculatorService.divide(10, 2);
        assertEquals(5, result);
    }

    @Test
    @DisplayName("test divide method with negative numbers")
    void testDivideMethodWithNegativeNumbers() {
        int result = calculatorService.divide(-10, 2);
        assertEquals(-5, result);
    }

    @Test
    @DisplayName("test divide method with mixed numbers")
    void testDivideMethodWithMixedNumbers() {
        int result = calculatorService.divide(-10, -2);
        assertEquals(5, result);
    }

    @Test
    @DisplayName("test divide method with zero divisor")
    void testDivideMethodWithZeroDivisor() {
        assertThrows(RuntimeException.class, () -> calculatorService.divide(10, 0));
    }
}